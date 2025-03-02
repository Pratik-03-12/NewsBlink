### processing.py

from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

# Summarization Pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_video_id(youtube_url):
    """Extracts the video ID from a full YouTube URL."""
    match = re.search(r"(?:v=|/)([\w-]{11})", youtube_url)
    return match.group(1) if match else None

def extract_youtube_transcript(video_url):
    """Extracts transcript from YouTube video ID."""
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except Exception as e:
        return str(e)

def summarize_text(text, max_length=130):
    """Summarizes extracted text."""
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def clean_text(text):
    """Preprocess text by removing special characters and converting to lowercase."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().strip()
