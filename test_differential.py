import sys
import os

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from nlp.clinical_parser import clinical_parser
from symptom_engine.differential_model import differential_engine

def test_pipeline():
    print("====================================")
    print("TESTING ADVANCED DIFFERENTIAL ENGINE")
    print("====================================")

    # Test Case 1: High Emergency Setup
    note_1 = "Patient is a 55 year old male who presents with severe chest pain and shortness of breath for 1 hours."
    print(f"\n[Test Case 1] Input: {note_1}")
    
    parsed_1 = clinical_parser.parse(note_1)
    print("Parsed NLP:", parsed_1)

    diffs_1 = differential_engine.predict_differentials(parsed_1, age=55, gender="Male", top_n=3)
    
    print("\n--- Results 1 ---")
    if parsed_1.get("flags"):
        print("EMERGENCY FLAGS:", parsed_1["flags"])
    
    for i, d in enumerate(diffs_1):
        print(f" {i+1}. {d['disease']} ({d['probability_percentage']}%) - Confidence: {d['confidence']}")
        print(f"    Rationale: {d['rationale']}\n")


    # Test Case 2: Standard Setup (Demographics Rule Trigger)
    note_2 = "25 year old female reports mild joint pain and slight fever since yesterday. No nausea."
    print("\n------------------------------------")
    print(f"[Test Case 2] Input: {note_2}")
    
    parsed_2 = clinical_parser.parse(note_2)
    print("Parsed NLP:", parsed_2)

    diffs_2 = differential_engine.predict_differentials(parsed_2, age=25, gender="Female", top_n=3)
    
    print("\n--- Results 2 ---")
    if parsed_2.get("flags"):
        print("EMERGENCY FLAGS:", parsed_2["flags"])
    
    for i, d in enumerate(diffs_2):
        print(f" {i+1}. {d['disease']} ({d['probability_percentage']}%) - Confidence: {d['confidence']}")
        print(f"    Rationale: {d['rationale']}\n")

if __name__ == "__main__":
    test_pipeline()
    print("End-to-End System Tests Completed.")
