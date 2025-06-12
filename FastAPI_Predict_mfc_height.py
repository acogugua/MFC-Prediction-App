#

# Predict MFC FAST API

# importing dependencies

import time
import numpy as np 
import pandas as pd 
import csv
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, RobustScaler


# Load dataset
data1= pd.read_csv(r"C:\Users\Clem\PycharmProjects\PythonProject\data\BilKaiLisaMonqMFC.csv")
# Process data

X = data1.drop(['Label'], axis = 1)
Y = data1['Label']
X = pd.get_dummies(X, prefix_sep='_')
y = LabelEncoder().fit_transform(Y) # Encode categorical variables
X = RobustScaler().fit_transform(X)# Scale features


# Train and save model
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import joblib

# Split data

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, 
                                                        test_size = 0.20, 
                                                        random_state = 42)
# TRain model
start = time.process_time()
model = RandomForestClassifier(n_estimators=400,max_depth = 8, max_features = 'sqrt',random_state = 42,criterion = 'gini').fit(X_train,Y_train)
print(time.process_time() - start)
model.fit(X_train, Y_train)

# Save model
joblib.dump(model, "random_forest_model.pkl")

# Create API
from fastapi import FastAPI
import pandas as pd
import joblib
from pydantic import BaseModel

# Load trained model
model = joblib.load("random_forest_model.pkl")

app = FastAPI()

class Item(BaseModel):
    features: list

@app.post("/predict")
async def predict(item: Item):
    X_input = pd.DataFrame([item.features])
    prediction = model.predict(X_input)
    return {"prediction": prediction.tolist()}

