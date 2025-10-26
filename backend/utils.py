"""Utility functions for NewsBlink backend."""
import pickle
import os

CATEGORY_MAPPING_PATH = "backend/models/cluster_category_mapping.pkl"

# Load category mapping with validation
if os.path.exists(CATEGORY_MAPPING_PATH):
    with open(CATEGORY_MAPPING_PATH, "rb") as f:
        cluster_to_category = pickle.load(f)
else:
    print(f"WARNING: Category mapping file not found at {CATEGORY_MAPPING_PATH}")
    cluster_to_category = {}

def get_category_name(cluster_id):
    return cluster_to_category.get(cluster_id, "Unknown")
