import numpy as np
import pickle
import os
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Load pre-trained BERT model
bert_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

MODEL_PATH = "backend/models/agnes_model.pkl"



def train_agnes_clustering(summaries, n_clusters=8):
    """Train AGNES clustering and save model with correct format."""
    embeddings = bert_model.encode(summaries, convert_to_numpy=True)

    clustering_model = AgglomerativeClustering(n_clusters=n_clusters, metric='cosine', linkage='average')
    cluster_labels = clustering_model.fit_predict(embeddings)

    # Compute centroids
    cluster_centroids = []
    for cluster in range(n_clusters):
        cluster_indices = np.where(cluster_labels == cluster)[0]  # Get indices of samples in this cluster
        if len(cluster_indices) > 0:
            cluster_centroids.append(np.mean(embeddings[cluster_indices], axis=0))
        else:
            cluster_centroids.append(np.zeros(embeddings.shape[1]))  # Handle empty clusters

    # Save embeddings, labels, and centroids
    model_data = {
        "embeddings": embeddings,  # Store embeddings for evaluation
        "labels": cluster_labels.tolist(),  # Store assigned cluster labels
        "centroids": np.array(cluster_centroids)
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)

    return model_data



def load_agnes_model():
    """Load AGNES model if available, else return None."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

# Load AGNES model at startup
agnes_model = load_agnes_model()



def classify_new_summary(summary):
    """Classify a new summary into the closest AGNES cluster."""
    if agnes_model is None:
        raise ValueError("AGNES model is not trained. Train it first!")

    summary_embedding = bert_model.encode([summary], convert_to_numpy=True)[0]
    
    centroids = np.array(agnes_model["centroids"])  # Use stored centroids
    similarities = cosine_similarity([summary_embedding], centroids)[0]
    
    predicted_cluster = np.argmax(similarities)
    return predicted_cluster


def evaluate_clustering(agnes_model):
    """Compute clustering evaluation metrics using stored embeddings & labels."""
    if "labels" not in agnes_model or "embeddings" not in agnes_model:
        raise ValueError("AGNES model is missing necessary data.")

    embeddings = np.array(agnes_model["embeddings"])  # Use stored embeddings, not centroids
    labels = np.array(agnes_model["labels"])

    silhouette = silhouette_score(embeddings, labels)
    davies_bouldin = davies_bouldin_score(embeddings, labels)

    return silhouette, davies_bouldin



