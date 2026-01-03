import math
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd 

def settling_velocities(roh, D):
    g = 9.81
    roh_water = 1025
    # CORRECTED: Dynamic viscosity of water at ~20°C is ~1.002e-3 Pa.s (Ns/m2)
    # The file says 1.07e-3, so we use that.
    vis_water = 1.07 * 10 ** -3 
    return (roh - roh_water) * g * D**2 / (18 * vis_water)

def calc_settling_velocities(time_s, height_m):
    # Standard method: Linear Regression on Height vs Time
    # Slope = velocity (m/s)
    # We only fit where the sediment is actually settling (ignoring the flat tail if possible)
    # For simplicity here, we fit the whole range, but visually check for linearity.
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(time_s, height_m)
    
    # Velocity is negative slope (height decreases)
    v_s = -slope 
    
    fitted_h = intercept + slope * time_s
    
    results = {
        "k": slope,       # Slope of the line
        "vs": v_s,        # Settling velocity in m/s
        "fitted_time": time_s,
        "fitted_height": fitted_h, # Comma was missing here
        "R_squared": r_value**2
    }
    return results

def data_clean(df):
    # Extract Time (Column 7) and Convert Minutes -> Seconds
    time_minutes = pd.to_numeric(df.iloc[4:, 7], errors='coerce').dropna().values
    time_seconds = time_minutes * 60 

    # Extract Heights (Columns 8-12) and Convert mm -> meters
    # Dividng by 1000 to get meters
    h_1157 = pd.to_numeric(df.iloc[4:, 8], errors='coerce').dropna().values / 1000
    h_1134 = pd.to_numeric(df.iloc[4:, 9], errors='coerce').dropna().values / 1000
    h_1123 = pd.to_numeric(df.iloc[4:, 10], errors='coerce').dropna().values / 1000
    h_1096 = pd.to_numeric(df.iloc[4:, 11], errors='coerce').dropna().values / 1000
    h_1072 = pd.to_numeric(df.iloc[4:, 12], errors='coerce').dropna().values / 1000

    return time_seconds, h_1157, h_1134, h_1123, h_1096, h_1072

# --- Theoretical Calculations ---
# D should be in meters. 4 microns = 4e-6 m.
settling_rate_Kaolinite = settling_velocities(2650, 4 * 10 **-6)
settling_rate_sand = settling_velocities(2650, 100 * 10 **-6)
# D = 8.5 microns from file
settling_rate_testfluid = settling_velocities(2620, 8.5 * 10 **-6)

print(f"Theoretical Stokes Velocity (Test Fluid): {settling_rate_testfluid:.2e} m/s")

# --- Load Data ---
# Update this path to your actual file location
file_path = r'C:\Users\malte\OneDrive\Dokumente\CivilEngineering\Roomyrivers\Data_tut_3.xlsx'
# Use sheet_name if needed, usually index 0 is default
data = pd.read_excel(file_path, header=None) 

time, h_1157, h_1134, h_1123, h_1096, h_1072 = data_clean(data)

# --- Plot Raw Data ---
plt.figure(figsize=(10, 6))
plt.plot(time, h_1157, 'o', label='Density 1157 kg/m3')
plt.plot(time, h_1134, 'o', label='Density 1134 kg/m3')
plt.plot(time, h_1123, 'o', label='Density 1123 kg/m3')
plt.plot(time, h_1096, 'o', label='Density 1096 kg/m3')
plt.plot(time, h_1072, 'o', label='Density 1072 kg/m3')
plt.xlabel('Time (s)')
plt.ylabel('Height (m)')
plt.title('Sedimentation Data (Corrected Units)')
plt.legend()
plt.grid(True)
plt.show()

# --- Calculate Experimental Velocities ---
experiments = [
    ("1157", calc_settling_velocities(time, h_1157)),
    ("1134", calc_settling_velocities(time, h_1134)),
    ("1123", calc_settling_velocities(time, h_1123)),
    ("1096", calc_settling_velocities(time, h_1096)),
    ("1072", calc_settling_velocities(time, h_1072))
]

# --- Sort Results ---
sorted_experiments = sorted(experiments, key=lambda x: x[1]['vs'], reverse=True)

# --- Print Sorted Results ---
print(f"{'Density':<10} | {'vs (m/s)':<12} | {'R^2':<8}")
print("-" * 40)
for label, res in sorted_experiments:
    print(f"{label:<10} | {res['vs']:<12.5e} | {res['R_squared']:<8.4f}")

# --- Plot Fits ---
plt.figure(figsize=(10, 6))
colors = {'1157': 'blue', '1134': 'orange', '1123': 'green', '1096': 'red', '1072': 'purple'}

for label, res in experiments:
    # Re-map data for plotting
    if label == '1157': h_data = h_1157
    elif label == '1134': h_data = h_1134
    elif label == '1123': h_data = h_1123
    elif label == '1096': h_data = h_1096
    else: h_data = h_1072
    
    plt.plot(time, h_data, 'o', color=colors[label], alpha=0.3, label=f'Density {label}')
    plt.plot(res['fitted_time'], res['fitted_height'], '-', color=colors[label], linewidth=2)

plt.xlabel('Time (s)')
plt.ylabel('Height (m)')
plt.title('Sedimentation Data & Linear Fits')
plt.legend()
plt.grid(True)
plt.show()