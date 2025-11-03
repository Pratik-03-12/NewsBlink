import pickle
try:
    from .clustering import classify_new_summary
    from .modified_preprocessing import clean_text  # Ensure text is preprocessed before prediction
    from .utils import get_category_name
except ImportError:
    from clustering import classify_new_summary
    from modified_preprocessing import clean_text  # Ensure text is preprocessed before prediction
    from utils import get_category_name

# Paths
MODEL_PATH = "backend/models/agnes_model.pkl"
CATEGORY_MAPPING_PATH = "backend/models/cluster_category_mapping.pkl"

# Load trained AGNES model
with open(MODEL_PATH, "rb") as f:
    spectral_model = pickle.load(f)

# Load category mapping
with open(CATEGORY_MAPPING_PATH, "rb") as f:
    cluster_to_category = pickle.load(f)

def test_model(summary):
    """Predict the cluster and category for a given summary."""
    cleaned_summary = clean_text(summary)
    
    # Predict cluster
    cluster_id = classify_new_summary(cleaned_summary)
    
    # Get category from mapping
    category = get_category_name(cluster_id)
    
    return cluster_id, category

# Example test case
if __name__ == "__main__":
    
    test_summary = input("Enter news summary: ")
    cluster, predicted_category = test_model(test_summary)
    print(f"Predicted Cluster: {cluster}")
    print(f"Predicted Category: {predicted_category}")
