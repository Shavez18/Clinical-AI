import pandas as pd
import joblib
import json

heart_model = joblib.load(r"C:\Major project\ai-health-assistant\src\models\elite_heart_model.pkl")
heart_scaler = joblib.load(r"C:\Major project\ai-health-assistant\src\models\heart_scaler.pkl")
heart_model_columns = joblib.load(r"C:\Major project\ai-health-assistant\src\models\heart_model_columns.pkl")

# Data from the user screenshot
data = {
    "age": 45,
    "sex": 1,
    "cp": 0,
    "trestbps": 200,
    "chol": 200,
    "fbs": 0,
    "restecg": 0,
    "thalach": 100,
    "exang": 0,
    "oldpeak": 6.0,
    "slope": 0,  # hardcoded to 0 in app.py frontend!
    "ca": 0,
    "thal": 0
}

input_df = pd.DataFrame([{
    "age": data["age"],
    "sex": "Male" if data["sex"] == 1 else "Female",
    "chest_pain_type": {0: "Typical angina", 1: "Atypical angina", 2: "Non-anginal pain", 3: "Asymptomatic"}.get(data["cp"], "Typical angina"),
    "resting_blood_pressure": data["trestbps"],
    "cholestoral": data["chol"],
    "fasting_blood_sugar": "Greater than 120 mg/ml" if data["fbs"] == 1 else "Lower than 120 mg/ml",
    "rest_ecg": {0: "Normal", 1: "ST-T wave abnormality", 2: "Left ventricular hypertrophy"}.get(data["restecg"], "Normal"),
    "Max_heart_rate": data["thalach"],
    "exercise_induced_angina": "Yes" if data["exang"] == 1 else "No",
    "oldpeak": data["oldpeak"],
    "slope": {0: "Downsloping", 1: "Flat", 2: "Upsloping"}.get(data["slope"], "Downsloping"),
    "vessels_colored_by_flourosopy": {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four"}.get(data["ca"], "Zero"),
    "thalassemia": {0: "Normal", 1: "Fixed Defect", 2: "Reversable Defect", 3: "No"}.get(data["thal"], "Normal")
}])

categorical_cols = [
    'sex', 'chest_pain_type', 'fasting_blood_sugar', 'rest_ecg',
    'exercise_induced_angina', 'slope', 'vessels_colored_by_flourosopy', 'thalassemia'
]

input_encoded = pd.get_dummies(input_df, columns=categorical_cols)

for col in heart_model_columns:
    if col not in input_encoded.columns:
        input_encoded[col] = False

features = input_encoded[heart_model_columns]

# Print out feature vector before scaling
features_dict = features.iloc[0].to_dict()

# Print out scale info
features_scaled = heart_scaler.transform(features)

probability = float(heart_model.predict_proba(features_scaled)[0][1])

output = {
    "features": features_dict,
    "scaled": features_scaled[0].tolist(),
    "probability": probability
}

with open(r"C:\Major project\ai-health-assistant\test_predict_out.json", "w") as f:
    json.dump(output, f, indent=4)
