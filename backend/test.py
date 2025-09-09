import os
import sys
import joblib

# Base directory = root of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

models = {}

def safe_load_model(name, relative_path):
    """Safe loader with full debug info."""
    try:
        model_path = os.path.join(BASE_DIR, relative_path)
        if not os.path.exists(model_path):
            print(f"[ERROR] {name} file not found at {model_path}")
            return None
        model = joblib.load(model_path)
        print(f"[SUCCESS] {name} loaded from {model_path}")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load {name}: {e}")
        return None

# ✅ Load all diabetes models
models['diabetes_subtype_classifier'] = safe_load_model(
    "diabetes_subtype_classifier", os.path.join('diabetes_class', 'lgbm_classifier.pkl')
)
models['diabetes_risk_model'] = safe_load_model(
    "diabetes_risk_model", os.path.join('diabetes_class', 'kmeans_model.pkl')
)
models['diabetes_preprocessor'] = safe_load_model(
    "diabetes_preprocessor", os.path.join('diabetes_class', 'preprocessor.pkl')
)
models['diabetes_cluster_map'] = safe_load_model(
    "diabetes_cluster_map", os.path.join('diabetes_class', 'cluster_risk_map.pkl')
)

print("--- Diabetes subtype models loading finished ---")
