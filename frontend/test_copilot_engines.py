"""
Verification script for Clinical AI Copilot Engines and Calculators.
"""
import sys
import os

# Add frontend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.health_calculators import calculate_bmi, calculate_bmi_range, estimate_body_fat
from utils.health_ranges import interpret_glucose, interpret_blood_pressure, interpret_cholesterol
from ai.bmi_engine import analyze_bmi
from ai.body_fat_engine import analyze_body_fat
from ai.glucose_engine import analyze_glucose
from ai.bp_engine import analyze_blood_pressure
from ai.cholesterol_engine import analyze_cholesterol
from ai.clinical_copilot import process_copilot_query

def run_tests():
    print("==================================================")
    print("RUNNING CLINICAL CO-PILOT UNIT TESTS & VERIFICATIONS")
    print("==================================================")
    
    errors = 0
    
    # 1. Test BMI Calculator
    print("Testing BMI calculations...")
    bmi = calculate_bmi(180, 80)
    if bmi != 24.7:
        print(f"[FAIL] Error: BMI for 180cm, 80kg should be 24.7, got {bmi}")
        errors += 1
    else:
        print("[PASS] BMI calculation correct (24.7)")
        
    min_w, max_w = calculate_bmi_range(180)
    if int(min_w) != 59 or int(max_w) != 80:
        print(f"[FAIL] Error: BMI range for 180cm should be ~59.9 to 80.6, got {min_w} to {max_w}")
        errors += 1
    else:
        print(f"[PASS] BMI healthy range correct ({min_w}kg - {max_w}kg)")

    # 2. Test Body Fat Calculator
    print("\nTesting Body Fat estimation...")
    fat = estimate_body_fat(24.7, 30, "Male")
    if fat != 20.3:
        print(f"[FAIL] Error: Body Fat for BMI 24.7, age 30, Male should be 20.3, got {fat}")
        errors += 1
    else:
        print("[PASS] Body Fat calculation correct (20.3%)")
        
    fat_analysis = analyze_body_fat(24.7, 30, "Male")
    if fat_analysis["category"] != "Acceptable / Average":
        print(f"[FAIL] Error: Body Fat category should be 'Acceptable / Average', got '{fat_analysis['category']}'")
        errors += 1
    else:
        print(f"[PASS] Body Fat category correct ({fat_analysis['category']})")

    # 3. Test Glucose Interpreter
    print("\nTesting Glucose interpretation...")
    gluc_normal = interpret_glucose(90)
    if gluc_normal["category"] != "Normal":
        print(f"[FAIL] Error: Glucose 90 should be 'Normal', got {gluc_normal['category']}")
        errors += 1
    else:
        print("[PASS] Glucose 90 classified correctly as 'Normal'")
        
    gluc_diab = interpret_glucose(135)
    if gluc_diab["category"] != "Diabetes Range":
        print(f"[FAIL] Error: Glucose 135 should be 'Diabetes Range', got {gluc_diab['category']}")
        errors += 1
    else:
        print("[PASS] Glucose 135 classified correctly as 'Diabetes Range'")

    # 4. Test Blood Pressure Interpreter
    print("\nTesting Blood Pressure interpretation...")
    bp_stage2 = interpret_blood_pressure(145, 95)
    if bp_stage2["category"] != "Stage 2 Hypertension":
        print(f"[FAIL] Error: BP 145/95 should be 'Stage 2 Hypertension', got {bp_stage2['category']}")
        errors += 1
    else:
        print("[PASS] BP 145/95 classified correctly as 'Stage 2 Hypertension'")
        
    bp_elevated = interpret_blood_pressure(125, 75)
    if bp_elevated["category"] != "Elevated Blood Pressure":
        print(f"[FAIL] Error: BP 125/75 should be 'Elevated Blood Pressure', got {bp_elevated['category']}")
        errors += 1
    else:
        print("[PASS] BP 125/75 classified correctly as 'Elevated Blood Pressure'")

    # 5. Test Cholesterol Interpreter
    print("\nTesting Cholesterol interpretation...")
    chol_res = interpret_cholesterol(250, 165, 35, 180, "Male")
    if chol_res["total"]["category"] != "High":
        print(f"[FAIL] Error: Total Chol 250 should be 'High', got {chol_res['total']['category']}")
        errors += 1
    else:
        print("[PASS] Total Cholesterol 250 classified correctly as 'High'")
    if chol_res["hdl"]["category"] != "Low (Unfavorable)":
        print(f"[FAIL] Error: HDL 35 for Male should be 'Low (Unfavorable)', got {chol_res['hdl']['category']}")
        errors += 1
    else:
        print("[PASS] HDL 35 classified correctly as 'Low (Unfavorable)'")

    # 6. Test Query Routing Engine
    print("\nTesting Copilot Query router...")
    
    # User's query (BMI calculation check)
    user_q = process_copilot_query("my height is 172 cm and my weight is 48 kg what is my bmi")
    if "BMI" not in user_q["response"] or user_q["autofill"] is None or user_q["autofill"].get("adv_bmi") is None:
        print("[FAIL] Error: Query 'my height is 172 cm and my weight is 48 kg what is my bmi' failed to calculate BMI or produce autofill.")
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in user_q["response"]:
        print("[FAIL] Error: BMI calculator did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] User query calculated BMI and offered correct autofill prompt.")

    # Vitals with values
    bp_q = process_copilot_query("my bp is 135/95")
    if "Blood Pressure Analysis" not in bp_q["response"] or bp_q["autofill"] is None or bp_q["autofill"].get("adv_bp") is None:
        print("[FAIL] Error: Query 'my bp is 135/95' failed to parse and analyze Blood Pressure.")
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in bp_q["response"]:
        print("[FAIL] Error: BP interpreter did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Query 'my bp is 135/95' parsed BP and offered correct autofill prompt.")

    glucose_q = process_copilot_query("what is my glucose if it is 135 mg/dL?")
    if "Blood Glucose Interpretation" not in glucose_q["response"] or glucose_q["autofill"] is None or glucose_q["autofill"].get("adv_gluc") is None:
        print("[FAIL] Error: Query 'what is my glucose if it is 135 mg/dL?' failed to parse and analyze glucose.")
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in glucose_q["response"]:
        print("[FAIL] Error: Glucose interpreter did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Query 'what is my glucose if it is 135 mg/dL?' parsed glucose and offered correct autofill prompt.")

    cholesterol_q = process_copilot_query("check my cholesterol 250")
    if "Lipid Panel Analysis" not in cholesterol_q["response"] or cholesterol_q["autofill"] is None or cholesterol_q["autofill"].get("adv_h_chol") is None:
        print("[FAIL] Error: Query 'check my cholesterol 250' failed to parse and analyze cholesterol.")
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in cholesterol_q["response"]:
        print("[FAIL] Error: Cholesterol interpreter did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Query 'check my cholesterol 250' parsed cholesterol and offered correct autofill prompt.")

    # 6.2 New Calculators (MHR, Ideal Weight, Body Fat)
    mhr_q = process_copilot_query("calculate my max heart rate if my age is 40")
    if "Maximum Heart Rate" not in mhr_q["response"] or mhr_q["autofill"] is None or mhr_q["autofill"].get("adv_h_thalach") != 180:
        print("[FAIL] Error: Max Heart Rate calculation failed or returned incorrect thalach. Got:", mhr_q["autofill"])
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in mhr_q["response"]:
        print("[FAIL] Error: Max Heart Rate did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Max Heart Rate calculation and autofill prompt verified.")

    iw_q = process_copilot_query("calculate my ideal body weight if height is 180 cm and male")
    if "Ideal Body Weight" not in iw_q["response"] or iw_q["autofill"] is None or iw_q["autofill"].get("adv_ideal_weight") is None:
        print("[FAIL] Error: Ideal Weight calculation failed. Got:", iw_q["autofill"])
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in iw_q["response"]:
        print("[FAIL] Error: Ideal Weight did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Ideal Body Weight calculation and autofill prompt verified.")

    bf_q = process_copilot_query("estimate my body fat percentage if bmi is 22.0, age 30, and male")
    if "Body Fat Estimation" not in bf_q["response"] or bf_q["autofill"] is None or bf_q["autofill"].get("adv_body_fat") is None:
        print("[FAIL] Error: Body Fat estimation failed. Got:", bf_q["autofill"])
        errors += 1
    elif "Would you like me to autofill this into the predictor?" not in bf_q["response"]:
        print("[FAIL] Error: Body Fat did not offer the exact required autofill string.")
        errors += 1
    else:
        print("[PASS] Body Fat estimation and autofill prompt verified.")

    # 6.3 Input Explanations (12 fields)
    field_q1 = process_copilot_query("explain resting ecg")
    if "Resting ECG" not in field_q1["response"] or "LVH" not in field_q1["response"]:
        print("[FAIL] Error: Failed to explain Resting ECG.")
        errors += 1
    else:
        print("[PASS] Resting ECG explanation verified.")

    field_q2 = process_copilot_query("what is st depression?")
    if "ST Depression" not in field_q2["response"] or "ischemia" not in field_q2["response"]:
        print("[FAIL] Error: Failed to explain ST Depression.")
        errors += 1
    else:
        print("[PASS] ST Depression explanation verified.")

    field_q3 = process_copilot_query("explain pregnancy history")
    if "Pregnancy History" not in field_q3["response"] or "gestational" not in field_q3["response"]:
        print("[FAIL] Error: Failed to explain Pregnancy History.")
        errors += 1
    else:
        print("[PASS] Pregnancy History explanation verified.")

    # 6.4 Medical Safety Protocol Refusals
    safety_q1 = process_copilot_query("predict my resting ecg")
    if "Medical Safety Protocol" not in safety_q1["response"] or "cannot estimate, predict, or invent" not in safety_q1["response"]:
        print("[FAIL] Error: Failed to enforce safety gatekeeper on diagnostic prediction.")
        errors += 1
    else:
        print("[PASS] Medical Safety Gatekeeper blocked ECG prediction correctly.")

    safety_q2 = process_copilot_query("diagnose my chest pain")
    if "Medical Safety Protocol" not in safety_q2["response"] or "cannot provide clinical diagnoses" not in safety_q2["response"]:
        print("[FAIL] Error: Failed to enforce safety gatekeeper on clinical diagnosis.")
        errors += 1
    else:
        print("[PASS] Medical Safety Gatekeeper blocked clinical diagnosis correctly.")

    safety_q3 = process_copilot_query("prescribe metformin")
    if "Medical Safety Protocol" not in safety_q3["response"] or "cannot provide clinical diagnoses or write drug prescriptions" not in safety_q3["response"]:
        print("[FAIL] Error: Failed to enforce safety gatekeeper on drug prescriptions.")
        errors += 1
    else:
        print("[PASS] Medical Safety Gatekeeper blocked drug prescription correctly.")

    # Original routing cases
    q1 = process_copilot_query("My height is 180cm, weight is 80kg")
    if "BMI" not in q1["response"] or q1["autofill"] is None:
        print("[FAIL] Error: Query 'My height is 180cm, weight is 80kg' failed to route to BMI analyzer or produce autofill.")
        errors += 1
    else:
        print("[PASS] Query 'My height is 180cm, weight is 80kg' routed correctly.")
        
    q2 = process_copilot_query("Tell me about Metformin")
    if "Metformin" not in q2["response"] or "Biguanide" not in q2["response"]:
        print("[FAIL] Error: Query 'Tell me about Metformin' failed to produce medication profile.")
        errors += 1
    else:
        print("[PASS] Query 'Tell me about Metformin' returned correct profile details.")
        
    q3 = process_copilot_query("go to diabetes page")
    if q3["navigation"] is None or "Diabetes" not in q3["navigation"]:
        print(f"[FAIL] Error: Query 'go to diabetes page' failed to map navigation. Got: {q3['navigation']}")
        errors += 1
    else:
        print("[PASS] Query 'go to diabetes page' mapped correctly to navigation (Diabetes Intelligence)")

    # Test Session State Lookups (No values provided)
    # 1. Fallback when 0/not set
    bmi_lookup_empty = process_copilot_query("what is my bmi")
    if "not set" not in bmi_lookup_empty["response"] and "0" not in bmi_lookup_empty["response"]:
        print("[FAIL] Error: Empty BMI session state did not return correct fallback message.")
        errors += 1
    else:
        print("[PASS] Empty BMI session state fallback message verified.")

    # 2. Mocking/setting session state keys to verify lookup returns values
    import streamlit as st
    try:
        st.session_state = {}
        st.session_state["adv_bmi"] = 24.7
        st.session_state["adv_gluc"] = 110.0
        st.session_state["adv_h_trestbps"] = 130.0
        st.session_state["adv_bp"] = 85.0
        st.session_state["adv_h_chol"] = 210.0
        
        # Test lookups with session state set
        bmi_lookup_val = process_copilot_query("what is my bmi")
        if "24.7" not in bmi_lookup_val["response"]:
            print("[FAIL] Error: BMI session state lookup did not return correct mock value.")
            errors += 1
        else:
            print("[PASS] BMI session state lookup verified with mock value.")

        gluc_lookup_val = process_copilot_query("what is my glucose")
        if "110" not in gluc_lookup_val["response"]:
            print("[FAIL] Error: Glucose session state lookup did not return correct mock value.")
            errors += 1
        else:
            print("[PASS] Glucose session state lookup verified with mock value.")
            
        # 3. Test Guided Assessment State Machine
        print("\nTesting Guided Assessment State Machine...")
        st.session_state = {}
        st.session_state["navigation_radio"] = "🩸  Diabetes Intelligence"
        st.session_state["guided_assessment"] = {
            "active": False,
            "module": None,
            "current_step": 0,
            "answers": {}
        }
        
        start_q = process_copilot_query("start assessment")
        if not st.session_state["guided_assessment"]["active"] or st.session_state["guided_assessment"]["module"] != "diabetes":
            print("[FAIL] Error: Failed to initialize guided assessment for diabetes.")
            errors += 1
        else:
            print("[PASS] Guided assessment initialized successfully (Module: Diabetes).")
            
        ans_q = process_copilot_query("35 years old")
        if st.session_state["guided_assessment"]["answers"].get("Age") != 35 or st.session_state["guided_assessment"]["current_step"] != 1:
            print(f"[FAIL] Error: Guided assessment did not store Age (35) or advance step: {st.session_state['guided_assessment']}")
            errors += 1
        else:
            print("[PASS] Guided assessment age parsing and step progression verified.")
            
        expl_q = process_copilot_query("i don't know")
        if "Fasting blood glucose measures" not in expl_q["response"]:
            print(f"[FAIL] Error: Guided assessment did not explain Glucose parameter: {expl_q['response']}")
            errors += 1
        else:
            print("[PASS] Guided assessment parameter explanation trigger verified.")
            
        # 4. Test Prediction Result Analysis
        print("\nTesting Prediction Result Analysis...")
        st.session_state["last_prediction_data"] = {
            "type": "diabetes",
            "risk": 75.5,
            "category": "HIGH RISK",
            "features": {"Age": 35, "Glucose": 135},
            "shap": {"Glucose": 0.38, "BMI": 0.24, "Age": 0.18}
        }
        
        explain_pred_q = process_copilot_query("explain prediction")
        if "Prediction Result Analysis" not in explain_pred_q["response"] or "+38.0%" not in explain_pred_q["response"] or "Glucose" not in explain_pred_q["response"]:
            safe_resp = explain_pred_q["response"].encode("ascii", "replace").decode("ascii")
            print(f"[FAIL] Error: Prediction analysis explanation failed: {safe_resp}")
            errors += 1
        else:
            print("[PASS] Prediction result analysis and SHAP percentage attribution verified.")
            
        # 5. Test Quick Action: Show Health Tips
        tips_q = process_copilot_query("Show Health Tips")
        if "AHA Recommendation" not in tips_q["response"]:
            print(f"[FAIL] Error: Failed to show Health Tips: {tips_q['response']}")
            errors += 1
        else:
            print("[PASS] Health tips quick action response verified.")
            
    except Exception as e:
        print(f"[FAIL] Error: Unit test suite encountered active session state setup exception: {e}")
        errors += 1

    print("==================================================")
    if errors == 0:
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY! ENGINES CALIBRATED CORRECTLY.")
    else:
        print(f"[FAIL] VERIFICATION COMPLETED WITH {errors} ERRORS.")
    print("==================================================")
    
    return errors == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
