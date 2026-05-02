import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# -------------------------
# Load Dataset
# -------------------------
data = pd.read_csv("C:\\Major project\\ai-health-assistant\\data\\raw\\DiseaseAndSymptoms.csv")

print("Dataset Shape:", data.shape)

# -------------------------
# Identify Symptom Columns
# -------------------------
symptom_cols = [col for col in data.columns if "Symptom" in col]

print("Total Symptom Columns:", len(symptom_cols))

# -------------------------
# Combine Symptoms into Single Text Field
# -------------------------
data["combined_symptoms"] = (
    data[symptom_cols]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.lower()
)

# Remove extra spaces
data["combined_symptoms"] = data["combined_symptoms"].str.replace(r"\s+", " ", regex=True)

X = data["combined_symptoms"]
y = data["Disease"]

# -------------------------
# Train-Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -------------------------
# TF-IDF Vectorization
# -------------------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000,
    ngram_range=(1,2)
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# -------------------------
# Train Model
# -------------------------
model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced"
)

model.fit(X_train_tfidf, y_train)

preds = model.predict(X_test_tfidf)

print("\nModel Performance:")
print("Accuracy:", round(accuracy_score(y_test, preds), 4))
print(classification_report(y_test, preds))

# -------------------------
# Save Model Artifacts
# -------------------------
os.makedirs("C:\\Major project\\ai-health-assistant\\src\\models", exist_ok=True)

joblib.dump(model, "C:\\Major project\\ai-health-assistant\\src\\models\\symptom_model.pkl")
joblib.dump(vectorizer, "C:\\Major project\\ai-health-assistant\\src\\models\\symptom_vectorizer.pkl")

print("\nSymptom NLP Model Saved Successfully.")