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
