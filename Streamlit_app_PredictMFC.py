# Create Streanlit APP

import streamlit as st
import pandas as pd
import  joblib
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

#from FastAPI_Predict_mfc_height import X_test, Y_test

#Load model
#model= joblib.load(r"C:\Users\Clem\PycharmProjects\PythonProject\random_forest_model.pkl")
model = joblib.load("random_forest_model.pkl")


st.title("ML Prediction App of Critical MFC Heights")


# Load test dataset

#X_test = pd.read_csv(r"C:\Users\Clem\PycharmProjects\PythonProject\X_test_sample.csv")
#Y_test = pd.read_csv(r"C:\Users\Clem\PycharmProjects\PythonProject\Y_test_sample.csv")
X_test = pd.read_csv("X_test_sample.csv")
Y_test_test = pd.read_csv("Y_test_sample.csv")

# Convert labels to binary format

Y_test_bin = label_binarize(Y_test, classes=["R1","R2","R3"])
y_pred_prob = model.predict_proba(X_test)

# Display ROC Curve
st.subheader("Model ROC Curve & AUC")

fig, ax = plt.subplots(figsize=(8,6))
colors = ["blue","red","green"]
for i, label in enumerate(["R1","R2","R3"]):
    fpr, tpr, _ = roc_curve(Y_test_bin[:,i], y_pred_prob[:,i])
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr,tpr, color = colors[i],lw=2, label=f"{label} (AUC= {roc_auc:.2f})")
ax.plot([0,1],[0,1], "k--",lw=2)# Random ine
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curve for Multi-Class Classification Model")
ax.legend(loc="lower right")

st.pyplot(fig)# plot in streamlit

st.write("Enter the 3-axis coordinate of your gait acceleration and gyrometer data")

# Define user input fields(features)
AccX = st.number_input("AccX", format="%.4f")
AccY = st.number_input("AccY", format="%.4f")
AccZ = st.number_input("AccZ", format="%.4f")
GyroX = st.number_input("GyroX", format="%.4f")
GyroY = st.number_input("GyroY", format="%.4f")
GyroZ = st.number_input("GyroZ", format="%.4f")

# Collect input into a DataFrame
input_data =pd.DataFrame([[AccX,AccY,AccZ,GyroX,GyroY,GyroZ]], columns=['AccX','AccY','AccZ','GyroX','GyroY','GyroZ'])

# Define Interpretaion Function

def interpret_prediction(prediction):
    if prediction == "R1":
        return "R1: MFC < 1.50 cm (Critical -Requires Immediate Attention)"
    elif prediction == "R2":
        return "R2 :MFC between 1.50 -2.0 cm (Safe -Within Acceptable Limits)"
    elif prediction == "R3":
        return "R3: MFC >= 2.0 cm (Above Safety Limit -Well Protected)"
    else:
        return "Unknown, check input parameters"

# Make prediction and Display Interpretation

if st.button("Predict"):
    prediction = model.predict(input_data)[0]
    interpretation = interpret_prediction(prediction)
    st.success(f"Prediction:{prediction}")
    st.info(interpretation)


