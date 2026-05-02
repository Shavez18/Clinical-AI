import requests

data = {
    'age': 24, 'sex': 1, 'cp': 1, 'trestbps': 100, 
    'chol': 600, 'fbs': 1, 'restecg': 1, 'thalach': 105, 
    'exang': 1, 'oldpeak': 6.0, 'slope': 0, 'ca': 3, 'thal': 1
}
headers = {'Authorization': 'Bearer demo_jwt_token'}

try:
    res = requests.post('http://localhost:8000/predict/heart', json=data, headers=headers)
    print("Status:", res.status_code)
    print("Text:", res.text)
except Exception as e:
    print("Exception calling API:", e)
