# Zenith filtering passes


import numpy as np
from astropy.time import Time
from sgp4.api import Satrec

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

# Generate time steps (every 1 min)
times = np.linspace(start_time.jd, end_time.jd, num=2880)#(num=1440 means every second snd 2880 every 30 secs)
times_astropy = Time(times, format="jd", scale="utc")

# Compute satellite positions
zenith_passes = []
for time in times_astropy:
    e, r, v = satellite.sgp4(time.jd1, time.jd2)  # Compute position
    elevation = r[2]  # Altitude in km
    azimuth = np.arctan2(v[0], v[1]) * 180 / np.pi  # Compute azimuth in degrees

    if elevation > 85:  # Zenith threshold
        zenith_passes.append((time.iso, elevation, azimuth))

# Output zenith passes with angles
print("\n🔹 **Zenith Passes Detected!** 🔹")
for pass_time, elevation, azimuth in zenith_passes:
    print(f"📍 Zenith pass at {pass_time} | Elevation: {elevation:.2f} km | Azimuth: {azimuth:.2f}°")


## Sample two include elevation angles
# We need to thoroughly examine why the elevation angles are not stricly in the range 85-90 degrees
import numpy as np
from astropy.time import Time
from sgp4.api import Satrec

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

# Generate time steps (every 1 min)
times = np.linspace(start_time.jd, end_time.jd, num=2880)
times_astropy = Time(times, format="jd", scale="utc")

# Compute satellite positions
zenith_passes = []
for time in times_astropy:
    e, r, v = satellite.sgp4(time.jd1, time.jd2)  # Compute position
    elevation = r[2]  # Altitude in km
    azimuth = np.arctan2(v[0], v[1]) * 180 / np.pi  # Compute azimuth in degrees
    elevation_angle = np.arctan2(r[2], np.sqrt(r[0]**2 + r[1]**2)) * 180 / np.pi  # Elevation angle at zenith

    if elevation > 85:  # Zenith threshold
        zenith_passes.append((time.iso, elevation, azimuth, elevation_angle))

# Output zenith passes with angles
print("\n🔹 **Zenith Passes Detected!** 🔹")
for pass_time, elevation, azimuth, elevation_angle in zenith_passes:
    print(f"📍 Zenith pass at {pass_time} | Elevation: {elevation:.2f} km | Azimuth: {azimuth:.2f}° | Elevation Angle: {elevation_angle:.2f}°")


## Comments
# a) How Azimuth and Elevation Work Together
# b) Imagine standing outside and watching a satellite pass overhead:

# c) Azimuth tells you which direction to face (north, east, south, west).

# c) Elevation tells you how high to look in the sky (near the horizon vs. directly overhead).

#d) Since you’re tracking zenith passes, the elevation angle is close to 85–90°, meaning the satellite is nearly overhead.
# e) The azimuth changes throughout each pass, explaining why the distance varies in different cycles! including the elevation angles