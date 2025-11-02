import pickle

MODEL_PATH = "backend/models/agnes_model.pkl"
# MODEL_PATH = "backend/models/cluster_category_mapping.pkl"

# Load and inspect the model file
with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

print("Type of model_data:", type(model_data))  # Check type
print("Model Content Preview:", model_data)  # Print part of the content

# If model_data is a dictionary, print available keys
if isinstance(model_data, dict):
    print("Model Keys:", model_data.keys())
    if "labels" in model_data:
        print("Example Label Values:", model_data["labels"][:10])
    else:
        print("Labels Missing!")
    if "centroids" in model_data:
        print("Centroids Available!")
    else:
        print("Centroids Missing!")

