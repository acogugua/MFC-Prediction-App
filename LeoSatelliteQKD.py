# Uplink and Downlink
import numpy as np
import matplotlib.pyplot as plt


# Constants
c = 3e8 # speed of light in vacuum (m/s)
wavelength = 1550e-9 # wavelength of the QKD signal in (m)
k = 2 * np.pi / wavelength  # wavelength number

# Diffraction loss calculation

def diffraction_loss (distance, aperture_diameter):
    return 10 * np.log10((wavelength * distance) / (aperture_diameter **2))

# Atmospheric turbulence calculation
def turbulence_loss(distance, beam_diameter):
    return 10 * np.log10(1 + (distance / beam_diameter)**2)


# Total channel loss calculation
def total_channel_loss(distance, aperture_diameter, beam_diameter, turbulence_factor):
    diffraction = diffraction_loss(distance, aperture_diameter)
    turbulence = turbulence_loss(distance, beam_diameter) * turbulence_factor
    return diffraction + turbulence

# Parameters

distances = np.linspace(100, 1200, 100)  # distance from 100 km to 120 km
aperture_diameter_downlink = 1.5  # Aperture diameter of downlink (m)
aperture_diameter_uplink = 0.5  # Aperture diameter of uplink (m)
beam_diameter_downlink = 12  # Beam diameter of downlink (m)
beam_diameter_uplink = 50  # Beam diameter of downlink (m)
turbulence_factor_downlink = 0.2  # Turbulence factor for downlink (m)
turbulence_factor_uplink = 1.0  # Turbulence factor for uplink (m)

# calculation Losses
loss_downlink = total_channel_loss(distances,aperture_diameter_downlink,beam_diameter_downlink, turbulence_factor_downlink)
loss_uplink = total_channel_loss(distances, aperture_diameter_uplink,beam_diameter_uplink,turbulence_factor_uplink)

# plot results
plt.figure(figsize=(10,6))
plt.plot(distances,loss_downlink, label = "Downlink Channel Loss")
plt.plot(distances, loss_uplink, label="Uplink channel Loss")
plt.xlabel("Path Length (km)")
plt.ylabel("Total Channel Loss (dB)")
plt.title("Channel Loss vs Path Length for Downlink and Uplink QKD Channels")
plt.legend()
plt.grid(True)
plt.show()
plt.savefig("Downlink and Uplink QKD Channels")


# Analysis
print("Analysis of QKD Channels")
print(f"Downlink channel loss at 1200 km: {loss_downlink[-1]:.2f} dB")
print(f"Uplink channel loss at 1200 km: {loss_uplink[-1]:.2f} dB")
print(f"Downlink loss at 500 km: {loss_downlink[distances == 500][0]:.2f} dB")
print(f"Uplink channel loss at 500 km:{loss_uplink[distances ==500][0]:.2f} dB")
