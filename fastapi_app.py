# Deploy ML to production
# 1. With FastAPI

import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
import os

import streamlit as st
import requests
import json


#data = pd.read_csv("data\\diabetes.csv")
data = pd.read_csv(r"C:\Users\Clem\PycharmProjects\PythonProject\data\diabetes.csv")
X = data.drop('Outcome', axis =1)
y = data['Outcome']
model = LogisticRegression(max_iter = 1000)
#create the directory
os.makedirs('models', exist_ok =True)

model.fit(X, y)

# save the model,
joblib.dump(model, 'models\\logreg_model.joblib')

model_path = os.path.join(os.getcwd(),'models', 'logreg_model.joblib')

print("Looking for model at :", model_path)

model = joblib.load(model_path)

from pydantic import BaseModel
from fastapi import FastAPI
import joblib

# Load the logistic regression model
model = joblib.load('models/logreg_model.joblib')

# Define the input data model
class DiabetesData(BaseModel):
    Pregnancies: int
    Glucose: int
    BloodPressure: int
    SkinThickness: int
    Insulin: int
    BMI: float
    DiabetesPedigreeFunction: float
    Age: int
app = FastAPI()

# Define prediction endpoint
@app.post("/predict")
def predict(data: DiabetesData):
    input_data = {
        'Pregnancies': [data.Pregnancies],
        'Glucose': [data.Glucose],
        'BloodPressure': [data.BloodPressure],
        'SkinThickness': [data.SkinThickness],
        'Insulin': [data.Insulin],
        'BMI': [data.BMI],
        'DiabetesPedigreeFunction': [data.DiabetesPedigreeFunction],
        'Age': [data.Age]
    }
    input_df = pd.DataFrame(input_data)

    # Make a prediction
    prediction = model.predict(input_df)
    result = "Diabetes" if prediction[0] == 1 else "Not Diabetes"
    return {"prediction": result}


### with XGBOOST
