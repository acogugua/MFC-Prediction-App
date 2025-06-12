Streamlit run -Diabetes Dataset Deployed


C:\Users\Clem\PycharmProjects\PythonProject>streamlit run C:\Users\Clem\PycharmProjects\PythonProject\DemoWithStreamlit.py

Use python module

python -m streamlit run C:\Users\Clem\PycharmProjects\PythonProject\DemoWithStreamlit.py

or

py -m streamlit run C:\Users\Clem\PycharmProjects\PythonProject\DemoWithStreamlit.py

Confirm FastAPI is Running
uvicorn your_fastapi_script:app --reload

Then open


  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8502 ----from your computer
  Network URL: http://192.168.1.118:8502  --- from a remote system is your computer address is 192.168.1.118: use port 8502


Project 2

convert your Flask-based satellite simulation into a FastAPI application and provide a Streamlit frontend for visualization

Step 1: Convert Flask to FastAPI
FastAPI Deployment (fastapi_satellite.py)
import pandas as pd
import random
from fastapi import FastAPI
from pydantic import BaseModel
from skyfield.api import load, EarthSatellite, Topos

# Initialize FastAPI app
app = FastAPI()

# Load satellite data and initialize timescale
ts = load.timescale()
tle_data = {
    "LEO": [
        ("STARLINK-3996", "1 52617U 22052V   24235.84331967 -.00000281  00000+0  46458-6 0  9993",
         "2 52617  53.2167 280.3292 0001521  86.0935 274.0231 15.08844460125864"),
    ],
    "GEO": [
        ("INMARSAT 4-F1", "1 28628U 05009A   24235.80508400  .00000026  00000+0  00000+0 0  9997",
         "2 28628   4.3477  41.3195 0002043 142.3871 255.7987  1.00272317 71027"),
    ]
}

def load_satellites():
    satellites = {"LEO": [], "GEO": []}
    for category, sats in tle_data.items():
        satellites[category] = [
            EarthSatellite(line1, line2, name, ts) for name, line1, line2 in sats
        ]
    return satellites

satellites = load_satellites()

ground_stations = {
    "Station 1": Topos(latitude_degrees=-34.8098, longitude_degrees=138.6200),
}

@app.get("/api/data")
def get_satellite_data():
    now = ts.now()
    satellite_positions = []

    # Get current positions for satellites
    for category, sats in satellites.items():
        for sat in sats:
            pos = sat.at(now).position.km  # Position in kilometers
            satellite_positions.append({
                "name": sat.name,
                "type": category,
                "position": pos.tolist()
            })

    # Simulate throughput
    throughput = [random.randint(1, 10) * 1e6 for _ in range(len(satellite_positions))]

    return {
        "satellite_positions": satellite_positions,
        "throughput": throughput
    }
B. Running the FastAPI Server
Install dependencies (if not already installed):
pip install fastapi uvicorn skyfield pydantic pandas

Run FastAPI:
C:\Users\Clem>uvicorn fastapi_satellite:app --reload --app-dir C:\Users\Clem\PycharmProjects\PythonProject

Result
C:\Users\Clem>uvicorn fastapi_satellite:app --reload --app-dir C:\Users\Clem\PycharmProjects\PythonProject
←[32mINFO←[0m:     Will watch for changes in these directories: ['C:\\Users\\Clem']
←[32mINFO←[0m:     Uvicorn running on ←[1mhttp://127.0.0.1:8000←[0m (Press CTRL+C to quit)
←[32mINFO←[0m:     Started reloader process [←[36m←[1m15232←[0m] using ←[36m←[1mStatReload←[0m
←[32mINFO←[0m:     Started server process [←[36m13200←[0m]
←[32mINFO←[0m:     Waiting for application startup.
←[32mINFO←[0m:     Application startup complete.

Step 2: Streamlit Frontend

C:\Users\Clem\PycharmProjects\PythonProject>streamlit run C:\Users\Clem\PycharmProjects\PythonProject\streamlit_satellite.py