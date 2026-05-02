import sys
import traceback
import os

out_path = r"C:\Major project\ai-health-assistant\src\train_debug_out.txt"

try:
    fout = open(out_path, "w", encoding="utf-8")
    fout.write("START\n")
    fout.flush()

    fout.write(f"Python: {sys.version}\n")
    fout.flush()

    import sklearn
    fout.write(f"sklearn: {sklearn.__version__}\n"); fout.flush()

    import xgboost
    fout.write(f"xgboost: {xgboost.__version__}\n"); fout.flush()

    import pandas as pd
    fout.write(f"pandas: {pd.__version__}\n"); fout.flush()

    import numpy as np
    import joblib
    from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report, roc_auc_score
    from xgboost import XGBClassifier

    DATA_PATH = r"C:\Major project\ai-health-assistant\data\raw\HeartDiseaseTrain-Test.csv"
    MODEL_DIR = r"C:\Major project\ai-health-assistant\src\models"

    fout.write("Loading data...\n"); fout.flush()
    data = pd.read_csv(DATA_PATH)
    fout.write(f"Shape: {data.shape}, target counts: {dict(data['target'].value_counts())}\n"); fout.flush()

    categorical_cols = [
        "sex", "chest_pain_type", "fasting_blood_sugar", "rest_ecg",
        "exercise_induced_angina", "slope", "vessels_colored_by_flourosopy", "thalassemia",
    ]
    X = data.drop("target", axis=1)
    y = data["target"]
    X_enc = pd.get_dummies(X, columns=categorical_cols, drop_first=True, dtype=bool)
    fout.write(f"Encoded shape: {X_enc.shape}\n"); fout.flush()

    model_columns = list(X_enc.columns)
    joblib.dump(model_columns, os.path.join(MODEL_DIR, "heart_model_columns.pkl"))
    fout.write("Saved heart_model_columns.pkl\n"); fout.flush()

    X_train, X_test, y_train, y_test = train_test_split(X_enc, y, test_size=0.2, stratify=y, random_state=42)
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_train)
    Xte = scaler.transform(X_test)
    joblib.dump(scaler, os.path.join(MODEL_DIR, "heart_scaler.pkl"))
    fout.write("Saved heart_scaler.pkl\n"); fout.flush()

    neg = int((y_train == 0).sum()); pos = int((y_train == 1).sum())
    spw = neg / pos
    fout.write(f"spw={spw:.3f} neg={neg} pos={pos}\n"); fout.flush()

    xgb = XGBClassifier(eval_metric="logloss", scale_pos_weight=spw, random_state=42,
                        n_estimators=200, max_depth=4, learning_rate=0.05)
    fout.write("Fitting...\n"); fout.flush()
    xgb.fit(Xtr, y_train)
    fout.write("Fitted!\n"); fout.flush()

    probs = xgb.predict_proba(Xte)[:, 1]
    preds = xgb.predict(Xte)
    auc = roc_auc_score(y_test, probs)
    fout.write(f"ROC-AUC: {auc:.4f}\n")
    fout.write(classification_report(y_test, preds))
    fout.flush()

    joblib.dump(xgb, os.path.join(MODEL_DIR, "elite_heart_model.pkl"))
    fout.write("Saved elite_heart_model.pkl\n")
    fout.write("DONE\n")
    fout.flush()
    fout.close()

except Exception:
    try:
        fout.write("\n\nERROR:\n" + traceback.format_exc())
        fout.flush()
        fout.close()
    except Exception:
        with open(out_path, "a") as f2:
            f2.write("\n\nFATAL:\n" + traceback.format_exc())
