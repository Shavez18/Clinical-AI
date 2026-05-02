import pandas as pd
data = pd.read_csv("C:\\Major project\\ai-health-assistant\\data\\raw\\HeartDiseaseTrain-Test.csv")
print(data.groupby("target")[["age", "resting_blood_pressure", "Max_heart_rate", "oldpeak"]].mean())
print(data.groupby("target")["exercise_induced_angina"].value_counts(normalize=True))
print(data.groupby("target")["chest_pain_type"].value_counts(normalize=True))
