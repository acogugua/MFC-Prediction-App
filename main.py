
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

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

# Initialize the FastAPI app
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
