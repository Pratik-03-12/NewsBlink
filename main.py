from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .preprocessing import extract_youtube_transcript, summarize_text, clean_text
from .clustering import classify_new_summary, load_agnes_model, compute_confidence_score #, evaluate_clustering
from .utils import get_category_name
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import pickle
import pandas as pd
from gtts import gTTS
import uuid
from .retrain_utils import retrain_model, DATASET_LOCK, DATASET_PATH

# Added for using modified preprocessing
from . import modified_preprocessing

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()

# Mount static folder for serving audio
app.mount("/static", StaticFiles(directory="static"), name="audio")

# Ensure audio folder exists
AUDIO_DIR = os.path.join("static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for security in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


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
        # Modified here — use functions from modified_preprocessing
        transcript = modified_preprocessing.extract_youtube_transcript(request.url)
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
        
        # Modified here — use improved summarizer
        summary = modified_preprocessing.summarize_text(transcript)
        print(f"=== SUMMARY GENERATED: {summary} ===")
        logging.info(f"Summary generated: {summary}")
        # Modified here — use improved clean_text
        cleaned_summary = modified_preprocessing.clean_text(summary)
         # Extract the summary text
        summary = cleaned_summary

        # Always use the same file name
        file_name = "summary.mp3"
        file_path = os.path.join(AUDIO_DIR, file_name)

        # Convert text to speech
        tts = gTTS(text=summary, lang='en')
        tts.save(file_path)
        
        #Return URL to frontend
        audio_url = f"/static/audio/{file_name}"

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
                
                # Check confidence threshold
