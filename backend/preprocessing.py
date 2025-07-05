"""Preprocessing utilities for NewsBlink backend."""

from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data (safe to call multiple times)
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Summarization Pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Load stopwords and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def extract_video_id(youtube_url):
    """Extracts the video ID from a full YouTube URL."""
    # Handle various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def extract_youtube_transcript(video_url):
    """Extracts transcript from YouTube video ID."""
    print(f"=== DEBUG: Processing URL: {video_url} ===")
    video_id = extract_video_id(video_url)
    print(f"=== DEBUG: Extracted video ID: {video_id} ===")
    
    if not video_id:
        return "Invalid YouTube URL - could not extract video ID"
    
    try:
        # Try the basic method first
        print("=== DEBUG: Trying basic transcript method ===")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        if not transcript:
            return "No transcript available for this video"
        
        full_text = " ".join([entry['text'] for entry in transcript])
        if not full_text.strip():
            return "Transcript is empty"
        
        print(f"=== DEBUG: Successfully extracted transcript of length: {len(full_text)} ===")
        return full_text
        
    except Exception as e:
        error_msg = str(e)
        print(f"=== DEBUG: Basic transcript extraction error: {error_msg} ===")
        
        # Try alternative method with transcript list
        try:
            print("=== DEBUG: Trying transcript list method ===")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Get the first available transcript
            for transcript_obj in transcript_list:
                try:
                    transcript = transcript_obj.fetch()
                    if transcript:
                        full_text = " ".join([entry['text'] for entry in transcript])
                        print(f"=== DEBUG: Successfully extracted transcript via list method, length: {len(full_text)} ===")
                        return full_text
                except Exception as inner_e:
                    print(f"=== DEBUG: Failed to fetch transcript: {inner_e} ===")
                    continue
            
            return "No transcript available for this video"
            
        except Exception as list_error:
            print(f"=== DEBUG: Transcript list method also failed: {list_error} ===")
        
        if "No transcript available" in error_msg:
            return "No transcript available for this video"
        elif "Video unavailable" in error_msg:
            return "Video is unavailable or private"
        elif "TranscriptsDisabled" in error_msg:
            return "Transcripts are disabled for this video"
        elif "no element found" in error_msg.lower():
            return "Transcript extraction failed - video may not have captions or may be restricted"
        else:
            return f"Transcript extraction failed: {error_msg}"

def summarize_text(text, max_length=130):
    """Summarizes extracted text."""
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def clean_text(text):
    """Preprocess text by removing special characters and converting to lowercase."""
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().strip()

def normalize_text(text):
    """Lowercase, remove URLs, HTML tags, special characters, and extra spaces."""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.strip()
    return text

def remove_stopwords(tokens):
    """Remove English stopwords from token list."""
    return [word for word in tokens if word not in stop_words]

def lemmatize_tokens(tokens):
    """Lemmatize a list of tokens."""
    return [lemmatizer.lemmatize(word) for word in tokens]

def preprocess_for_clustering(text):
    """Full pipeline: normalize, tokenize, remove stopwords, lemmatize, join back to string."""
    norm = normalize_text(text)
    tokens = word_tokenize(norm)
    filtered = remove_stopwords(tokens)
    lemmatized = lemmatize_tokens(filtered)
    return " ".join(lemmatized)
