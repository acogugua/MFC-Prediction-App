import requests
import json

API_URL = "http://localhost:8000/predict"
input_data = {
    "Pregnancies": 2,
    "Glucose": 120,
    "BloodPressure": 80,
    "SkinThickness": 25,
    "Insulin": 100,
    "BMI": 24.5,
    "DiabetesPedigreeFunction": 0.5,
    "Age": 40
}

response = requests.post(API_URL, json=input_data)

print("Response:", response.json())
