import requests
import sys
try:
    r = requests.post('http://localhost:8000/register', json={'username': 'test1', 'email': 'test1@example.com', 'password': 'password', 'role': 'patient', 'full_name': 'Test', 'hospital_name': ''})
    print('Status:', r.status_code)
    print('Text:', r.text)
except Exception as e:
    print('Exception:', e)
