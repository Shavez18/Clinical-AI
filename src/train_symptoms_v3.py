import pandas as pd
import numpy as np
import joblib
import os
import json
import random
import time

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score

# Ensure src in path to import nlp module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.nlp.clinical_parser import clinical_parser

# -------------------------
# Load & Prepare Dataset
# -------------------------
print("Loading core dataset...")
data_path = "C:\\Major project\\ai-health-assistant\\data\\raw\\DiseaseAndSymptoms.csv"
data = pd.read_csv(data_path)
print("Original Dataset Shape:", data.shape)

symptom_cols = [col for col in data.columns if "Symptom" in col]

# Combine base symptoms into a list per row
data["symptom_list"] = data[symptom_cols].apply(
    lambda x: [str(item).strip().lower().replace("_", " ") for item in x if pd.notna(item) and str(item).strip() != ""],
    axis=1
)

# -------------------------
# Data Augmentation Engine
# -------------------------
print("Starting Data Augmentation phase...")
# To prevent constant/similar predictions and make the model highly robust to variations,
# we will synthetically expand the dataset.

noise_words = [
    "patient complains of", "feeling", "experiencing", "started yesterday", 
    "severe", "mild", "for 3 days", "chronic", "acute", "sudden", "since morning"
]

synonyms = {
    "itching": ["itchy skin", "scratching", "pruritus"],
    "skin rash": ["breaking out", "rash", "red spots"],
    "continuous sneezing": ["sneezing a lot", "always sneezing"],
    "shivering": ["shaking", "chills", "feeling cold"],
    "stomach pain": ["tummy ache", "belly pain", "abdominal pain", "cramps"],
    "acidity": ["heartburn", "acid reflux"],
    "vomiting": ["throwing up", "puking"],
    "fatigue": ["tired", "exhausted", "no energy"],
    "weight loss": ["losing weight"],
    "lethargy": ["lazy", "tired"],
    "high fever": ["fever", "high temperature", "hot"],
    "headache": ["migraine", "head pain", "head aches"],
    "mild fever": ["slight fever", "warm"],
    "chest pain": ["chest tightness", "chest hurts", "heart pain"],
    "breathlessness": ["shortness of breath", "can't breathe", "panting"]
}

augmented_rows = []

for index, row in data.iterrows():
    disease = row["Disease"]
    base_symptoms = row["symptom_list"]
    
    # Keep original (clean string)
    augmented_rows.append({"Disease": disease, "Text": " ".join(base_symptoms)})
    
    # Generate 3 variations per row
    for _ in range(3):
        # 1. Randomly drop 1 or 2 symptoms to simulate incomplete notes
        k = max(1, len(base_symptoms) - random.randint(0, 2))
        sampled = random.sample(base_symptoms, k)
        
        # 2. Inject Synonyms
        varied = []
        for s in sampled:
            if s in synonyms and random.random() > 0.4:
                varied.append(random.choice(synonyms[s]))
            else:
                varied.append(s)
                
        # 3. Add noise
        if random.random() > 0.5:
            varied.insert(0, random.choice(noise_words))
            
        random.shuffle(varied)
        augmented_rows.append({"Disease": disease, "Text": " ".join(varied)})

aug_df = pd.DataFrame(augmented_rows)
print(f"Data Augmented randomly from {len(data)} to {len(aug_df)} rows.")

# -------------------------
# NLP Feature Extraction
# -------------------------
print("Applying Clinical NLP parser to all rows... (Takes ~10-15 seconds)")
start_t = time.time()

# We strictly enforce that the model learns on the EXACT same normalized tokens 
# output by the inference pipeline's spaCy parser.
def extract_normalized_features(text):
    parsed = clinical_parser.parse(text)
    # The clinical parser already returns space-separated lemmas and mapped synonyms
    return parsed["clean_text"]

aug_df["clean_text"] = aug_df["Text"].apply(extract_normalized_features)
print(f"NLP Parsing complete in {time.time() - start_t:.1f}s")

# Filter out empty texts
aug_df = aug_df[aug_df["clean_text"].str.strip() != ""]

X = aug_df["clean_text"]
y = aug_df["Disease"]

# -------------------------
# Train-Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y
)

# -------------------------
# Vectorization & Model Pipeline
# -------------------------
print("Vectorizing Text data (TF-IDF)...")
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=8000,
    ngram_range=(1, 3),
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("Training Advanced RandomForest Classifier...")
base_model = RandomForestClassifier(
    n_estimators=150,
    class_weight="balanced",
    max_depth=30,
    random_state=42,
    n_jobs=-1
)

print("Applying Isotonic Probability Calibration...")
calibrated_model = CalibratedClassifierCV(estimator=base_model, method="isotonic", cv=3)
calibrated_model.fit(X_train_tfidf, y_train)

# -------------------------
# Evaluation
# -------------------------
preds = calibrated_model.predict(X_test_tfidf)
print(f"Validation Accuracy on Augmented Data: {accuracy_score(y_test, preds):.4f}")

# -------------------------
# Build Profiles for Inference engine
# -------------------------
print("Building Disease Profiles...")
base_model.fit(X_train_tfidf, y_train)
feature_names = vectorizer.get_feature_names_out()

profile_map = {}
for disease in np.unique(y_train):
    disease_indices = (y_train == disease).values
    mean_vector = np.squeeze(np.asarray(X_train_tfidf[disease_indices].mean(axis=0)))
    top_indices = mean_vector.argsort()[-10:][::-1]
    top_symptoms = [feature_names[i] for i in top_indices if mean_vector[i] > 0]
    profile_map[disease] = top_symptoms

# -------------------------
# Export Artifacts
# -------------------------
model_dir = "C:\\Major project\\ai-health-assistant\\src\\models"
os.makedirs(model_dir, exist_ok=True)

joblib.dump(calibrated_model, os.path.join(model_dir, "differential_model.pkl"))
joblib.dump(vectorizer, os.path.join(model_dir, "clinical_vectorizer.pkl"))

with open(os.path.join(model_dir, "disease_profiles.json"), "w") as f:
    json.dump(profile_map, f, indent=4)

print("Real Dataset & Training Pipeline complete. ML Models Overwritten.")
