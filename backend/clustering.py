"""Clustering utilities for NewsBlink backend."""
import numpy as np
import pickle
import os
from sklearn.cluster import AgglomerativeClustering
# from sklearn.cluster import SpectralClustering
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score, davies_bouldin_score

# Load pre-trained BERT model
bert_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

MODEL_PATH = "backend/models/agnes_model.pkl"
# MODEL_PATH = "backend/models/spectral_model.pkl"


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

# def train_spectral_clustering(summaries, n_clusters=8):
#     """Train Spectral Clustering model and save it."""
#     embeddings = bert_model.encode(summaries, convert_to_numpy=True)

#     # Step 1: Precompute cosine similarity matrix
#     similarity_matrix = cosine_similarity(embeddings)  # shape: (n_samples, n_samples)

#     # Step 2: Apply Spectral Clustering
#     clustering_model = SpectralClustering(
#         n_clusters=n_clusters,
#         affinity='precomputed',  # IMPORTANT
#         assign_labels='kmeans',  # Good default
#         random_state=42
#     )

#     cluster_labels = clustering_model.fit_predict(similarity_matrix)

#     # Save embeddings, labels, and centroids
#     cluster_centroids = []
#     for cluster in range(n_clusters):
#         cluster_indices = np.where(cluster_labels == cluster)[0]
#         if len(cluster_indices) > 0:
#             cluster_centroids.append(np.mean(embeddings[cluster_indices], axis=0))
#         else:
#             cluster_centroids.append(np.zeros(embeddings.shape[1]))

#     model_data = {
#         "embeddings": embeddings,
#         "labels": cluster_labels.tolist(),
#         "centroids": np.array(cluster_centroids)
#     }

#     with open(MODEL_PATH, "wb") as f:
#         pickle.dump(model_data, f)

#     return model_data


def load_agnes_model():
    """Load AGNES model if available, else return None."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

# Load AGNES model at startup
agnes_model = load_agnes_model()

# def load_spectral_model():
#     """Load Spectral model if available."""
#     if os.path.exists(MODEL_PATH):
#         with open(MODEL_PATH, "rb") as f:
#             return pickle.load(f)
#     return None

# # Load model
# spectral_model = load_spectral_model()

def classify_new_summary(summary):
    """Classify a new summary into the closest AGNES cluster."""
    if agnes_model is None:
        raise ValueError("AGNES model is not trained. Train it first!")

    summary_embedding = bert_model.encode([summary], convert_to_numpy=True)[0]
    
    centroids = np.array(agnes_model["centroids"])  # Use stored centroids
    similarities = cosine_similarity([summary_embedding], centroids)[0]
    
    predicted_cluster = np.argmax(similarities)
    return predicted_cluster

def compute_confidence_score(summary, cluster_id):
    """Compute confidence score based on cosine similarity between summary embedding and cluster centroid."""
    if agnes_model is None:
        raise ValueError("AGNES model is not trained. Train it first!")
    
    # Get the summary embedding
    summary_embedding = bert_model.encode([summary], convert_to_numpy=True)[0]
    
    # Get the centroid of the assigned cluster
    centroids = np.array(agnes_model["centroids"])
    cluster_centroid = centroids[cluster_id]
    
    # Compute cosine similarity
    similarity = cosine_similarity([summary_embedding], [cluster_centroid])[0][0]
    
    # Convert to percentage and round to 2 decimal places
    confidence_score = round(float(similarity) * 100, 2)
    
    return confidence_score

# def classify_new_summary(summary):
#     """Classify a new summary into the closest Spectral cluster."""
#     if spectral_model is None:
#         raise ValueError("Spectral model is not trained. Train it first!")

#     summary_embedding = bert_model.encode([summary], convert_to_numpy=True)[0]
    
#     centroids = np.array(spectral_model["centroids"])
#     similarities = cosine_similarity([summary_embedding], centroids)[0]
    
#     predicted_cluster = np.argmax(similarities)
#     return predicted_cluster

# def evaluate_clustering(agnes_model):
#     """Compute clustering evaluation metrics using stored embeddings & labels."""
#     if "labels" not in agnes_model or "embeddings" not in agnes_model:
#         raise ValueError("AGNES model is missing necessary data.")

#     embeddings = np.array(agnes_model["embeddings"])  # Use stored embeddings, not centroids
#     labels = np.array(agnes_model["labels"])

#     silhouette = float(silhouette_score(embeddings, labels))
#     davies_bouldin = float(davies_bouldin_score(embeddings, labels))

#     return silhouette, davies_bouldin



