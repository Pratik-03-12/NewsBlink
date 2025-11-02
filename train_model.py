import pandas as pd
import pickle
from collections import Counter
from clustering import train_agnes_clustering

# Paths
DATASET_PATH = "backend/datasets/Research_project_Dataset_1.xlsx"
MODEL_PATH = "backend/models/agnes_model.pkl"
# MODEL_PATH = "backend/models/spectral_model.pkl"
CATEGORY_MAPPING_PATH = "backend/models/cluster_category_mapping.pkl"

# Load dataset
df = pd.read_excel(DATASET_PATH)
print(df.columns)

# Ensure required columns exist
if "Summary" not in df.columns or "Category" not in df.columns:
    raise ValueError("Required columns ('Summary' or 'Category') not found in dataset!")

# Train AGNES clustering on summaries
summaries = df["Summary"].dropna().tolist()  # Remove NaN values
model_data = train_agnes_clustering(summaries)  # Returns a dictionary

# Store cluster labels in the DataFrame
df["Cluster"] = model_data["labels"]

# Function to extract top words from text for each category/cluster
def get_top_words(df, column="Summary", category_column="Category", top_n=10):
    keywords = {}

    for group in df[category_column].unique():
        texts = df[df[category_column] == group][column].str.lower().str.split()
        words = [word for text in texts.dropna() for word in text]
        common_words = [word for word, count in Counter(words).most_common(top_n)]
        keywords[group] = common_words

    return keywords

# Extract category and cluster keywords
category_keywords = get_top_words(df, category_column="Category")
cluster_keywords = get_top_words(df, category_column="Cluster")


def match_clusters_to_categories(cluster_keywords, category_keywords):
    cluster_to_category = {}

    # Track categories already assigned to prevent duplicates
    assigned_categories = set()

    for cluster, cluster_words in cluster_keywords.items():
        best_match = None
        max_overlap = 0

        for category, category_words in category_keywords.items():
            overlap = len(set(cluster_words) & set(category_words))

            # Ensure each category is only assigned once
            if overlap > max_overlap and category not in assigned_categories:
                max_overlap = overlap
                best_match = category

        # If no strong match is found, assign the most common unassigned category
        if best_match is None:
            unassigned_categories = set(category_keywords.keys()) - assigned_categories
            best_match = unassigned_categories.pop() if unassigned_categories else "unknown"

        cluster_to_category[cluster] = best_match
        assigned_categories.add(best_match)  # Mark this category as used

    return cluster_to_category


# Assign clusters to categories
cluster_to_category = match_clusters_to_categories(cluster_keywords, category_keywords)

# Save the complete clustering model dictionary
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model_data, f)  # Saving full dictionary with "centroids" and "labels"

# Save category-cluster mapping
with open(CATEGORY_MAPPING_PATH, "wb") as f:
    pickle.dump(cluster_to_category, f)

print("AGNES Model Training & Category Mapping Completed & Saved!")
# print("Spectral Model Training & Category Mapping Completed & Saved!")