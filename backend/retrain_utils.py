import pandas as pd
import pickle
from collections import Counter
from threading import Lock
try:
    from .clustering import train_agnes_clustering
    from .modified_preprocessing import preprocess_for_clustering
except ImportError:
    from clustering import train_agnes_clustering
    from modified_preprocessing import preprocess_for_clustering

DATASET_PATH = "backend/datasets/Research_project_Dataset_1.xlsx"
MODEL_PATH = "backend/models/agnes_model.pkl"
CATEGORY_MAPPING_PATH = "backend/models/cluster_category_mapping.pkl"

# Global lock for dataset/model access
DATASET_LOCK = Lock()

def get_top_words(df, column="Summary", category_column="Category", top_n=10):
    keywords = {}
    for group in df[category_column].unique():
        texts = df[df[category_column] == group][column].str.lower().str.split()
        words = [word for text in texts.dropna() for word in text]
        common_words = [word for word, count in Counter(words).most_common(top_n)]
        keywords[group] = common_words
    return keywords

def match_clusters_to_categories(cluster_keywords, category_keywords):
    cluster_to_category = {}
    assigned_categories = set()
    for cluster, cluster_words in cluster_keywords.items():
        best_match = None
        max_overlap = 0
        for category, category_words in category_keywords.items():
            overlap = len(set(cluster_words) & set(category_words))
            if overlap > max_overlap and category not in assigned_categories:
                max_overlap = overlap
                best_match = category
        if best_match is None:
            unassigned = set(category_keywords.keys()) - assigned_categories
            best_match = unassigned.pop() if unassigned else "unknown"
        cluster_to_category[cluster] = best_match
        assigned_categories.add(best_match)
    return cluster_to_category

def retrain_model():
    with DATASET_LOCK:
        df = pd.read_excel(DATASET_PATH)
        # Preprocess summaries for clustering
        df["Processed_Summary"] = df["Summary"].astype(str).apply(preprocess_for_clustering)
        # Retrain clustering model
        summaries = df["Processed_Summary"].dropna().tolist()
        model_data = train_agnes_clustering(summaries)
        df["Cluster"] = model_data["labels"]
        # Extract keywords
        category_keywords = get_top_words(df, column="Summary", category_column="Category")
        cluster_keywords = get_top_words(df, column="Summary", category_column="Cluster")
        # Map clusters to categories
        cluster_to_category = match_clusters_to_categories(cluster_keywords, category_keywords)
        # Save model and mapping
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model_data, f)
        with open(CATEGORY_MAPPING_PATH, "wb") as f:
            pickle.dump(cluster_to_category, f) 