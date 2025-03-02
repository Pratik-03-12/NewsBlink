### main.py

from preprocessing import extract_youtube_transcript, summarize_text, clean_text
from clustering import classify_new_summary, evaluate_clustering
from utils import get_category_name

def process_video(youtube_url):
    """Full pipeline for processing a YouTube video link."""
    transcript = extract_youtube_transcript(youtube_url)
    if 'error' in transcript:
        return {"error": transcript}
    
    summary = summarize_text(transcript)
    cleaned_summary = clean_text(summary)
    predicted_cluster = classify_new_summary(cleaned_summary)
    category = get_category_name(predicted_cluster)
    
    return {"summary": summary, "category": category}

if __name__ == "__main__":
    video_url = "YOUR_YOUTUBE_VIDEO_LINK"
    result = process_video(video_url)
    print(result)
