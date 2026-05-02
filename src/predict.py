import joblib
import numpy as np

# -------------------------
# Load Elite Model Artifacts
# -------------------------
model = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\elite_diabetes_model.pkl")
scaler = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\scaler.pkl")
threshold = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\threshold.pkl")

# -------------------------
# Prediction Function
# -------------------------
def predict_diabetes(features):
    """
    features order:
    [Pregnancies, Glucose, BloodPressure, SkinThickness,
     Insulin, BMI, DiabetesPedigreeFunction, Age]
    """

    features = np.array(features).reshape(1, -1)
    features_scaled = scaler.transform(features)

    probability = model.predict_proba(features_scaled)[0][1]

    # Use optimized medical threshold instead of 0.5
    prediction = 1 if probability >= threshold else 0

    return prediction, probability


# -------------------------
# Example Test
# -------------------------
if __name__ == "__main__":

    sample = [2, 120, 70, 20, 85, 30.5, 0.5, 35]

    pred, prob = predict_diabetes(sample)

    print("\n===== Diabetes Risk Report =====")

    if pred == 1:
        print("Prediction: ⚠️ High Risk (Diabetic)")
    else:
        print("Prediction: ✅ Low Risk (Not Diabetic)")

    print("Risk Probability:", round(prob * 100, 2), "%")
    print("Model Threshold Used:", round(threshold, 4))