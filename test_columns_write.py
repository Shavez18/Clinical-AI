import joblib
columns = joblib.load(r'C:\Major project\ai-health-assistant\src\models\heart_model_columns.pkl')
with open(r'C:\Major project\ai-health-assistant\test_out.txt', 'w') as f:
    f.write('\n'.join(columns))
