import requests
import json

url = "http://localhost:5001/api/login"
data = {"username": "parent", "password": "123", "role": "parent"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    user_data = response.json().get('user', {})
    print(f"Student Name: {user_data.get('student_name')}")
    print(f"Is Absent: {user_data.get('is_absent')}")
    print(f"Assigned Stop: {user_data.get('assigned_stop')}")
except Exception as e:
    print(f"Error: {e}")
