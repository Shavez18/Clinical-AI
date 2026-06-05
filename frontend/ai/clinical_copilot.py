"""
Clinical AI Copilot Routing Engine.
Parses natural language questions, extracts clinical parameters,
routes to specialized medical engines, and returns professional markdown answers.
"""
import re
import streamlit as st
from ai.bmi_engine import analyze_bmi
from ai.body_fat_engine import analyze_body_fat
from ai.glucose_engine import analyze_glucose
from ai.cholesterol_engine import analyze_cholesterol
from ai.bp_engine import analyze_blood_pressure
from ai.risk_explainer import explain_latest_risk
from ai.symptom_assistant import explain_symptom_or_term
from ai.medication_assistant import explain_medication
from ai.lab_report_assistant import explain_lab_report
from ai.patient_summary_engine import generate_patient_profile
from ai.navigation_assistant import check_navigation_intent
from ai.llm_layer import get_llm_explanation

def safe_session_get(key: str, default_val=0.0):
    try:
        if key in st.session_state:
            return st.session_state[key]
    except Exception:
        pass
    return default_val

# ─── GUIDED ASSESSMENT PARAMETERS & CONFIGURATIONS ───
DIABETES_STEPS = [
    {
        "name": "Age",
        "prompt": "Step 1: What is your age?",
        "state_key": "adv_age",
        "type": "number",
        "explanation": "Age is a major non-modifiable risk factor for type 2 diabetes, as insulin sensitivity often decreases with age."
    },
    {
        "name": "Glucose",
        "prompt": "Step 2: What is your fasting glucose level (mg/dL)?",
        "state_key": "adv_gluc",
        "type": "number",
        "explanation": "Fasting blood glucose measures the concentration of sugar in your blood after fasting for 8+ hours. Normal is <100 mg/dL, prediabetes is 100-125, and diabetes is >=126."
    },
    {
        "name": "BMI",
        "prompt": "Step 3: What is your Body Mass Index (BMI)? (If you don't know, type your height and weight, e.g. 180cm, 80kg, and I'll calculate it!)",
        "state_key": "adv_bmi",
        "type": "number",
        "explanation": "BMI is a measure of weight relative to height. High BMI is strongly linked to insulin resistance and elevated diabetes risk."
    },
    {
        "name": "Blood Pressure",
        "prompt": "Step 4: What is your Diastolic Blood Pressure (mmHg)?",
        "state_key": "adv_bp",
        "type": "number",
        "explanation": "Diastolic blood pressure is the pressure in your arteries when your heart rests between beats. Normal is <80 mmHg."
    },
    {
        "name": "Pregnancy History",
        "prompt": "Step 5: Have you ever been pregnant? If yes, how many times? (If not applicable, type 'No' or '0')",
        "state_key": "adv_preg",
        "type": "text",
        "explanation": "Pregnancy history tracks gestational status. Multiple pregnancies are linked to metabolic adaptations and elevated risk for gestational diabetes."
    },
    {
        "name": "Family History",
        "prompt": "Step 6: Do you have a family history of diabetes? (Type 'Yes' or 'No')",
        "state_key": "adv_pedigree",
        "type": "text",
        "explanation": "A positive family history indicates potential genetic susceptibility to type 2 diabetes."
    },
    {
        "name": "Physical Activity",
        "prompt": "Step 7: How would you describe your physical activity level? (e.g. Active, Sedentary, or average hours per week)",
        "state_key": None,
        "type": "text",
        "explanation": "Regular physical activity increases insulin sensitivity and helps manage body weight, lowering diabetes risk."
    },
    {
        "name": "Diet Pattern",
        "prompt": "Step 8: Finally, what is your typical diet pattern? (e.g. Balanced, High Sugar, High Carb)",
        "state_key": None,
        "type": "text",
        "explanation": "Dietary habits directly impact blood glucose levels and insulin demand. High sugar diets stress pancreatic beta cells."
    }
]

HEART_STEPS = [
    {
        "name": "Age",
        "prompt": "Step 1: What is your age?",
        "state_key": "adv_h_age",
        "type": "number",
        "explanation": "Age is a key risk factor for coronary artery disease, as blood vessels naturally stiffen and accumulate plaque over time."
    },
    {
        "name": "Sex",
        "prompt": "Step 2: What is your biological sex? (Male/Female)",
        "state_key": "adv_h_sex",
        "type": "text",
        "explanation": "Biological sex influences cardiovascular risk profiles; historically, males have higher rates of early onset CAD."
    },
    {
        "name": "Resting Blood Pressure",
        "prompt": "Step 3: What is your Resting Blood Pressure (mmHg)? (e.g. 120/80)",
        "state_key": "adv_h_trestbps",
        "type": "number",
        "explanation": "Elevated resting blood pressure strains the myocardium and damages arterial linings over time."
    },
    {
        "name": "Cholesterol",
        "prompt": "Step 4: What is your Serum Cholesterol level (mg/dL)?",
        "state_key": "adv_h_chol",
        "type": "number",
        "explanation": "Serum cholesterol measures total lipids. High cholesterol leads to plaque accumulation (atherosclerosis) in coronary arteries."
    },
    {
        "name": "Heart Rate",
        "prompt": "Step 5: What is your typical resting heart rate or maximum heart rate? (e.g. 72 bpm)",
        "state_key": "adv_h_thalach",
        "type": "number",
        "explanation": "Heart rate ranges reflect cardiac reserve. Max heart rate achieved during exercise stress testing indicates physical fitness."
    },
    {
        "name": "Smoking Status",
        "prompt": "Step 6: Do you smoke? (Yes/No)",
        "state_key": None,
        "type": "text",
        "explanation": "Smoking introduces toxins that damage arterial walls, accelerate plaque buildup, and raise heart rate and BP."
    },
    {
        "name": "Diabetes History",
        "prompt": "Step 7: Do you have a history of diabetes? (Yes/No)",
        "state_key": "adv_h_fbs",
        "type": "text",
        "explanation": "Diabetes significantly increases cardiovascular risk by causing microvascular and macrovascular damage."
    },
    {
        "name": "Exercise Habits",
        "prompt": "Step 8: Finally, do you experience chest pain during physical exertion (Exercise Angina)? (Yes/No)",
        "state_key": "adv_h_exang",
        "type": "text",
        "explanation": "Exercise-induced angina indicates that physical exertion triggers cardiac ischemia due to narrowed coronary arteries."
    }
]

def parse_step_value(step_name: str, q: str, raw_query: str):
    # Parse numbers
    num_match = re.search(r'(\d+(?:\.\d+)?)', q)
    val = None
    if num_match:
        val = float(num_match.group(1))
        if step_name == "Age":
            val = int(val)
            
    # Specific step logic
    if step_name == "Sex":
        if "female" in q or "woman" in q or "women" in q:
            return 0, "Female"
        elif "male" in q or "man" in q or "men" in q:
            return 1, "Male"
    elif step_name in ["Pregnancy History", "Smoking Status", "Diabetes History", "Exercise Habits"]:
        if "no" in q or "never" in q or "nope" in q or "false" in q or "zero" in q or "none" in q:
            return 0, "No"
        elif "yes" in q or "yeah" in q or "yup" in q or "true" in q or "history" in q:
            if val is not None:
                return int(val), f"Yes ({int(val)} times)"
            return 1, "Yes"
            
    if val is not None:
        return val, str(val)
        
    # If no numbers, look for strings
    if len(q.strip()) > 0:
        return q.strip(), q.strip()
        
    return None, None

def explain_prediction_result(data: dict) -> str:
    p_type = data.get("type", "diabetes")
    risk = data.get("risk", 0.0)
    category = data.get("category", "LOW RISK")
    features = data.get("features", {})
    shap_vals = data.get("shap", {})
    
    risk_label = "Low Risk" if risk <= 30 else ("Medium Risk" if risk <= 70 else "High Risk")
    
    sorted_shap = sorted(shap_vals.items(), key=lambda x: abs(x[1]), reverse=True)
    factor_lines = []
    for feat, val in sorted_shap[:4]:
        sign = "+" if val >= 0 else "-"
        impact_pct = abs(val) * 100
        factor_lines.append(f"- **{feat}**: {sign}{impact_pct:.1f}%")
        
    factors_str = "\n".join(factor_lines)
    
    if p_type == "diabetes":
        intro_desc = (
            f"Based on our predictive models, your estimated risk of developing Diabetes is **{risk:.1f}%**, "
            f"which places you in the **{risk_label}** category. This calculation is derived using gradient boosted trees "
            f"calibrated against clinical parameters."
        )
        recs = (
            "- **Weight Management**: Maintain a healthy BMI (target range 18.5 - 24.9).\n"
            "- **Daily Walking**: Engage in at least 30 minutes of moderate physical activity daily.\n"
            "- **Reduce Sugary Drinks**: Limit simple sugars and processed carbohydrates.\n"
            "- **Regular Glucose Monitoring**: Monitor your fasting blood glucose levels regularly, especially if they exceed 100 mg/dL."
        )
    else:
        intro_desc = (
            f"Based on our predictive models, your estimated risk of Cardiovascular Disease is **{risk:.1f}%**, "
            f"which places you in the **{risk_label}** category. This calculation is derived using logistic risk pipelines "
            f"and clinical vitals."
        )
        recs = (
            "- **Reduce Sodium Intake**: Keep sodium intake under 2,000 mg per day to protect your arteries.\n"
            "- **Exercise Regularly**: Commit to 150 minutes of moderate aerobic exercise per week.\n"
            "- **Monitor Blood Pressure**: Keep a regular log of systolic and diastolic readings.\n"
            "- **Annual Cardiac Screening**: Schedule routine check-ups including lipid panel and resting ECG."
        )
        
    response = (
        f"### 📊 Prediction Result Analysis\n"
        f"**Risk Level:** **{risk_label}** ({risk:.1f}% Probability)\n\n"
        f"**Clinical Explanation:**\n"
        f"{intro_desc}\n\n"
        f"**Key Risk Factors (SHAP Feature Attribution):**\n"
        f"{factors_str}\n\n"
        f"**Personalized Healthcare Recommendations:**\n"
        f"{recs}\n\n"
        f"Please discuss these recommendations with a medical professional to establish a clinical treatment plan."
    )
    return response

def process_copilot_query(query: str, api_key: str = None) -> dict:
    """
    Main entry point for chatbot query processing.
    Returns a dict with:
        "response": Markdown response string
        "autofill": Dict containing parameter names and values if applicable (None if not)
        "navigation": Page key to navigate to if applicable (None if not)
        "show_summary": Boolean to render the summary export panel
    """
    q = query.lower()
    
    # Defaults
    result = {
        "response": "",
        "autofill": None,
        "navigation": None,
        "show_summary": False
    }

    # 0.5. PREDICTION RESULT ANALYSIS TRIGGER
    if "explain prediction" in q or "explain my prediction" in q or (q.strip() in ["yes", "y", "sure", "please", "ok", "explain"] and st.session_state.get("last_prediction_data")):
        data = st.session_state.get("last_prediction_data")
        if data:
            result["response"] = explain_prediction_result(data)
            return result
        else:
            result["response"] = (
                "### 📊 Prediction Explanation\n"
                "I don't have any recent prediction results to explain. "
                "Please complete a prediction form on the Diabetes or Cardiovascular page first!"
            )
            return result

    # 0.7. GUIDED ASSESSMENT STATE MACHINE
    # Detect intent to start guided assessment
    start_diabetes = any(word in q for word in ["predict diabetes", "diabetes predict", "diabetes assessment", "start diabetes", "diabetes screening"])
    start_heart = any(word in q for word in ["predict heart", "heart predict", "cardiac assessment", "start heart", "heart screening", "predict cardiovascular", "cardiovascular assessment"])
    
    nav_radio = safe_session_get("navigation_radio", "")
    if "start assessment" in q or "guided assessment" in q or "start guided" in q or "collect" in q or "proactively guide" in q:
        if "Diabetes" in nav_radio:
            start_diabetes = True
        elif "Cardiovascular" in nav_radio:
            start_heart = True
        else:
            result["response"] = (
                "### ⚕️ Clinical Assessment Guide\n"
                "I can guide you through a step-by-step biometric data collection assessment. Which module would you like to complete?\n\n"
                "- **Diabetes Intelligence Assessment** (Type `predict diabetes`)\n"
                "- **Cardiovascular Intelligence Assessment** (Type `predict heart`)"
            )
            return result
            
    if start_diabetes:
        st.session_state["guided_assessment"] = {
            "active": True,
            "module": "diabetes",
            "current_step": 0,
            "answers": {}
        }
        result["response"] = (
            "### 🩸 Diabetes Guided Assessment\n"
            "Great! I will help you collect the required parameters for the Diabetes Intelligence predictor.  \n"
            "Let's start with Step 1:\n\n"
            "**What is your age?**"
        )
        return result
        
    if start_heart:
        st.session_state["guided_assessment"] = {
            "active": True,
            "module": "heart",
            "current_step": 0,
            "answers": {}
        }
        result["response"] = (
            "### 🫀 Cardiovascular Guided Assessment\n"
            "Great! I will help you collect the required parameters for the Cardiovascular Risk predictor.  \n"
            "Let's start with Step 1:\n\n"
            "**What is your age?**"
        )
        return result

    # 1. GREETINGS & INTRO
    # Use word boundary checks for greetings to avoid matching substrings (e.g. "hi" in "history" or "thin")
    is_guided_active = False
    try:
        is_guided_active = st.session_state.get("guided_assessment", {}).get("active", False)
    except Exception:
        pass

    has_greeting = re.search(r'\b(hello|hi|hey|greetings)\b', q) or "who are you" in q or "what can you do" in q
    has_help = re.search(r'\bhelp\b', q)

    if has_greeting or (has_help and not is_guided_active):
        result["response"] = (
            "### ⚕️ ClinicalAI Assistant\n"
            "Welcome! I am your global floating **AI Clinical Copilot**. I assist with health calculations, interpret lab reports, explain risk parameters, and aid in system navigation.  \n\n"
            "**Here is what I can do for you:**\n"
            "1. **Health Calculators:** Enter height and weight (e.g. `180cm, 80kg`) for BMI, Ideal Weight, and Body Fat analysis.\n"
            "2. **Vitals Interpreter:** Enter BP (e.g. `BP 130/85`), Fasting Glucose (`glucose 110`), or Cholesterol (`cholesterol 210`) to check ranges.\n"
            "3. **Risk & Explainability:** Ask `explain my risk` or `why is my score high` to get SHAP-based explanations of predictive models.\n"
            "4. **Symptom & Drug Assistant:** Ask about symptoms (e.g. `headache`, `chest pain`) or drug profiles (e.g. `Metformin`, `Lisinopril`).\n"
            "5. **Lab Explanations:** Ask `explain CBC` or `explain liver function` for quick clinical references.\n"
            "6. **Patient Summary:** Type `summary` to view the comprehensive profile and download a printable report.\n"
            "7. **Navigation:** Tell me to `go to Diabetes` or `navigate to Cardiac` to auto-switch application tabs."
        )
        return result

    # 1.3. MEDICAL SAFETY GATEKEEPER
    safety_diagnostics = ["ecg", "resting ecg", "restecg", "st depression", "oldpeak", "vessels", "major vessels", "thalassemia", "thal"]
    is_asking_invention = any(word in q for word in ["estimate", "predict", "guess", "invent", "fake", "generate", "assume", "recommend"])
    has_diagnostic_kw = any(kw in q for kw in safety_diagnostics)
    is_asking_diagnosis = any(word in q for word in ["diagnose", "diagnosis", "what disease", "do i have", "my symptoms indicate"])
    is_asking_prescription = any(word in q for word in ["prescribe", "prescription", "write prescription", "give medicine", "get drug"])

    if (is_asking_invention and has_diagnostic_kw) or is_asking_diagnosis or is_asking_prescription:
        result["response"] = (
            "### ⚠️ Medical Safety Protocol\n"
            "As an AI Clinical Input Assistant, I cannot estimate, predict, or invent diagnostic measurements "
            "such as ECG findings, ST depression values, major blood vessel occlusion counts, or thalassemia status. "
            "I also cannot provide clinical diagnoses or write drug prescriptions.\n\n"
            "These values require direct clinical measurements (e.g., electrocardiograms, exercise stress tests, "
            "fluoroscopy, or genetic blood tests) and must be entered directly from your medical records. "
            "Please consult a licensed healthcare provider for clinical diagnosis and treatment plans."
        )
        return result

    # 1.35. PREDICT / CALCULATE BMI WITHOUT VALUES (Missing Value Assistant prompt)
    if "calculate bmi" in q or "don't know my bmi" in q or "don't know bmi" in q or "calculate my bmi" in q:
        height_match = re.search(r'(?:height|ht)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:cm|in|inch|inches)', q)
        weight_match = re.search(r'(?:weight|wt)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:kg|lbs|pounds)', q)
        if not (height_match and weight_match):
            result["response"] = (
                "### ⚖️ BMI Calculator\n"
                "No problem. Please enter:\n"
                "- Height (e.g. `180 cm`)\n"
                "- Weight (e.g. `80 kg`)\n\n"
                "I will calculate your BMI automatically."
            )
            return result

    # 1.38. PREVENTATIVE HEALTH TIPS
    if "health tips" in q or "show health tips" in q or "tips" in q:
        result["response"] = (
            "### 🍏 ClinicalAI Health Guidelines & Tips\n"
            "Here are some evidence-based preventative guidelines for metabolic and cardiac health:\n\n"
            "1. **Cardiovascular Health**:\n"
            "   - **AHA Recommendation**: Achieve at least 150 minutes of moderate-intensity exercise weekly.\n"
            "   - **Dietary Sodium**: Maintain sodium levels under 2,000 mg/day, prioritizing potassium-rich whole foods.\n"
            "2. **Metabolic Stability (Diabetes Prevention)**:\n"
            "   - **Refined Carbs**: Limit simple sugars to prevent spike loads on pancreatic beta cells.\n"
            "   - **Fiber Intake**: Aim for 25-30g of dietary fiber daily to stabilize glycemic response.\n"
            "3. **Regular Monitoring**:\n"
            "   - Screen fasting blood glucose annually if over age 35 or if BMI > 25.\n"
            "   - Track lipid panels (Cholesterol, HDL, LDL) regularly."
        )
        return result

    # 1.39. NAVIGATION ASSISTANT
    nav_page = check_navigation_intent(query)
    if nav_page:
        result["navigation"] = nav_page
        result["response"] = f"### 📡 Navigation Protocol\nInitializing redirect to **{nav_page}** page. Please wait..."
        return result

    # 1.40. GUIDED ASSESSMENT STATE MACHINE INTERCEPTION
    # If guided assessment is active, intercept input to process the step
    assessment = st.session_state.get("guided_assessment")
    if assessment and assessment.get("active"):
        module = assessment["module"]
        step_idx = assessment["current_step"]
        steps = DIABETES_STEPS if module == "diabetes" else HEART_STEPS
        current_step = steps[step_idx]
        
        # Check if user is asking for an explanation/don't know
        is_asking_unknown = any(phrase in q for phrase in ["don't know", "unknown", "i do not know", "no idea", "what does", "explain", "why", "help", "meaning of"])
        
        if is_asking_unknown:
            result["response"] = (
                f"### 💡 Clinical Information: {current_step['name']}\n"
                f"{current_step['explanation']}\n\n"
                f"Please enter your value for **{current_step['name']}** to continue, or type `skip` / `0` to default it."
            )
            return result
            
        # Check if user wants to skip
        if "skip" in q or q.strip() in ["default", "none"]:
            val = 0 if current_step["type"] == "number" else "Unknown"
            parsed_text = "Defaulted"
        else:
            # Check for calculator triggers within the steps (e.g. BMI height/weight calculation)
            height_match = re.search(r'(?:height|ht)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:cm|in|inch|inches)', q)
            weight_match = re.search(r'(?:weight|wt)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:kg|lbs|pounds)', q)
            
            if current_step["name"] == "BMI" and height_match and weight_match:
                try:
                    h_val = float(height_match.group(1) or height_match.group(2))
                    w_val = float(weight_match.group(1) or weight_match.group(2))
                    if h_val < 100 and ("in" in q or "inch" in q):
                        h_val = h_val * 2.54
                    if w_val > 150 and ("lb" in q or "pound" in q):
                        w_val = w_val * 0.453592
                    from utils.health_calculators import calculate_bmi
                    val = calculate_bmi(h_val, w_val)
                    parsed_text = f"{val:.1f} (calculated from {h_val}cm, {w_val}kg)"
                except Exception:
                    val, parsed_text = parse_step_value(current_step["name"], q, query)
            else:
                val, parsed_text = parse_step_value(current_step["name"], q, query)
                
        if val is None:
            result["response"] = (
                f"I couldn't parse a valid value for **{current_step['name']}**.  \n"
                f"Please enter your **{current_step['name']}**, or type `skip` to proceed."
            )
            return result
            
        assessment["answers"][current_step["name"]] = val
        
        # Autofill user's Streamlit session state keys directly!
        if current_step["state_key"]:
            if current_step["state_key"] == "adv_preg":
                st.session_state["adv_has_preg"] = "Yes" if val > 0 else "No"
                st.session_state["adv_preg"] = int(val)
            elif current_step["state_key"] == "adv_h_sex":
                st.session_state["adv_h_sex"] = (1, "Male") if val == 1 else (0, "Female")
            elif current_step["state_key"] == "adv_h_fbs":
                st.session_state["adv_h_fbs"] = (1, "True") if val == 1 else (0, "False")
            elif current_step["state_key"] == "adv_h_exang":
                st.session_state["adv_h_exang"] = (1, "Yes") if val == 1 else (0, "No")
            else:
                st.session_state[current_step["state_key"]] = val
                
        # Advance step
        assessment["current_step"] += 1
        next_step_idx = assessment["current_step"]
        
        if next_step_idx >= len(steps):
            assessment["active"] = False
            st.session_state["guided_assessment"] = assessment
            
            summary_lines = []
            for k, v in assessment["answers"].items():
                summary_lines.append(f"- **{k}**: {v}")
            summary_str = "\n".join(summary_lines)
            
            result["response"] = (
                f"### 🎉 Guided Assessment Completed!\n"
                f"We have collected all parameters for the **{module.title()}** module:\n\n"
                f"{summary_str}\n\n"
                f"I have successfully filled these parameters into the predictor input fields on the screen!  \n"
                f"Please click **'INITIALIZE INFERENCE ENGINE'** at the bottom of the page to run the prediction."
            )
            return result
            
        next_step = steps[next_step_idx]
        st.session_state["guided_assessment"] = assessment
        
        result["response"] = (
            f"Received value for **{current_step['name']}**: `{parsed_text}`.  \n"
            f"Moving to the next parameter...\n\n"
            f"**{next_step['prompt']}**"
        )
        return result

    # 2. BMI, BODY FAT & IDEAL WEIGHT CALCULATOR (with values)
    height_match = re.search(r'(?:height|ht)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:cm|in|inch|inches)', q)
    weight_match = re.search(r'(?:weight|wt)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:kg|lbs|pounds)', q)
    
    if height_match and weight_match:
        try:
            h_val = float(height_match.group(1) or height_match.group(2))
            w_val = float(weight_match.group(1) or weight_match.group(2))
            
            if h_val < 100 and ("in" in q or "inch" in q):
                h_val = h_val * 2.54
            if w_val > 150 and ("lb" in q or "pound" in q):
                w_val = w_val * 0.453592
                
            bmi_analysis = analyze_bmi(h_val, w_val)
            fat_analysis = analyze_body_fat(bmi_analysis["bmi"], 35, "Male")
            
            result["response"] = (
                f"### ⚖️ BMI & Body Composition Analysis\n"
                f"- **Exact BMI Score:** {bmi_analysis['bmi']}\n"
                f"- **Category:** **{bmi_analysis['category']}**\n"
                f"- **Healthy Range:** {bmi_analysis['healthy_range']}\n"
                f"- **Target Weight Range:** {bmi_analysis['target_weight_range']}\n"
                f"- **Weight Adjustment:** **{bmi_analysis['adjustment']}**\n"
                f"- **Clinical Impact:** {bmi_analysis['clinical_impact']}\n"
                f"- **Estimated Body Fat:** {fat_analysis['percentage']}% ({fat_analysis['category']})\n\n"
                f"*Interpretation:* {fat_analysis['interpretation']}\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_bmi": bmi_analysis["bmi"]}
            return result
        except Exception:
            pass

    # 3. VITALS: BLOOD PRESSURE INTERPRETER (with values)
    bp_match = re.search(r'(?:bp|blood pressure)?\s*(\d{2,3})\s*[\s/\\,-]\s*(\d{2,3})', q)
    if bp_match:
        try:
            systolic = float(bp_match.group(1))
            diastolic = float(bp_match.group(2))
            bp_analysis = analyze_blood_pressure(systolic, diastolic)
            
            result["response"] = (
                f"### 🫀 Blood Pressure Analysis\n"
                f"The clinical classification for **{int(systolic)}/{int(diastolic)} mmHg** is:\n"
                f"**{bp_analysis['category']}**\n\n"
                f"- *Physiological Impact:* {bp_analysis['interpretation']}\n"
                f"- *Clinical Guidelines:* {bp_analysis['guidelines'][0]}\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {
                "adv_bp": diastolic,
                "adv_h_trestbps": systolic
            }
            return result
        except Exception:
            pass

    # 4. VITALS: GLUCOSE INTERPRETER (with values)
    gluc_match = re.search(r'(?:glucose|sugar)\s*(?:is|are|value|values|of|level|levels|currently|at|if|it|reading|readings|to|set|be|\s)*\s*(\d{2,3})', q)
    if gluc_match:
        try:
            val = float(gluc_match.group(1))
            gluc_analysis = analyze_glucose(val)
            
            result["response"] = (
                f"### 🩸 Blood Glucose Interpretation\n"
                f"Fasting glucose value of **{val} mg/dL** is categorized as:\n"
                f"**{gluc_analysis['category']}**\n\n"
                f"- *Clinical Meaning:* {gluc_analysis['interpretation']}\n\n"
                f"{gluc_analysis['visual_html']}\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_gluc": val}
            return result
        except Exception:
            pass

    # 5. VITALS: CHOLESTEROL INTERPRETER (with values)
    chol_match = re.search(r'(?:cholesterol|chol|lipids)\s*(?:is|are|value|values|of|level|levels|currently|at|if|it|reading|readings|to|set|be|\s)*\s*(\d{2,3})', q)
    if chol_match:
        try:
            val = float(chol_match.group(1))
            ldl = round(val * 0.6)
            hdl = 50.0
            trig = 145.0
            
            chol_analysis = analyze_cholesterol(val, ldl, hdl, trig)
            
            result["response"] = (
                f"### 🍔 Lipid Panel Analysis (Simulated Panel)\n"
                f"Based on a Total Cholesterol of **{val} mg/dL**:\n\n"
                f"{chol_analysis['grid_html']}\n"
                f"- **Dietary Recommendations:**\n"
                f"  - {chr(10).join([f'  - {r}' for r in chol_analysis['recommendations']])}\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_h_chol": val}
            return result
        except Exception:
            pass

    # 6. VITALS: MAX HEART RATE CALCULATOR
    if any(phrase in q for phrase in ["max heart rate", "maximum heart rate", "mhr"]):
        try:
            age_match = re.search(r'(?:age|am|is)\s*(\d{1,3})', q)
            if age_match:
                age = int(age_match.group(1))
            else:
                age = int(safe_session_get("adv_age") or safe_session_get("adv_h_age") or safe_session_get("adv_s_age") or 30)
                if age == 0: age = 30
                
            haskell_fox = round(220 - age)
            tanaka = round(208 - 0.7 * age)
            
            result["response"] = (
                f"### 🫀 Maximum Heart Rate (MHR) Calculation\n"
                f"Based on an age of **{age}** years:\n\n"
                f"- **Haskell & Fox Formula:** **{haskell_fox} bpm** (Standard clinical estimate: 220 - age)\n"
                f"- **Tanaka Formula:** **{tanaka} bpm** (Research-calibrated: 208 - 0.7 * age)\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_h_thalach": haskell_fox}
            return result
        except Exception:
            pass

    # 7. VITALS: IDEAL WEIGHT CALCULATOR
    if any(phrase in q for phrase in ["ideal weight", "ideal body weight", "ibw"]):
        try:
            height_match = re.search(r'(?:height|ht)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:cm|in|inch|inches)', q)
            if height_match:
                height = float(height_match.group(1) or height_match.group(2))
                if height < 100 and ("in" in q or "inch" in q):
                    height = height * 2.54
            else:
                height = 175.0
                
            gender_match = re.search(r'\b(male|female|men|women|man|woman)\b', q)
            if gender_match:
                g_str = gender_match.group(1).lower()
                gender = "female" if g_str in ["female", "women", "woman"] else "male"
            else:
                gender = "female" if safe_session_get("adv_h_sex") == 0 else "male"
                
            from utils.health_calculators import calculate_ideal_weight_devine, calculate_ideal_weight_robinson
            devine_val = calculate_ideal_weight_devine(height, gender)
            robinson_val = calculate_ideal_weight_robinson(height, gender)
            
            result["response"] = (
                f"### ⚖️ Ideal Body Weight (IBW) Analysis\n"
                f"Based on a height of **{height:.1f} cm** and biological profile **{gender.title()}**:\n\n"
                f"- **Devine Formula (1974):** **{devine_val} kg** (Clinical standard)\n"
                f"- **Robinson Formula (1983):** **{robinson_val} kg** (Research reference)\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_ideal_weight": devine_val}
            return result
        except Exception:
            pass

    # 8. VITALS: BODY FAT ESTIMATOR
    if any(phrase in q for phrase in ["body fat", "fat percentage", "bf%"]):
        try:
            bmi_match = re.search(r'(?:bmi)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)', q)
            if bmi_match:
                bmi = float(bmi_match.group(1))
            else:
                bmi = float(safe_session_get("adv_bmi", 0.0))
                
            height_match = re.search(r'(?:height|ht)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:cm|in|inch|inches)', q)
            weight_match = re.search(r'(?:weight|wt)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:kg|lbs|pounds)', q)
            if bmi == 0 and height_match and weight_match:
                h_val = float(height_match.group(1) or height_match.group(2))
                w_val = float(weight_match.group(1) or weight_match.group(2))
                if h_val < 100 and ("in" in q or "inch" in q):
                    h_val = h_val * 2.54
                if w_val > 150 and ("lb" in q or "pound" in q):
                    w_val = w_val * 0.453592
                from utils.health_calculators import calculate_bmi
                bmi = calculate_bmi(h_val, w_val)
                
            if bmi <= 0:
                result["response"] = (
                    "### 🧬 Body Fat Estimation\n"
                    "I need your BMI to estimate your body fat percentage. "
                    "Please specify your BMI (e.g. `BMI 24.5`) or your height and weight (e.g. `180cm, 80kg`)."
                )
                return result
                
            age_match = re.search(r'(?:age|am|is)\s*(\d{1,3})', q)
            if age_match:
                age = int(age_match.group(1))
            else:
                age = int(safe_session_get("adv_age") or safe_session_get("adv_h_age") or safe_session_get("adv_s_age") or 30)
                if age == 0: age = 30
                
            gender_match = re.search(r'\b(male|female|men|women|man|woman)\b', q)
            if gender_match:
                g_str = gender_match.group(1).lower()
                gender = "Female" if g_str in ["female", "women", "woman"] else "Male"
            else:
                gender = "Female" if safe_session_get("adv_h_sex") == 0 else "Male"
                
            fat_analysis = analyze_body_fat(bmi, age, gender)
            
            result["response"] = (
                f"### 🧬 Body Fat Estimation\n"
                f"Based on a BMI of **{bmi}**, age **{age}** years, and gender **{gender}**:\n\n"
                f"- **Estimated Body Fat:** **{fat_analysis['percentage']}%** (Deurenberg Formula)\n"
                f"- **Category:** **{fat_analysis['category']}**\n\n"
                f"- *Clinical Meaning:* {fat_analysis['interpretation']}\n\n"
                f"Would you like me to autofill this into the predictor?"
            )
            result["autofill"] = {"adv_body_fat": fat_analysis['percentage']}
            return result
        except Exception:
            pass

    # 9. CHECK MY METRIC (What is my [metric]? / check my [metric])
    if any(phrase in q for phrase in ["my", "current", "value of", "check"]):
        if "glucose" in q or "sugar" in q:
            gluc_val = safe_session_get("adv_gluc", 0.0)
            if gluc_val > 0:
                gluc_analysis = analyze_glucose(gluc_val)
                result["response"] = (
                    f"### 🩸 Current Fasting Glucose\n"
                    f"Your current Fasting Glucose is set to **{gluc_val} mg/dL**.\n\n"
                    f"**Classification:** **{gluc_analysis['category']}**\n"
                    f"- *Interpretation:* {gluc_analysis['interpretation']}\n\n"
                    f"{gluc_analysis['visual_html']}"
                )
            else:
                result["response"] = (
                    "### 🩸 Current Fasting Glucose\n"
                    "Your Fasting Glucose is currently not set (or is 0 mg/dL).\n\n"
                    "You can enter a glucose value on the **Diabetes Intelligence** page or type a value here (e.g. `glucose 110`) to check it."
                )
            return result
            
        elif "blood pressure" in q or "bp" in q or "diastolic" in q or "systolic" in q or "trestbps" in q:
            systolic = safe_session_get("adv_h_trestbps", 0.0)
            diastolic = safe_session_get("adv_bp", 0.0)
            if systolic > 0 or diastolic > 0:
                if systolic == 0: systolic = 120.0
                if diastolic == 0: diastolic = 80.0
                bp_analysis = analyze_blood_pressure(systolic, diastolic)
                result["response"] = (
                    f"### 🫀 Current Blood Pressure\n"
                    f"Your current Blood Pressure is set to **{int(systolic)}/{int(diastolic)} mmHg**.\n\n"
                    f"**Classification:** **{bp_analysis['category']}**\n"
                    f"- *Interpretation:* {bp_analysis['interpretation']}\n"
                    f"- *Guidelines:* {bp_analysis['guidelines'][0]}\n\n"
                    f"{bp_analysis['visual_html']}"
                )
            else:
                result["response"] = (
                    "### 🫀 Current Blood Pressure\n"
                    "Your Blood Pressure is currently not set (or is 0 mmHg).\n\n"
                    "You can enter BP values on the **Cardiovascular Intelligence** page or type a value here (e.g. `120/80`) to check it."
                )
            return result
            
        elif "cholesterol" in q or "chol" in q or "lipids" in q:
            chol_val = safe_session_get("adv_h_chol", 0.0)
            if chol_val > 0:
                ldl = round(chol_val * 0.6)
                hdl = 50.0
                trig = 145.0
                chol_analysis = analyze_cholesterol(chol_val, ldl, hdl, trig)
                result["response"] = (
                    f"### 🍔 Current Cholesterol\n"
                    f"Your current Total Cholesterol is set to **{chol_val} mg/dL**.\n\n"
                    f"{chol_analysis['grid_html']}"
                )
            else:
                result["response"] = (
                    "### 🍔 Current Cholesterol\n"
                    "Your Serum Cholesterol is currently not set (or is 0 mg/dL).\n\n"
                    "You can enter cholesterol values on the **Cardiovascular Intelligence** page or type a value here (e.g. `cholesterol 220`) to check it."
                )
            return result
            
        elif "bmi" in q or "body mass index" in q:
            bmi_val = safe_session_get("adv_bmi", 0.0)
            if bmi_val > 0:
                height = safe_session_get("adv_age", 175.0)
                weight = bmi_val * ((height/100.0)**2)
                bmi_analysis = analyze_bmi(height, weight)
                result["response"] = (
                    f"### ⚖️ Current BMI\n"
                    f"Your current BMI is set to **{bmi_val}**.\n\n"
                    f"**Classification:** **{bmi_analysis['category']}**\n"
                    f"- *Clinical Impact:* {bmi_analysis['clinical_impact']}\n"
                    f"- *Target Range:* {bmi_analysis['target_weight_range']}"
                )
            else:
                result["response"] = (
                    "### ⚖️ Current BMI\n"
                    "Your BMI is currently not set (or is 0).\n\n"
                    "You can enter your height and weight here (e.g. `180cm, 80kg`) or on the **Diabetes Intelligence** page to calculate it."
                )
            return result

    # 10. INPUT EXPLANATIONS (For 12 predictor fields)
    explanation_map = {
        "bmi": ("BMI", "Body Mass Index (BMI) is a measure of body fatness calculated as weight in kilograms divided by height in meters squared (kg/m²). It screens for weight categories (Underweight, Normal, Overweight, Obese) linked to metabolic and cardiovascular risks."),
        "glucose": ("Glucose", "Fasting plasma glucose concentration (mg/dL) measures glucose in the blood after an 8-hour fast. It is a critical diagnostic marker: normal is <100 mg/dL, prediabetes is 100-125 mg/dL, and diabetes is >=126 mg/dL."),
        "blood pressure": ("Blood Pressure", "Blood pressure is the force of blood against artery walls, recorded as Systolic (pressure during heartbeats, normal <120 mmHg) and Diastolic (pressure between beats, normal <80 mmHg). High blood pressure strains the cardiovascular system."),
        "chest pain type": ("Chest Pain Type", "Chest Pain Type classifies chest discomfort: Typical Angina (exertion-induced chest pain), Atypical Angina (exertion-linked atypical presentation), Non-anginal pain (non-cardiac pain, e.g., musculoskeletal), or Asymptomatic (no pain, often seen in diabetic neuropathy)."),
        "resting ecg": ("Resting ECG", "Resting ECG records heart electrical activity at rest. It screens for abnormalities like ST-T wave changes (ischemia indicators) or Left Ventricular Hypertrophy (LVH, thickened heart walls due to high blood pressure)."),
        "st depression": ("ST Depression", "ST Depression is the downward shift of the ST segment during exercise stress testing relative to rest. It is a diagnostic marker indicating myocardial ischemia, where the heart muscle receives insufficient oxygen-rich blood."),
        "st slope": ("ST Slope", "ST Slope describes the recovery angle of the ST segment during peak exercise on a stress test. It is classified as Upsloping (normal recovery), Flat (borderline ischemia), or Downsloping (strongly indicating coronary artery disease)."),
        "major vessels": ("Major Vessels", "Major Vessels (0-3) represents the number of major coronary arteries showing occlusion or narrowing under fluoroscopic examination. A higher score indicates severe blockages and reduced cardiac blood supply."),
        "thalassemia": ("Thalassemia", "Thalassemia is an inherited blood disorder. In cardiac models, it tracks coronary perfusion status: Normal, Fixed Defect (permanent tissue damage from a past infarction), or Reversible Defect (active, treatable ischemia)."),
        "exercise angina": ("Exercise Angina", "Exercise-Induced Angina indicates whether physical exertion triggers chest pain (1 = Yes, 0 = No). Its presence is a strong clinical indicator of significant coronary artery stenosis."),
        "cholesterol": ("Cholesterol", "Serum Cholesterol measures total lipids in your blood, including LDL ('bad' cholesterol), HDL ('good' cholesterol), and Triglycerides. High cholesterol levels cause plaque buildup in coronary arteries (atherosclerosis)."),
        "pregnancy history": ("Pregnancy History", "Pregnancy history tracks the number of times a female patient has been pregnant. Multiple pregnancies are linked to metabolic adaptations and elevated risk for gestational diabetes and subsequent Type 2 Diabetes.")
    }

    matched_field = None
    if any(phrase in q for phrase in ["explain", "what is", "tell me about", "meaning of", "definition of", "understand", "what does"]):
        if "resting ecg" in q or "restecg" in q or "ecg" in q or "electrocardiogram" in q:
            matched_field = "resting ecg"
        elif "st depression" in q or "oldpeak" in q or "st-depression" in q:
            matched_field = "st depression"
        elif "st slope" in q or "slope" in q:
            matched_field = "st slope"
        elif "major vessel" in q or "ca" in q or "vessels" in q:
            matched_field = "major vessels"
        elif "thalassemia" in q or "thal" in q:
            matched_field = "thalassemia"
        elif "exercise angina" in q or "exang" in q or "exercise induced angina" in q:
            matched_field = "exercise angina"
        elif "pregnancy" in q or "pregnancy history" in q or "pregnancies" in q:
            matched_field = "pregnancy history"
        elif "bmi" in q or "body mass index" in q:
            matched_field = "bmi"
        elif "glucose" in q or "sugar" in q:
            matched_field = "glucose"
        elif "blood pressure" in q or "bp" in q:
            matched_field = "blood pressure"
        elif "chest pain" in q or "cp" in q:
            matched_field = "chest pain type"
        elif "cholesterol" in q or "chol" in q or "lipids" in q:
            matched_field = "cholesterol"

    if matched_field:
        field_name, local_desc = explanation_map[matched_field]
        llm_response = get_llm_explanation(query, context=f"Predictor parameter explanations. Field: {field_name}. Local base explanation: {local_desc}", api_key=api_key)
        if llm_response:
            result["response"] = f"### 🧠 Clinical Assistant: {field_name}\n{llm_response}"
        else:
            result["response"] = (
                f"### 🧠 Clinical Assistant: {field_name}\n"
                f"{local_desc}\n\n"
                f"*Note: Gemini LLM layer is currently not configured or inactive. You can configure a free Gemini API Key in the settings below to enable real-time educational expansions.*"
            )
        return result

    # 12. PATIENT SUMMARY ENGINE
    if any(word in q for word in ["summary", "patient summary", "profile", "export", "report"]):
        result["show_summary"] = True
        result["response"] = (
            "### 📋 Patient Summary compiled.\n"
            "I have parsed the telemetry logs and compiled a comprehensive Clinical Summary Report below. "
            "You can review active risk scores and download the report as a printable HTML document."
        )
        return result

    # 13. RISK EXPLANABILITY ASSISTANT
    if any(word in q for word in ["explain risk", "explain my risk", "why is my risk", "why is my score", "shap", "factors"]):
        result["response"] = explain_latest_risk()
        return result

    # 14. DRUG INFORMATION ASSISTANT
    med_response = explain_medication(query)
    if "Medication Profile" in med_response:
        result["response"] = med_response
        return result

    # 15. LAB REPORT ASSISTANT
    lab_response = explain_lab_report(query)
    if "Reference Standards" in lab_response:
        result["response"] = lab_response
        return result

    # 16. SYMPTOM ASSISTANT
    symptom_response = explain_symptom_or_term(query)
    if "🔍" in symptom_response:
        result["response"] = symptom_response
        return result

    # 17. GENERAL HEALTH / CHAT FALLBACK
    if api_key and api_key.strip():
        llm_response = get_llm_explanation(query, context="General health education, predictor field explanations, or clinical telemetry guidance.", api_key=api_key)
        if llm_response:
            result["response"] = f"### ⚕️ ClinicalAI Assistant\n{llm_response}"
            return result

    result["response"] = (
        "### ⚕️ ClinicalAI General Inquiry Response\n"
        "Your query was received, but no specific biometric values or known drugs/symptoms were matching standard triggers.  \n\n"
        "**Are you trying to:**\n"
        "- Calculate BMI and body fat? Specify your height and weight (e.g. `175 cm, 70 kg`).\n"
        "- Calculate Ideal Weight? Ask `calculate my ideal weight`.\n"
        "- Calculate Max Heart Rate? Ask `calculate my max heart rate`.\n"
        "- Interpret blood pressure? Specify your reading (e.g. `120/80 mmHg`).\n"
        "- Explain a drug or symptom? Specify the term (e.g. `tell me about Metformin` or `explain Angina`).\n"
        "- Navigate around the platform? Ask `go to Cardiovascular page`.\n\n"
        "For urgent safety concerns: If you are experiencing chest pain, severe dyspnea, or sudden neurologic weakness, please seek immediate emergency care."
    )
    return result
