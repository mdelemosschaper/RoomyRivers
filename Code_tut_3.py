import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd 

# --- 1. Define Theoretical Calculation (Stokes) ---
def settling_velocity_stokes(rho_fluid):
    """
    Calculates settling velocity using Stokes' Law.
    Parameters from image:
    - Particle Density (rho_p): 2620 kg/m3
    - Viscosity (mu): 1.07 x 10^-3 Ns/m2
    - Diameter (d50): 8.5 microns
    """
    g = 9.81
    rho_p = 2620  # From image
    d_50 = 8.5 * 10**-6  # Converted microns to meters
    viscosity = 1.07 * 10**-3 # From image
    
    # Stokes formula: v = ( (rho_p - rho_f) * g * D^2 ) / (18 * mu)
    v_s = (rho_p - rho_fluid) * g * (d_50**2) / (18 * viscosity)
    return v_s

# --- 2. Calculation Functions ---

def calc_log_phase_rate(time_s, height_m):
    """
    Calculates sedimentation rate using the Log-Linear method on the first 3 points.
    Formula: ln(h) = ln(h0) - kt
    v_s = k * h_mid
    """
    # 1. Select first 3 points (Indices 0, 1, 2)
    t_segment = time_s[:3]
    h_segment = height_m[:3]
    
    # 2. Log-transform height
    ln_h = np.log(h_segment)
    
    # 3. Linear Regression on ln(h) vs t
    # Slope corresponds to -k
    slope, intercept, r_value, p_value, std_err = stats.linregress(t_segment, ln_h)
    
    k = -slope  # Decay coefficient (1/s)
    
    # 4. Calculate v_s = k * h_mid
    h_mid = np.mean(h_segment)
    v_s = k * h_mid
    
    return k, v_s

def calc_tangent_velocity(time_s, height_m):
    """
    Calculates settling velocity based on the tangent line between Point 3 and Point 4.
    (Indices 2 and 3 -> 20 min and 30 min).
    Returns velocity and the line parameters (slope, intercept) for plotting.
    """
    # Select Point 3 (Index 2) and Point 4 (Index 3)
    t1 = time_s[2]
    t2 = time_s[3]
    h1 = height_m[2]
    h2 = height_m[3]
    
    # Calculate Slope (m)
    slope = (h2 - h1) / (t2 - t1)
    
    # Calculate Intercept (c) -> y = mx + c  =>  c = y - mx
    intercept = h1 - slope * t1
    
    # Velocity is negative slope
    v_s = -slope
    
    return v_s, slope, intercept

# --- 3. Data Cleaning Function ---
def data_clean(df):
    # --- EXACT TIME VALUES (Minutes) ---
    # Hardcoded from your provided list (Rows 5-47)
    time_minutes_list = [
        0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 130, 190, 288, 
        1076, 1196, 1366, 1747, 1917, 2075, 2444, 2564, 2684, 2824, 
        3078, 3198, 3390, 3817, 3978, 4270, 4580, 4763, 8230, 9576, 
        11043, 12527, 13621, 18306, 21162, 23996, 28415, 29855, 61641
    ]
    
    # Convert to numpy array and then to seconds
    time_seconds = np.array(time_minutes_list) * 60

    # --- Extract Heights ---
    # We slice the dataframe to match the length of the time array (43 points)
    # Rows 5-47 correspond to indices 4:47 in pandas (exclusive end)
    h_1096 = pd.to_numeric(df.iloc[4:47, 11], errors='coerce').values / 1000
    h_1072 = pd.to_numeric(df.iloc[4:47, 12], errors='coerce').values / 1000

    return time_seconds, h_1096, h_1072

# --- MAIN EXECUTION ---

# 1. Theoretical Calculations for the specific densities requested
v_stokes_1096 = settling_velocity_stokes(rho_fluid=1096)
v_stokes_1072 = settling_velocity_stokes(rho_fluid=1072)

print(f"--- Theoretical Stokes Velocities (D=8.5um, rho_p=2620) ---")
print(f"Density 1096: {v_stokes_1096:.2e} m/s")
print(f"Density 1072: {v_stokes_1072:.2e} m/s")
print("-" * 50)

# 2. Load Data
file_path = r'C:\Users\Public\PublicProgramming\Malte\RoomyRivers\Data_tut_3.xlsx'

try:
    data = pd.read_excel(file_path, header=None)
    time, h_1096, h_1072 = data_clean(data)

    print("="*60)
    print("CALCULATION RESULTS (Units: m/s)")
    print("="*60)

    # --- 1. Log-Phase Calculations ---
    k_1096, vs_log_1096 = calc_log_phase_rate(time, h_1096)
    k_1072, vs_log_1072 = calc_log_phase_rate(time, h_1072)

    print(f"METHOD 1: LOG-LINEAR PHASE (First 3 Points)")
    print(f"Density 1096 Rate: {vs_log_1096:.4e} m/s")
    print(f"Density 1072 Rate: {vs_log_1072:.4e} m/s")
    print("-" * 40)

    # --- 2. Tangent Calculations ---
    vs_tan_1096, m_1096, c_1096 = calc_tangent_velocity(time, h_1096)
    vs_tan_1072, m_1072, c_1072 = calc_tangent_velocity(time, h_1072)

    print(f"METHOD 2: TANGENT LINE (Points 3 to 4: 20 -> 30 min)")
    print(f"Density 1096 Velocity: {vs_tan_1096:.4e} m/s")
    print(f"Density 1072 Velocity: {vs_tan_1072:.4e} m/s")
    print("="*60)

    # --- PLOT 1: Full Dataset ---
    plt.figure(figsize=(10, 6))
    plt.plot(time, h_1096, 'o', color='red', label='Density 1096 kg/m3', markersize=3)
    plt.plot(time, h_1072, 'o', color='purple', label='Density 1072 kg/m3', markersize=3)
    plt.xlabel('Time (s)')
    plt.ylabel('Height (m)')
    plt.title('Sedimentation Raw Data (Full Dataset)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- PLOT 2: First 6 Points Only ---
    plt.figure(figsize=(10, 6))
    plt.plot(time[:6], h_1096[:6], 'o', color='red', label='Density 1096 kg/m3', markersize=4)
    plt.plot(time[:6], h_1072[:6], 'o', color='purple', label='Density 1072 kg/m3', markersize=4)
    plt.xlabel('Time (s)')
    plt.ylabel('Height (m)')
    plt.title('Sedimentation Raw Data (First 6 Points)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- PLOT 3: Tangent Line Visualization ---
    plt.figure(figsize=(10, 6))

    # 1. Define Range for the Tangent Line (Visual extension 10min -> 40min)
    t_line = np.linspace(10*60, 40*60, 100)
    
    # 2. Calculate Line Y-values: y = mx + c
    y_line_1096 = m_1096 * t_line + c_1096
    y_line_1072 = m_1072 * t_line + c_1072

    # 3. Plot Raw Data (First 6 points only to keep it zoomed in)
    plt.plot(time[:6], h_1096[:6], 'o', color='red', label='Raw Data (1096)', markersize=5)
    plt.plot(time[:6], h_1072[:6], 'o', color='purple', label='Raw Data (1072)', markersize=5)

    # 4. Plot Tangent Lines
    plt.plot(t_line, y_line_1096, '--', color='red', alpha=0.6, linewidth=1.5, label='Tangent (20-30 min)')
    plt.plot(t_line, y_line_1072, '--', color='purple', alpha=0.6, linewidth=1.5, label='Tangent (20-30 min)')

    # 5. Highlight the points used for tangent
    plt.plot(time[2:4], h_1096[2:4], 'o', color='black', markerfacecolor='none', markersize=10, label='Points used for Tangent')
    plt.plot(time[2:4], h_1072[2:4], 'o', color='black', markerfacecolor='none', markersize=10)

    plt.xlabel('Time (s)')
    plt.ylabel('Height (m)')
    plt.title('Sedimentation Rate: Method 2 (Tangent Line 20-30 min)')
    plt.legend()
    plt.grid(True)
    plt.show()

except FileNotFoundError:
    print(f"Error: Could not find file at {file_path}. Please check the path.")
except Exception as e:
    print(f"An error occurred: {e}")
# --- 3. Data Cleaning Function ---
def data_clean(df):
    # --- EXACT TIME VALUES (Minutes) ---
    # Hardcoded from your provided list (Rows 5-47)
    time_minutes_list = [
        0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 130, 190, 288, 
        1076, 1196, 1366, 1747, 1917, 2075, 2444, 2564, 2684, 2824, 
        3078, 3198, 3390, 3817, 3978, 4270, 4580, 4763, 8230, 9576, 
        11043, 12527, 13621, 18306, 21162, 23996, 28415, 29855, 61641
    ]
    
    # Convert to numpy array and then to seconds
    time_seconds = np.array(time_minutes_list) * 60

    # --- Extract Heights ---
    # We slice the dataframe to match the length of the time array (43 points)
    # Rows 5-47 correspond to indices 4:47 in pandas (exclusive end)
    h_1096 = pd.to_numeric(df.iloc[4:47, 11], errors='coerce').values / 1000
    h_1072 = pd.to_numeric(df.iloc[4:47, 12], errors='coerce').values / 1000

    return time_minutes_list, h_1096, h_1072

# --- MAIN EXECUTION ---

# 1. Theoretical Calculations for the specific densities requested
# Assuming '1096' and '1072' refer to the fluid density in the mixture for the theoretical calc:
v_stokes_1096 = settling_velocity_stokes(rho_fluid=1096)
v_stokes_1072 = settling_velocity_stokes(rho_fluid=1072)

print(f"--- Theoretical Stokes Velocities (D=8.5um, rho_p=2620) ---")
print(f"Density 1096: {v_stokes_1096:.2e} m/s")
print(f"Density 1072: {v_stokes_1072:.2e} m/s")
print("-" * 50)

# 2. Load Data
# Update this path to your actual file location
file_path = r'C:\Users\Public\PublicProgramming\Malte\RoomyRivers\Data_tut_3.xlsx'

try:
    data = pd.read_excel(file_path, header=None)
    time, h_1096, h_1072 = data_clean(data)

# --- PLOT 1: Full Dataset (Small Points) ---
    plt.figure(figsize=(10, 6))
    
    # Added markersize=3 to make points smaller
    plt.plot(time, h_1096, 'o', color='red', label='Density 1096 kg/m3', markersize=3)
    plt.plot(time, h_1072, 'o', color='purple', label='Density 1072 kg/m3', markersize=3)

    plt.xlabel('Time (s)')
    plt.ylabel('Height (m)')
    plt.title('Sedimentation Raw Data (Full Dataset)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- PLOT 2: First 6 Points Only ---
    plt.figure(figsize=(10, 6))
    
    # Slicing the arrays to get the first 6 elements
    plt.plot(time[:6], h_1096[:6], 'o', color='red', label='Density 1096 kg/m3', markersize=4)
    plt.plot(time[:6], h_1072[:6], 'o', color='purple', label='Density 1072 kg/m3', markersize=4)

    plt.xlabel('Time (s)')
    plt.ylabel('Height (m)')
    plt.title('Sedimentation Raw Data (First 6 Points)')
    plt.legend()
    plt.grid(True)
    plt.show()

except FileNotFoundError:
    print(f"Error: Could not find file at {file_path}. Please check the path.")
except Exception as e:
    print(f"An error occurred: {e}")