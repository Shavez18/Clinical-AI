import joblib
import json

try:
    cols = joblib.load(r"C:\Major project\ai-health-assistant\src\models\heart_model_columns.pkl")
    with open(r"C:\Major project\ai-health-assistant\test_cols.json", "w", encoding="utf-8") as f:
        json.dump(cols, f)
except Exception as e:
    with open(r"C:\Major project\ai-health-assistant\test_cols.json", "w", encoding="utf-8") as f:
        json.dump({"error": str(e)}, f)
