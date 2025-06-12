import numpy as np
import matplotlib.pyplot as plt
import os
import hashlib
from astropy.time import Time
from sgp4.api import Satrec
from scipy.interpolate import interp1d
from cryptography.fernet import Fernet

# Generate a secure key for encryption
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# **BB84 Quantum Key Generation**
def bb84_qkd_key(bits=512):
    basis_choices = np.random.randint(0, 2, bits)  # Random basis (0 = rectilinear, 1 = diagonal)
    raw_key = np.random.randint(0, 2, bits)  # Random quantum bits
    return basis_choices, raw_key

# **Error Correction (Parity Check)**
def error_correction(qkd_key):
    parity = sum(qkd_key) % 2  # Simple parity check
    return parity == 0  # A valid key should have an even sum

# **Privacy Amplification (Hashing)**
def privacy_amplification(qkd_key):
    key_str = "".join(map(str, qkd_key))
    hashed_key = hashlib.sha256(key_str.encode()).hexdigest()  # SHA-256 hashing
    return hashed_key

# **Secure Storage of QKD Key (AES-256)**
def store_qkd_key(qkd_key, filename="qkd_key.enc"):
    hashed_key = privacy_amplification(qkd_key)  # Apply privacy amplification
    encrypted_data = cipher.encrypt(hashed_key.encode())  # Encrypt key
    with open(filename, "wb") as f:
        f.write(encrypted_data)  # Save encrypted key

# **Retrieve & Decrypt QKD Key**
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
        basis_choices, raw_key = bb84_qkd_key()  # Generate BB84 quantum key

        # **Verify Key Integrity**
        if error_correction(raw_key):
            store_qkd_key(raw_key)  # Secure storage
            qkd_transmissions.append({"start": qkd_start_time, "end": qkd_end_time, "QKD Key": raw_key})
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

# Output QKD Transmission with Verified Key Data
print("\n🔹 **QKD Transmission Data (Secured & Verified)** 🔹")
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
utc_times = [Time(jd, format="jd").iso for jd in jd_vals]  # Convert JD to UTC


plt.figure(figsize=(10, 5))
plt.plot(jd_vals, elev_vals, label="Elevation Curve", color="blue")
plt.axhline(y=85, color="r", linestyle="--", label="Zenith Threshold (85°)")
plt.scatter(jd_vals[max_idx], max_elevation, color="green", label="Peak Zenith")
#plt.xlabel("Time (Julian Date)")
plt.xticks(jd_vals[::500], utc_times[::500], rotation=45)  # Show readable timestamps
#plt.xlabel("Pass Time (UTC)")
plt.xlabel("Elapsed Time (Minutes)")
plt.ylabel("Elevation (km)")
plt.title("Satellite Zenith Pass Prediction & QKD Scheduling")
plt.legend()
#plt.show()
plt.savefig("Graphing Predictions.png")
plt.show()

# 🌍 Graphing Predictions with Annotations
plt.figure(figsize=(12, 6))
plt.plot(jd_vals, elev_vals, label="Elevation Curve", color="blue")
plt.axhline(y=85, color="r", linestyle="--", label="Zenith Threshold (85°)")

# Highlight QKD windows
for pass_data in zenith_passes:
    plt.axvspan(pass_data["start"], pass_data["end"], color="yellow", alpha=0.3, label="QKD Transmission Window")

# Annotate peak elevation
plt.scatter(jd_vals[max_idx], max_elevation, color="green", label="Peak Zenith")
plt.annotate(f"Peak Elevation: {max_elevation:.2f} km",
             xy=(jd_vals[max_idx], max_elevation),
             xytext=(jd_vals[max_idx] + 0.1, max_elevation + 5),
             arrowprops=dict(facecolor='green', shrink=0.05))

plt.xticks(jd_vals[::500], utc_times[::500], rotation=45)  # Show readable timestamps
#plt.xlabel("Pass Time (UTC)")
plt.xlabel("Elapsed Time (Minutes)")
plt.ylabel("Elevation (km)")
plt.title("Satellite Zenith Pass Prediction & QKD Scheduling")
plt.legend()
plt.grid(True)
#plt.show()
plt.savefig("QKD Predictions with Annotations.jpg")
plt.show()

# Convert Julian Date to elapsed time in seconds
start_jd = jd_vals[0]  # Reference start time
elapsed_time_sec = [(jd - start_jd) * 86400 for jd in jd_vals]  # Convert JD difference to seconds
elapsed_time_min = [t / 60 for t in elapsed_time_sec]  # Convert seconds to minutes

# 🌍 Graphing Predictions with Time in Minutes
plt.figure(figsize=(12, 6))
plt.plot(elapsed_time_min, elev_vals, label="Elevation Curve", color="blue")
plt.axhline(y=85, color="r", linestyle="--", label="Zenith Threshold (85°)")

# Highlight QKD windows
for pass_data in zenith_passes:
    start_time_min = (pass_data["start"] - start_jd) * 1440  # Convert JD to minutes
    end_time_min = (pass_data["end"] - start_jd) * 1440
    plt.axvspan(start_time_min, end_time_min, color="yellow", alpha=0.3, label="QKD Transmission Window")

# Annotate peak elevation
#peak_time_min = (max_time - start_jd) * 1440
peak_time_min = (max_time.jd - start_jd) * 1440  # Convert Time object to Julian Date float
plt.scatter(peak_time_min, max_elevation, color="green", label="Peak Zenith")
plt.annotate(f"Peak Elevation: {max_elevation:.2f} km",
             xy=(peak_time_min, max_elevation),
             xytext=(peak_time_min + 5, max_elevation + 5),
             arrowprops=dict(facecolor='green', shrink=0.05))

# Labels & Legends
plt.xlabel("Elapsed Time (Minutes)")
plt.ylabel("Elevation (km)")
plt.title("Satellite Zenith Pass Prediction & proposed QKD Scheduling")
plt.legend()
plt.grid(True)
plt.savefig("QKD Predictions with Annotations.jpg")
plt.show()

