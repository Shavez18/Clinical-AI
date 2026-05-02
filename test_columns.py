import joblib
columns = joblib.load(r'C:\Major project\ai-health-assistant\src\models\heart_model_columns.pkl')
for i, c in enumerate(columns):
    print(i, c)
