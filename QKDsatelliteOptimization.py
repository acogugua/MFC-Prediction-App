# Satellite Orbit Optimization
# Minimize atmospheric path length and maximize link duration
# a) Using zenith passes (when satellite passes diirectly overhead)
# b) Low elevation angles to reduce atmospheric thickness
# This will result in reduced turbulence absorption and improved link quality

import numpy as np
import matplotlib.pyplot as plt

# Constants
R_earth = 6371e3 # Radius of earth (m)
h_satellite = 500e3 # altitude of satellite in meters

# elevation angles from 0-90 degrees
elevation_angles = np.linspace(0,90,100)

# calculate atmospheric path length for each elevation angle
path_lengths = R_earth * (np.sqrt((R_earth + h_satellite)**2 / (R_earth**2 * np.sin(np.radians(elevation_angles))**2) -1)-np.cos(np.radians(elevation_angles)))

# Plotting
plt.figure(figsize=(10,6))
plt.plot(elevation_angles, path_lengths /1e3, 'b', linewidth =2)
plt.xlabel("Elevation Angle (degrees)")
plt.ylabel("Atmospheric Path length (km)")
plt.title("Atmospheric Path Lenght vs Elevation Angle")
plt.grid(True)
plt.show()
plt.savefig("LEO Path Length against Elevation.png")

# Zenith pass (90 degrees elevation angle
zenith_path_length = path_lengths[-1] / 1e3

# Minimum atmospheric path length
min_path_length = np.min(path_lengths) /1e3

# Path length at 30 degrees

path_length_30_degrees = path_lengths[elevation_angles ==30][0] /1e3

print(f"Atmospheric path length at zenith pass (90 degree): {zenith_path_length:.2f} km")
print(f"Minimum atmospheric path length:{min_path_length:2f} km")
print(f"Atmospheric path length at 30 degrees: {path_length_30_degrees:.2f} km")

# At low elevation angles, the signal travels much longer diagonal path through the atmospher,
# #increasing loss and turbulence effects

# At zenith (90 degrees) the signal travels the shortest vertical path, minimizing atmospheric interference- ideal for QKD

# The minimum atmospheric path length in this simulation is 1398 km. it occured at specific elevation angle
# slightly above 75 degrees. where the geometry of the Earth-satellite line results in the shortest atmospheric segment
# Zenith (90 degrees) is close to but not the absolute minimum due to the curvature of the earth and the geometry of the path
# The path length at 30 degrees is significantly longer as expected
