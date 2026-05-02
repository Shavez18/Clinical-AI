import pandas as pd
data = pd.read_csv('C:\\Major project\\ai-health-assistant\\data\\raw\\Final_Augmented_dataset_Diseases_and_Symptoms.csv', nrows=5)
print("Columns:")
print(data.columns.tolist()[:20])
print("\nFirst row:")
print(data.iloc[0, :20].to_dict())
symptom_cols = [col for col in data.columns if "Symptom" in col]
print(f"\nSymptom columns count: {len(symptom_cols)}")
print(f"Symptom columns: {symptom_cols}")
