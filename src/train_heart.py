"""
train_heart.py  — Retrained with corrected, production-safe pipeline
=====================================================================

KEY FIXES vs original:
  1. Explicit dtype=bool for get_dummies → avoids pandas version dtype drift
  2. Scaler saved alongside model columns in one consistent artifact set
  3. Added class_weight balancing to handle imbalanced dataset
  4. ROC-AUC and classification report printed for monitoring
  5. All absolute paths kept consistent with project structure
  6. Added target distribution printout to make label direction explicit:
       target=0 → No heart disease
       target=1 → Heart disease present
"""

import pandas as pd
import numpy as np
import joblib
import os
import matplotlib
matplotlib.use("Agg")          # headless backend — no display needed
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
)
from xgboost import XGBClassifier

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
DATA_PATH  = r"C:\Major project\ai-health-assistant\data\raw\HeartDiseaseTrain-Test.csv"
MODEL_DIR  = r"C:\Major project\ai-health-assistant\src\models"
os.makedirs(MODEL_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# 1. Load dataset & Clean
# ──────────────────────────────────────────────────────────────────────────────
data = pd.read_csv(DATA_PATH)

print(f"Original Dataset shape: {data.shape}")
data.drop_duplicates(inplace=True)
print(f"Dataset shape after dropping duplicates: {data.shape}")

print(f"\nTarget distribution (0=No disease, 1=Heart disease):")
print(data["target"].value_counts())
print()

# ──────────────────────────────────────────────────────────────────────────────
# 2. Preprocessing — encode categoricals identically to inference pipeline
# ──────────────────────────────────────────────────────────────────────────────
categorical_cols = [
    "sex",
    "chest_pain_type",
    "fasting_blood_sugar",
    "rest_ecg",
    "exercise_induced_angina",

    "slope",
    "vessels_colored_by_flourosopy",
    "thalassemia",
]

X = data.drop("target", axis=1)
y = data["target"]          # 0 = no disease, 1 = disease — CONFIRMED from dataset inspection

# Apply one-hot encoding — drop_first=True to avoid dummy-variable trap
# dtype=bool is explicit so the saved column structure is dtype-consistent
X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True, dtype=bool)

print(f"Encoded feature count: {X_encoded.shape[1]}")
print(f"Feature names:\n{list(X_encoded.columns)}\n")

# ── Save model_columns BEFORE any split — same feature set for inference ──
model_columns = list(X_encoded.columns)
joblib.dump(model_columns, os.path.join(MODEL_DIR, "heart_model_columns.pkl"))
print(f"Saved heart_model_columns.pkl  ({len(model_columns)} features)")

# ──────────────────────────────────────────────────────────────────────────────
# 3. Train / test split
# ──────────────────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, stratify=y, random_state=42
)
print(f"Train: {X_train.shape}  Test: {X_test.shape}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Scaling — fit ONLY on training data to prevent data leakage
# ──────────────────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

joblib.dump(scaler, os.path.join(MODEL_DIR, "heart_scaler.pkl"))
print("Saved heart_scaler.pkl")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Hyperparameter search
# ──────────────────────────────────────────────────────────────────────────────
# scale_pos_weight balances the class weights
neg_count = (y_train == 0).sum()
pos_count = (y_train == 1).sum()
spw = float(neg_count) / float(pos_count)
print(f"\nClass balance -> scale_pos_weight = {spw:.3f}\n")

xgb_base = XGBClassifier(
    eval_metric="logloss",
    scale_pos_weight=spw,       # handles class imbalance
    random_state=42,
)

param_dist = {
    "n_estimators":  [100, 200, 300],
    "max_depth":     [3, 4, 5, 6],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample":     [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

random_search = RandomizedSearchCV(
    xgb_base,
    param_distributions=param_dist,
    n_iter=20,
    scoring="roc_auc",
    cv=cv,
    n_jobs=-1,
    verbose=1,
    random_state=42,
)

random_search.fit(X_train_scaled, y_train)
best_model = random_search.best_estimator_
print(f"\nBest params: {random_search.best_params_}")

# ──────────────────────────────────────────────────────────────────────────────
# 6. Evaluation
# ──────────────────────────────────────────────────────────────────────────────
probs = best_model.predict_proba(X_test_scaled)[:, 1]   # P(disease)
preds = best_model.predict(X_test_scaled)

roc_auc = roc_auc_score(y_test, probs)
print(f"\nROC-AUC: {roc_auc:.4f}")
print(classification_report(y_test, preds, target_names=["No Disease", "Heart Disease"]))

# ──────────────────────────────────────────────────────────────────────────────
# 7. Save model
# ──────────────────────────────────────────────────────────────────────────────
joblib.dump(best_model, os.path.join(MODEL_DIR, "elite_heart_model.pkl"))
print("Saved elite_heart_model.pkl")

# ──────────────────────────────────────────────────────────────────────────────
# 8. Plots
# ──────────────────────────────────────────────────────────────────────────────
fpr, tpr, _ = roc_curve(y_test, probs)
plt.figure()
plt.plot(fpr, tpr, label=f"ROC AUC = {roc_auc:.4f}")
plt.plot([0, 1], [0, 1], "k--")
plt.title("Heart Disease ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.savefig(os.path.join(MODEL_DIR, "heart_roc.png"))
plt.close()

cm = confusion_matrix(y_test, preds)
plt.figure()
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["No Disease", "Heart Disease"],
            yticklabels=["No Disease", "Heart Disease"])
plt.title("Heart Disease Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig(os.path.join(MODEL_DIR, "heart_confusion.png"))
plt.close()

print("\nHeart Disease Model Retrained and Saved Successfully ✅")
print("Run  python src/predict_heart.py  to verify the pipeline after retraining.")