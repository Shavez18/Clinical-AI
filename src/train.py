import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix
)

from xgboost import XGBClassifier

# -------------------------
# Load Dataset
# -------------------------
data = pd.read_csv("C:\\Major project\\ai-health-assistant\\data\\raw\\diabetes.csv")

cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in cols:
    data[col] = data[col].replace(0, np.nan)
    data[col].fillna(data[col].median(), inplace=True)

X = data.drop("Outcome", axis=1)
y = data["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -------------------------
# Hyperparameter Tuning
# -------------------------
xgb = XGBClassifier(eval_metric="logloss")

param_dist = {
    "n_estimators": [100, 200, 300],
    "max_depth": [3, 4, 5, 6],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

random_search = RandomizedSearchCV(
    xgb,
    param_distributions=param_dist,
    n_iter=20,
    scoring="roc_auc",
    cv=cv,
    verbose=1,
    n_jobs=-1
)

random_search.fit(X_train, y_train)
best_model = random_search.best_estimator_

# -------------------------
# Evaluation
# -------------------------
probs = best_model.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, probs)

precision, recall, thresholds = precision_recall_curve(y_test, probs)
f1_scores = 2 * (precision * recall) / (precision + recall)
best_threshold = thresholds[np.argmax(f1_scores)]

preds = (probs >= best_threshold).astype(int)

print("Best ROC-AUC:", round(roc_auc, 4))
print("Best Threshold:", round(best_threshold, 4))
print(classification_report(y_test, preds))

# -------------------------
# Create Visualization Folder
# -------------------------
os.makedirs("C:\\Major project\\ai-health-assistant\\src\\models", exist_ok=True)

# -------------------------
# ROC Curve
# -------------------------
fpr, tpr, _ = roc_curve(y_test, probs)
plt.figure()
plt.plot(fpr, tpr)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.savefig("C:\\Major project\\ai-health-assistant\\src\\models\\roc_curve.png")
plt.close()

# -------------------------
# Precision-Recall Curve
# -------------------------
plt.figure()
plt.plot(recall, precision)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.savefig("C:\\Major project\\ai-health-assistant\\src\\models\\pr_curve.png")
plt.close()

# -------------------------
# Confusion Matrix
# -------------------------
cm = confusion_matrix(y_test, preds)
plt.figure()
sns.heatmap(cm, annot=True, fmt="d")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.savefig("C:\\Major project\\ai-health-assistant\\src\\models\\confusion_matrix.png")
plt.close()

# -------------------------
# Feature Importance
# -------------------------
importances = best_model.feature_importances_
feature_names = data.drop("Outcome", axis=1).columns

plt.figure()
sns.barplot(x=importances, y=feature_names)
plt.title("Feature Importance")
plt.savefig("C:\\Major project\\ai-health-assistant\\src\\models\\feature_importance.png")
plt.close()

# -------------------------
# Save Model
# -------------------------
joblib.dump(best_model, "C:\\Major project\\ai-health-assistant\\src\\models\\elite_diabetes_model.pkl")
joblib.dump(scaler, "C:\\Major project\\ai-health-assistant\\src\\models\\scaler.pkl")
joblib.dump(best_threshold, "C:\\Major project\\ai-health-assistant\\src\\models\\threshold.pkl")

print("Elite model saved successfully.")