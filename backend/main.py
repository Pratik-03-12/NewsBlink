from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from preprocessing import extract_youtube_transcript, summarize_text, clean_text
from clustering import classify_new_summary, load_agnes_model, evaluate_clustering
from utils import get_category_name
import logging

app = FastAPI()

# Load AGNES model at startup
agnes_model = load_agnes_model()
if not agnes_model:
    logging.warning("AGNES model not found. Please train it before classification!")

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "Welcome to the NewsBlink API"}

@app.post("/process_video")
def process_video(request: VideoRequest):
    try:
        transcript = extract_youtube_transcript(request.url)
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcript extraction failed.")
        
        summary = summarize_text(transcript)
        cleaned_summary = clean_text(summary)

        if not agnes_model:
            raise HTTPException(status_code=500, detail="AGNES model is not trained. Please train it first!")

        predicted_cluster = classify_new_summary(cleaned_summary)
        category = get_category_name(predicted_cluster)

        # Compute clustering quality metrics
        # silhouette, davies_bouldin = evaluate_clustering(agnes_model)

        return {
            "summary": summary,
            "category": category,
        #     "silhouette_score": silhouette,
        #     "davies_bouldin_index": davies_bouldin
        }

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
