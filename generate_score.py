import re
import numpy as np
import nltk
import pickle
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Download necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('punkt')


# Load stopwords and lemmatizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Function to normalize text
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters & numbers
    text = text.strip()
    return text

# Function to remove stopwords
def remove_stopwords(tokens):
    return [word for word in tokens if word not in stop_words]

# Function to lemmatize tokens
def lemmatize_tokens(tokens):
    return [lemmatizer.lemmatize(word) for word in tokens]

# Load sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load dataset
df = pd.read_excel('backend/datasets/Research_project_Dataset_1.xlsx')

# Preprocessing

df['Cleaned_text_step1'] = df['Summary'].apply(normalize_text)
df['Filtered_text_step2'] = df['Cleaned_text_step1'].apply(lambda text: remove_stopwords(word_tokenize(text)))
df['lemmatized_text_step3'] = df['Filtered_text_step2'].apply(lemmatize_tokens)

# Convert tokens back to text for embedding
df['Processed_Text'] = df['lemmatized_text_step3'].apply(lambda tokens: " ".join(tokens))

# Generate embeddings
embeddings = model.encode(df['Processed_Text'].tolist(), show_progress_bar=True)
clustering_model = AgglomerativeClustering(n_clusters=8, metric='cosine', linkage='average')
cluster_labels = clustering_model.fit_predict(embeddings)
# Save embeddings to a pickle file
model_data = {
        "embeddings": embeddings,  # Store embeddings for evaluation
        "labels": cluster_labels.tolist()
}
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(model_data, f)
    
def evaluate_clustering(agnes_model):
    """Compute clustering evaluation metrics using stored embeddings & labels."""
    if "labels" not in agnes_model or "embeddings" not in agnes_model:
        raise ValueError("AGNES model is missing necessary data.")

    embeddings = np.array(agnes_model["embeddings"])  # Use stored embeddings, not centroids
    labels = np.array(agnes_model["labels"])

    silhouette = silhouette_score(embeddings, labels)
    davies_bouldin = davies_bouldin_score(embeddings, labels)

    return silhouette, davies_bouldin

# print(f"Embeddings shape: {embeddings.shape}")