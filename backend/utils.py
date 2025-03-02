import pickle

CATEGORY_MAPPING_PATH = "backend/models/cluster_category_mapping.pkl"

# Load category mapping
with open(CATEGORY_MAPPING_PATH, "rb") as f:
    cluster_to_category = pickle.load(f)

def get_category_name(cluster_id):
    return cluster_to_category.get(cluster_id, "Unknown")
