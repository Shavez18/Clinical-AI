from src.nlp.clinical_parser import clinical_parser
from src.symptom_engine.differential_model import differential_engine
import json

def test_scenario(name, text):
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"INPUT: '{text}'")
    
    parsed = clinical_parser.parse(text)
    print("\n[PARSED DATA]")
    print(json.dumps(parsed, indent=2))
    
    differentials = differential_engine.predict_differentials(
        parsed_symptoms=parsed,
        age=30,
        gender="Male",
        top_n=3
    )
    
    print("\n[DIAGNOSIS OUTPUT]")
    for r in differentials:
        print(f" - {r['disease']}: {r['probability_percentage']}% ({r['confidence']})")
        print(f"   Reasoning: {r['rationale']}")

if __name__ == "__main__":
    test_scenario("Advanced Negation", "I have a cough but I am not experiencing any chest pain or fever.")
    test_scenario("Complex Ancestor Negation", "The patient denies having shortness of breath, but confirms sweating.")
    test_scenario("Strict Filtration", "I have pain and sweating") # No chest pain -> Heart attack MUST be removed
    test_scenario("Emergency Threshold", "I have chest pain but no shortness of breath") # Only 1 critical flag. No emergency override allowed.
    test_scenario("Context Usage", "I have had a high fever and headache after travel to Africa") # Malaria should bonus
    test_scenario("Context Usage 2", "I've had this cough for months") # Tuberculosis should bonus
