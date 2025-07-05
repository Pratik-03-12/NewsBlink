from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from .preprocessing import extract_youtube_transcript, summarize_text, clean_text
from .clustering import classify_new_summary, load_agnes_model, compute_confidence_score #, evaluate_clustering
from .utils import get_category_name
import logging
import os
import pickle
import pandas as pd
from .retrain_utils import retrain_model, DATASET_LOCK, DATASET_PATH

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()

# Load AGNES model at startup
agnes_model = load_agnes_model()
if not agnes_model:
    logging.warning("AGNES model not found. Please train it before classification!")

embeddings_model = "backend/models/embeddings.pkl"
if os.path.exists(embeddings_model):
        with open(embeddings_model, "rb") as f:
            embed_model = pickle.load(f)
class VideoRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "Welcome to the NewsBlink API"}

@app.post("/process_video")
def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    try:
        transcript = extract_youtube_transcript(request.url)
        print(f"=== TRANSCRIPT EXTRACTED: {transcript[:100]}... ===")
        logging.info(f"Transcript extracted: {transcript[:100]}...")
        
        # Check if transcript extraction failed
        if not transcript or len(transcript) < 50:
            print("=== TRANSCRIPT EXTRACTION FAILED ===")
            raise HTTPException(status_code=400, detail="Transcript extraction failed or transcript too short.")
        
        # Check if transcript contains error messages
        error_indicators = ["error", "failed", "max retries", "ssl", "connection", "timeout"]
        if any(indicator in transcript.lower() for indicator in error_indicators):
            print("=== TRANSCRIPT CONTAINS ERROR MESSAGES ===")
            raise HTTPException(status_code=400, detail="Transcript extraction failed due to network or access issues.")
        
        summary = summarize_text(transcript)
        print(f"=== SUMMARY GENERATED: {summary} ===")
        logging.info(f"Summary generated: {summary}")
        cleaned_summary = clean_text(summary)

        if not agnes_model:
            raise HTTPException(status_code=500, detail="AGNES model is not trained. Please train it first!")

        predicted_cluster = classify_new_summary(cleaned_summary)
        category = get_category_name(predicted_cluster)
        
        # Log cluster information for debugging
        logging.info(f"Cluster ID: {predicted_cluster}, Category: {category}")
        
        # Compute confidence score
        confidence_score = compute_confidence_score(cleaned_summary, predicted_cluster)
        
        # Add confidence label for better user interpretation
        if confidence_score >= 80:
            confidence_label = "Very High"
        elif confidence_score >= 60:
            confidence_label = "High"
        elif confidence_score >= 40:
            confidence_label = "Moderate"
        elif confidence_score >= 20:
            confidence_label = "Low"
        else:
            confidence_label = "Very Low"
            
        # Add explanation for user understanding
        if confidence_score >= 80:
            confidence_explanation = f"This score indicates how similar the content is to typical {category} news. Very high confidence means the content is very similar to typical {category} content."
        elif confidence_score >= 60:
            confidence_explanation = f"This score indicates how similar the content is to typical {category} news. High confidence means the content is quite similar to typical {category} content."
        elif confidence_score >= 40:
            confidence_explanation = f"This score indicates how similar the content is to typical {category} news. Moderate confidence means the content has reasonable similarity to typical {category} content."
        elif confidence_score >= 20:
            confidence_explanation = f"This score indicates how similar the content is to typical {category} news. Low confidence means the content is somewhat different from typical {category} content, but still classified in this category."
        else:
            confidence_explanation = f"This score indicates how similar the content is to typical {category} news. Very low confidence means the content is quite different from typical {category} content, but was still classified in this category."

        # Define confidence threshold for retraining (skip if below this threshold)
        CONFIDENCE_THRESHOLD = 20.0  # Skip retraining if confidence < 20%
        
        # Determine if we should retrain based on confidence
        should_retrain = confidence_score >= CONFIDENCE_THRESHOLD

        def append_and_retrain():
            try:
                print("=== [BG] BACKGROUND TASK STARTED ===")
                logging.info("[BG] Background task started: append and retrain.")
                
                # Check confidence threshold before proceeding
                if not should_retrain:
                    print(f"=== [BG] SKIPPING RETRAINING: Confidence {confidence_score}% is below threshold {CONFIDENCE_THRESHOLD}% ===")
                    logging.info(f"[BG] Skipping retraining: Confidence {confidence_score}% is below threshold {CONFIDENCE_THRESHOLD}%")
                    return
                
                with DATASET_LOCK:
                    df = pd.read_excel(DATASET_PATH)
                    # Check for expected columns
                    expected_col = 'NEWS (Full Transcript)'
                    if expected_col not in df.columns:
                        print(f"=== [BG] COLUMN NOT FOUND: {expected_col} ===")
                        logging.warning(f"[BG] Expected column '{expected_col}' not found in dataset. Columns: {df.columns.tolist()}")
                        return
                    # Prevent duplication: check if transcript already exists
                    if (df[expected_col] == transcript).any():
                        print("=== [BG] DUPLICATE TRANSCRIPT DETECTED ===")
                        logging.info("[BG] Duplicate transcript detected. Skipping append.")
                    else:
                        new_row = {expected_col: transcript, "Summary": summary, "Category": category}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        df.to_excel(DATASET_PATH, index=False)
                        print("=== [BG] NEW ROW APPENDED TO DATASET ===")
                        logging.info("[BG] New row appended to dataset.")
                print("=== [BG] STARTING MODEL RETRAINING ===")
                logging.info("[BG] Starting model retraining...")
                retrain_model()
                print("=== [BG] MODEL RETRAINING COMPLETED ===")
                logging.info("[BG] Model retraining completed.")
            except Exception as e:
                print(f"=== [BG] ERROR: {e} ===")
                logging.error(f"[BG] Error in background append/retrain: {e}")

        background_tasks.add_task(append_and_retrain)

        logging.info(f"Processed video for URL: {request.url} | Category: {category} | Confidence: {confidence_score}% | Retraining: {'scheduled' if should_retrain else 'skipped'}")
        return {
            "summary": summary,
            "category": category,
            "confidence_score": f"{confidence_score}%",
            "confidence_label": confidence_label,
            "confidence_explanation": confidence_explanation,
            "retraining_status": "skipped" if not should_retrain else "scheduled",
            "retraining_note": f"Retraining {'skipped' if not should_retrain else 'scheduled'} due to {'low confidence' if not should_retrain else 'sufficient confidence'} ({confidence_score}% vs {CONFIDENCE_THRESHOLD}% threshold)"
        }

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
