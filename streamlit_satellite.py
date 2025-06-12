import streamlit as st
import requests
import json

# Set API URL
#API_URL = "http://127.0.0.1:8000/api/data"

API_URL = "http://localhost:8000/api/data"

st.title("Satellite Simulation Dashboard ")
st.write("Real-time satellite position tracking and throughput simulation.")

# Fetch data from FastAPI
if st.button("Get Satellite Data"):
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        # Display satellite positions
        st.subheader("Satellite Positions:")
        for sat in data["satellite_positions"]:
            st.write(f"**{sat['name']}** ({sat['type']}) - Position: {sat['position']}")

        # Display throughput
        st.subheader("Simulated Throughput (Mbps):")
        st.write(data["throughput"])

    else:
        st.error("Failed to fetch data. Please ensure FastAPI is running.")
