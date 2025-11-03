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

def chunk_text(text: str, max_length: int = 600):
    """Split text into chunks while preserving sentence boundaries."""
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks
    except Exception as e:
        print(f"=== DEBUG: Error chunking text: {str(e)} ===")
        return [text]


def postprocess_summary(summary: str) -> str:
    """Clean up the generated summary."""
    summary = re.sub(r'\s+', ' ', summary)
    summary = re.sub(r'\s+([.,!?])', r'\1', summary)
    summary = re.sub(r'([.,!?])\s*([A-Z])', r'\1 \2', summary)
    return summary.strip()


def summarize_text(text, max_length=150, min_length=30):
    """Summarizes extracted text using multi-chunk approach."""
    try:
        if not summarizer:
            raise RuntimeError("Summarizer model not loaded")

        # Split text into manageable chunks
        chunks = chunk_text(text)
        summaries = []
        tokenizer = getattr(summarizer, "tokenizer", None)

        for i, chunk in enumerate(chunks):
            if len(chunk.split()) > 30:
                print(f"=== DEBUG: Summarizing chunk {i+1}/{len(chunks)} ===")
                try:
                    # Adapt generation lengths to the chunk token length
                    token_count = None
                    if tokenizer is not None:
                        tokenized = tokenizer(chunk, truncation=True)
                        ids = tokenized.get("input_ids", [])
                        if ids:
                            # Handle both list[int] and list[list[int]]
                            token_count = len(ids[0]) if isinstance(ids[0], list) else len(ids)

                    # Choose conservative defaults if token_count unavailable
                    if token_count is None:
                        token_count = max(64, len(chunk.split()))

                    adaptive_max_new = min(120, max(60, token_count // 2))
                    adaptive_min = max(10, min(min_length, max(10, token_count // 3)))
                    # Ensure min does not exceed max_new_tokens - 5
                    adaptive_min = min(adaptive_min, max(10, adaptive_max_new - 5))

                    summary = summarizer(
                        chunk,
                        max_new_tokens=adaptive_max_new,
                        min_length=adaptive_min,
                        do_sample=False,
                        truncation=True
                    )
                    chunk_summary = postprocess_summary(summary[0]['summary_text'])
                    summaries.append(chunk_summary)
                except Exception as e:
                    print(f"=== DEBUG: Error summarizing chunk {i+1}: {str(e)} ===")
                    continue

        if not summaries:
            raise Exception("Failed to generate summary from any chunks")

        final_summary = " ".join(summaries)
        final_summary = postprocess_summary(final_summary)

        print("=== DEBUG: Summary generated successfully ===")
        return final_summary

    except Exception as e:
        print(f"=== DEBUG: Summarization error: {str(e)} ===")
        fallback_length = min(200, len(text))
        return text[:fallback_length] + "..." if len(text) > fallback_length else text

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