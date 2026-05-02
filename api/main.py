from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from src.drug_checker.openfda_engine import analyze_drug_interactions
from src.predict_heart import predict_heart as _predict_heart
from typing import List
from sqlalchemy.orm import Session
from api.database import SessionLocal, engine
from api.models import User , PredictionHistory
from api.auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.models import Base
from jose import JWTError, jwt
from api.auth import SECRET_KEY, ALGORITHM

app = FastAPI(title="AI Health Assistant API")

# -------------------------
# Load Diabetes Model
# -------------------------
diabetes_model = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\elite_diabetes_model.pkl")
diabetes_scaler = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\scaler.pkl")
diabetes_threshold = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\threshold.pkl")

# -------------------------
# Heart Model — loaded inside src.predict_heart at import time
# -------------------------

# -------------------------
# Load Symptom Model
# -------------------------
symptom_model = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\symptom_model.pkl")
symptom_vectorizer = joblib.load("C:\\Major project\\ai-health-assistant\\src\\models\\symptom_vectorizer.pkl")

# -------------------------
# Database Setup
# -------------------------
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Authentication
# ------------------------- 
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -------------------------
# Input Schemas
# -------------------------

class DiabetesInput(BaseModel):
    Pregnancies: int
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int


class HeartInput(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: float
    chol: float
    fbs: int
    restecg: int
    thalach: float
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

class DifferentialInput(BaseModel):
    symptoms: str
    age: int = 30
    gender: str = "Unknown"
    duration: str = ""

class DrugInput(BaseModel):
    drugs: List[str]

class RegisterInput(BaseModel):
    username: str
    email: str
    password: str

# -------------------------
# Home Route
# -------------------------
@app.get("/")
def home():
    return {"message": "AI Health Assistant API Running 🚀"}


# -------------------------
# Diabetes Endpoint
# -------------------------
@app.post("/predict/diabetes")
def predict_diabetes(
    data: DiabetesInput,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    features = np.array([[
        data.Pregnancies,
        data.Glucose,
        data.BloodPressure,
        data.SkinThickness,
        data.Insulin,
        data.BMI,
        data.DiabetesPedigreeFunction,
        data.Age
    ]])

    features_scaled = diabetes_scaler.transform(features)
    probability = diabetes_model.predict_proba(features_scaled)[0][1]
    prediction = 1 if probability >= diabetes_threshold else 0
    history = PredictionHistory(
    username=current_user,
    prediction_type="diabetes",
    result="High Risk" if prediction == 1 else "Low Risk",
    probability=float(probability)
)
    db.add(history)
    db.commit()

    return {
        "prediction": int(prediction),
        "risk_percentage": round(float(probability * 100), 2)
    }


# -------------------------
# Heart Endpoint
# -------------------------
@app.post("/predict/heart")
def predict_heart_endpoint(
    data: HeartInput,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Correct inference pipeline:
      1. Map integer inputs → exact CSV string categories
      2. pd.get_dummies  (same call as training)
      3. Align & reorder columns to heart_model_columns
      4. StandardScaler.transform (fitted on training data)
      5. predict_proba[0][1]  → P(heart disease)  ← class-1, NOT class-0
    """

    # Delegate to the validated, fully-correct pipeline in src/predict_heart.py
    try:
        probability, prediction = _predict_heart(
            age      = data.age,
            sex      = data.sex,
            cp       = data.cp,
            trestbps = data.trestbps,
            chol     = data.chol,
            fbs      = data.fbs,
            restecg  = data.restecg,
            thalach  = data.thalach,
            exang    = data.exang,
            oldpeak  = data.oldpeak,
            slope    = data.slope,
            ca       = data.ca,
            thal     = data.thal,
        )
    except ValueError as exc:
        # Invalid physiological inputs (e.g. 0 BP, 0 cholesterol)
        raise HTTPException(status_code=422, detail=str(exc))

    history = PredictionHistory(
        username         = current_user,
        prediction_type  = "heart",
        result           = "High Risk" if prediction == 1 else "Low Risk",
        probability      = probability,
    )
    db.add(history)
    db.commit()

    return {
        "prediction":      int(prediction),
        "risk_percentage": round(probability * 100, 2),
    }

# -------------------------
# Advanced Differential Diagnosis Endpoint
# -------------------------
from src.nlp.clinical_parser import clinical_parser
from src.symptom_engine.differential_model import differential_engine

@app.post("/analyze/differential")
def analyze_differential(
    data: DifferentialInput,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # 1. NLP Parse & Emergency Check
    parsed = clinical_parser.parse(data.symptoms)
    emergencies = parsed.get("flags", [])
    triage_level = "High Emergency" if emergencies else "Standard"

    # 2. Advanced Differential Inference (with Rules Engine)
    differentials = differential_engine.predict_differentials(
        parsed_symptoms=parsed,
        age=data.age,
        gender=data.gender,
        top_n=3
    )

    # 3. Log History
    # We log the top prediction if available
    top_pred = differentials[0]["disease"] if differentials else "Unknown"
    top_prob = differentials[0]["probability_percentage"] / 100.0 if differentials else 0.0
    
    history = PredictionHistory(
        username=current_user,
        prediction_type="differential_triage",
        result=top_pred,
        probability=float(top_prob)
    )
    db.add(history)
    db.commit() 

    return {
        "triage_level": triage_level,
        "emergency_flags": emergencies,
        "parsed_duration": parsed.get("duration", "Unknown"),
        "severity": parsed.get("severity", "Moderate"),
        "differentials": differentials,
        "disclaimer": "This is an AI decision-support tool, not a definitive medical diagnosis. Always consult a physician."
    }

# -------------------------
# Drug Interaction Endpoint
# -------------------------
@app.post("/check/drug-interaction")
def drug_interaction(
    data: DrugInput,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    analysis = analyze_drug_interactions(data.drugs)

    return {
        "source": "Clinical Decision Support Engine",
        "analysis": analysis
    }

# -------------------------
# Registration Endpoint
# -------------------------

@app.post("/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(data.password)

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pw
    )

    db.add(user)
    db.commit()

    return {"message": "User registered successfully"}

# -------------------------
# Login Endpoint
# -------------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# History Endpoint
# ------------------------- 
@app.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    records = db.query(PredictionHistory).filter(
        PredictionHistory.username == current_user
    ).all()

    return records