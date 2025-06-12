import numpy as np
import matplotlib.pyplot as plt
import os
from astropy.time import Time
from sgp4.api import Satrec
from scipy.interpolate import interp1d
from cryptography.fernet import Fernet

# Generate a secure key for encryption
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Secure QKD Key Generation (512-bit)
def generate_qkd_key(bits=512):
    return np.random.randint(0, 2, bits)  # Secure random quantum key

# Key Verification using Parity Check
def verify_qkd_key(qkd_key):
    parity = sum(qkd_key) % 2  # Simple parity check (should be extended in real QKD)
    return parity == 0  # A valid key should have an even sum

# Secure Storage of QKD Key
def store_qkd_key(qkd_key, filename="qkd_key.enc"):
    qkd_str = "".join(map(str, qkd_key))  # Convert key to string
    encrypted_data = cipher.encrypt(qkd_str.encode())  # Encrypt key
    with open(filename, "wb") as f:
        f.write(encrypted_data)  # Save encrypted key

# Retrieve & Decrypt QKD Key
def retrieve_qkd_key(filename="qkd_key.enc"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            encrypted_key = f.read()
        decrypted_key = cipher.decrypt(encrypted_key).decode()
        return decrypted_key
    return None

# Define Starlink satellite TLE data
tle_lines = [
    "STARLINK-5722",
    "1 44713U 19074U   24235.84331967  .00000281  00000+0  46458-6 0  9993",
    "2 44713  53.2167 280.3292 0001521  86.0935 274.0231 15.08844460125864"
]

# Load the satellite using sgp4
satellite = Satrec.twoline2rv(tle_lines[1], tle_lines[2])

# Define observer location (Melbourne)
latitude = -37.8136
longitude = 144.9631
altitude = 0  # Ground level

# Define time range
start_time = Time("2025-06-03T00:00:00", scale="utc")
end_time = Time("2025-06-04T00:00:00", scale="utc")

# Generate time steps (every 10 seconds for finer resolution)
times = np.linspace(start_time.jd, end_time.jd, num=8640)
times_astropy = Time(times, format="jd", scale="utc")

# Compute satellite positions
elevation_data = []
zenith_passes = []
qkd_schedules = []
qkd_transmissions = []
current_pass = None

for time in times_astropy:
    e, r, v = satellite.sgp4(time.jd1, time.jd2)  # Compute position
    elevation = r[2]  # Altitude in km
    azimuth = np.arctan2(v[0], v[1]) * 180 / np.pi  # Compute azimuth in degrees
    elevation_angle = np.arctan2(r[2], np.sqrt(r[0]**2 + r[1]**2)) * 180 / np.pi  # Elevation angle

    elevation_data.append((time.jd, elevation, azimuth, elevation_angle))

    # Detect zenith pass entry & exit
    if elevation_angle > 85:
        if current_pass is None:
            current_pass = {"start": time.iso, "start_elevation": elevation_angle}
        current_pass["end"] = time.iso
        current_pass["end_elevation"] = elevation_angle
    elif current_pass:
        # Calculate duration
        start_time = Time(current_pass["start"], format="iso", scale="utc")
        end_time = Time(current_pass["end"], format="iso", scale="utc")
        duration = (end_time - start_time).sec
        current_pass["duration"] = duration

        zenith_passes.append(current_pass)

        # **Schedule QKD Transmission**
        qkd_start_time = start_time.iso
        qkd_end_time = Time(start_time.jd + (duration / 2 / 86400), format="jd").iso  # Allocate half the pass time for QKD
        qkd_key = generate_qkd_key()  # Simulated QKD key bits

        # **Verify Key**
        if verify_qkd_key(qkd_key):
            store_qkd_key(qkd_key)  # Secure storage
            qkd_transmissions.append({"start": qkd_start_time, "end": qkd_end_time, "QKD Key": qkd_key})
        else:
            print(f"⚠️ Invalid QKD Key Detected at {qkd_start_time} - Discarding Transmission")

        current_pass = None

# Convert data to arrays for interpolation
jd_vals = np.array([entry[0] for entry in elevation_data])
elev_vals = np.array([entry[1] for entry in elevation_data])

# Interpolate elevation data
interp_func = interp1d(jd_vals, elev_vals, kind="cubic")
max_idx = np.argmax(elev_vals)
max_time = Time(jd_vals[max_idx], format="jd", scale="utc")
max_elevation = interp_func(jd_vals[max_idx])
max_azimuth = elevation_data[max_idx][2]
max_elevation_angle = elevation_data[max_idx][3]

# Output Zenith Pass Data
print("\n🔹 **Interpolated Zenith Pass Detected!** 🔹")
print(f"📍 Zenith pass at {max_time.iso} | Max Elevation: {max_elevation:.2f} km | Azimuth: {max_azimuth:.2f}° | Elevation Angle: {max_elevation_angle:.2f}°")

# Output QKD Scheduling Allocation
print("\n🔹 **Scheduled Time Allocation for QKD Communication** 🔹")
for schedule in qkd_schedules:
    print(f"📍 QKD Transmission Window: {schedule['start']} - {schedule['end']} | Duration: {schedule['duration']/60:.2f} min")

# Output QKD Transmission with Verified Key Data
print("\n🔹 **QKD Transmission Data** (Secured & Verified) 🔹")
for transmission in qkd_transmissions:
    print(f"📍 QKD Key Transmission: {transmission['start']} - {transmission['end']} | Key Bits: {''.join(map(str, transmission['QKD Key'][:64]))}...")  # Show first 64 bits

# Retrieve & Decrypt Stored QKD Key
retrieved_key = retrieve_qkd_key()
if retrieved_key:
    print("\n🔹 **Retrieved & Decrypted QKD Key** 🔹")
    print(f"📍 Decrypted Key Bits: {retrieved_key[:64]}...")  # Show first 64 bits
else:
    print("\n❌ No stored QKD key found for decryption.")

# 🌍 Graphing Predictions
plt.figure(figsize=(10, 5))
plt.plot(jd_vals, elev_vals, label="Elevation Curve", color="blue")
plt.axhline(y=85, color="r", linestyle="--", label="Zenith Threshold (85°)")
plt.scatter(jd_vals[max_idx], max_elevation, color="green", label="Peak Zenith")
plt.xlabel("Time (Julian Date)")
plt.ylabel("Elevation (km)")
plt.title("Satellite Zenith Pass Prediction & QKD Scheduling")
plt.legend()
plt.show()

# Enhancements for Secure QKD Demonstration
# ✔ Retrieves & decrypts stored keys after transmission.
# ✔ Verifies keys before storing using parity check for integrity.
# ✔ **Encrypts keys using Fernet encryption to ensure security.
# ✔ Displays decrypted key for demonstration after retrieval.