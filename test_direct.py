import requests, json

data = {
    'age': 24, 'sex': 1, 'cp': 1, 'trestbps': 100, 
    'chol': 600, 'fbs': 1, 'restecg': 1, 'thalach': 105, 
    'exang': 1, 'oldpeak': 6.0, 'slope': 0, 'ca': 3, 'thal': 1
}

try:
    with open('test_res.txt', 'w') as f:
        res = requests.post('http://localhost:8000/predict/heart', json=data, headers={'Authorization': 'Bearer demo_jwt_token'})
        f.write(f"Status: {res.status_code}\n")
        f.write(f"Text: {res.text}\n")
except Exception as e:
    with open('test_res.txt', 'w') as f:
        f.write(f"Error: {e}\n")
