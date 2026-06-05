import requests
try:
    r = requests.post('http://localhost:8000/register', json={'username': 'test1', 'email': 'test1@example.com', 'password': 'password', 'role': 'patient', 'full_name': 'Test', 'hospital_name': ''})
    with open('register_error.txt', 'w') as f:
        f.write(str(r.status_code) + '\n')
        f.write(r.text)
except Exception as e:
    with open('register_error.txt', 'w') as f:
        f.write('Exception: ' + str(e))
