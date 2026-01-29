import numpy as np

# ==========================================
# INPUT VARIABLES
# ==========================================
U_e = 1.3541933829186972         # Mean flow velocity (m/s)
h0  = 7.798        # Flow depth (m)
d50 = 0.0034         # Grain size (m)
Delta = 1.65       # Relative density
Psi_c = 0.06       # Shields parameter
Alpha_10 = 2     # Alpha value read from graph at L/h0 = 10

# Parameters for "Short Protection" Method (L/h0 < 5)
r_mixing = 0.3     # Relative turbulence intensity (standard assumption r approx 0.2 if unknown) [cite: 13, 14]
U_e_loc = 2 * U_e
# ==========================================
# 1. PRE-CALCULATIONS
# ==========================================
# Critical Velocity (Shields) [cite: 42, 44]
kr = 2 * d50
C = 18 * np.log10((12 * h0) / kr)
uc = C * np.sqrt(Psi_c * Delta * d50)

# ==========================================
# 2. ITERATIVE CALCULATION
# ==========================================
current_alpha = Alpha_10
L_req = 0
h_se = 0
tolerance = 0.001
method_used = "Iterative (Decay Formula)"

for _ in range(100):
    # A. Calculate Scour Depth [cite: 8]
    # h_se/h0 = (0.5 * alpha * u - uc) / uc
    scour_factor = (0.5 * current_alpha * U_e - uc) / uc
    h_se = h0 * scour_factor if scour_factor > 0 else 0

    # B. Calculate Required Length (1:6 slope assumption) [cite: 103]
    L_req = 6 * h_se 
    ratio_L_h = L_req / h0

    # C. CHECK: Is Length too short for this method? 
    if ratio_L_h < 5:
        method_used = "Short Protection (Local Turbulence)"
        # Switch to Method 2: Calculate alpha from mixing layer r
        # Formula: alpha = 1.5 + 5 * r [cite: 14, 86]
        current_alpha = 1.5 + 5 * r_mixing
        
        # Recalculate H_se and L one last time with this fixed alpha
        scour_factor = (0.5 * current_alpha * U_e - uc) / uc
        h_se = h0 * scour_factor if scour_factor > 0 else 0
        L_req = 6 * h_se
        ratio_L_h = L_req / h0
        break # Exit loop as this method doesn't require iteration (alpha is constant based on r)

    # D. Update Alpha (Decay formula for L/h0 > 5) [cite: 11]
    new_alpha = 1.5 + (1.57 * Alpha_10 - 2.35) * np.exp(-0.045 * ratio_L_h)

    # Convergence Check
    if np.abs(new_alpha - current_alpha) < tolerance:
        current_alpha = new_alpha
        break
    
    current_alpha = new_alpha

fc = C/40
r0 = r_mixing/fc

# C. Calculate Beta
# Term 1: Velocity influence
term1 = 3e-4 * (U_e**2) / (Delta * 9.81 * d50)

# Term 2: Turbulence influence
term2 = (0.11 + 0.75 * r0) * fc

# Arcsin calculation
beta_rad = np.arcsin(term1 + term2)
beta_deg = np.degrees(beta_rad)


# ==========================================
# FINAL RESULTS
# ==========================================
print(f"--- Final Design Results ---")
print(f"Method Used:              {method_used}")
print(f"Critical Velocity (uc):   {uc:.3f} m/s")
print(f"Final Turbulence (Alpha): {current_alpha:.3f}")
print(f"Scour Depth (h_se):       {h_se:.3f} m")
print(f"Required Bed Length (L):  {L_req:.3f} m")
print(f"Ratio L/h0:               {ratio_L_h:.2f}")
print(f"Slope Angle (Beta):        {beta_deg:.2f} degrees")

shields = 0.03
chezy = 50
delta = 1.65

## Create loop to find D50

D50_new = 0.01 #initial guess
D50 = 0.02 #initial value to enter loop

while abs(D50_new - D50) > 0.00001:
    D50 = D50_new
    k = 2*D50
    C = 18*np.log10(12*h0/k)
    D50_new = (1*U_e**2)/(1*shields*delta*C**2)

print("The median grain size before calibration is:", D50_new, "m")
print("The Chezy roughness is:", C, "m^(1/2)/s")

Ks = 1
Kv = 1.3

D50 = D50_new * (Kv**2 / Ks)

print("We use the filter CP90/180")

import numpy as np

# ==========================================
# 1. DEFINE MATERIALS
# ==========================================

# --- A. ARMOUR LAYER (CP90/180) ---
# Note: In your snippet, this was called "Filter", but it is the top Armour layer.
d50_A = 0.115      # 11.5 cm
ratio_A = 2.0      # d85/d15 from table

# Calculate Armour Distribution
factor_A = np.sqrt(ratio_A) 
d15_A = d50_A / factor_A  # Approx 0.081 m
d85_A = d50_A * factor_A  # Approx 0.163 m

# --- B. BASE MATERIAL (Riverbed Sand/Gravel) ---
d50_B = 0.0034     # 3.4 mm
d90_B = 0.01186    # 11.86 mm

# Calculate Base Distribution (Log-Normal)
# Sigma calculation derived from d90 (z=1.282)
sigma_log_B = np.log(d90_B / d50_B) / 1.282

# Calculate d85 (z=1.036) and d15 (z=-1.036)
d85_B = d50_B * np.exp(1.036 * sigma_log_B)
d15_B = d50_B * np.exp(-1.036 * sigma_log_B)

# ==========================================
# 2. CHECK 1: DIRECT PLACEMENT (Armour on Base)
# ==========================================
print(f"--- SCENARIO 1: Direct Placement (Armour on Base) ---")
print(f"Base d85:   {d85_B:.4f} m")
print(f"Armour d15: {d15_A:.4f} m")

# Stability Check (d15_Armour / d85_Base < 5)
val1 = d15_A / d85_B
print(f"Stability Check (d15A/d85B < 5):")
print(f"   {d15_A:.4f} / {d85_B:.4f} = {val1:.2f} -> {'PASS' if val1 < 5 else 'FAIL (Needs Filter!)'}")

# ==========================================
# 3. SOLUTION: INTERMEDIATE FILTER (20/40 mm)
# ==========================================
if val1 >= 5:
    print(f"\n" + "="*40)
    print(f"--- SCENARIO 2: With Intermediate Filter (20/40 mm) ---")
    print("="*40)

    # Define Filter: Coarse Aggregate 20/40 mm
    # d_lcl = 20mm, d_ucl = 40mm
    d15_F = 0.020   # 20 mm (Conservative Lower Limit)
    d85_F = 0.040   # 40 mm (Conservative Upper Limit)
    d50_F = 0.030   # 30 mm (Average)

    # Estimate Internal Stability (d60/d10) for Filter
    # Log-linear interpolation
    log_d15 = np.log10(d15_F)
    log_d85 = np.log10(d85_F)
    slope = (log_d85 - log_d15) / (85 - 15)
    d60_F = 10**(log_d15 + slope * (60 - 15))
    d10_F = 10**(log_d15 + slope * (10 - 15))

    print(f"Filter Properties (20/40 mm):")
    print(f"  d15: {d15_F:.4f} m")
    print(f"  d85: {d85_F:.4f} m")
    print("-" * 30)

    # --- INTERFACE A: BASE -> FILTER ---
    print("Check A: Base -> Filter")
    
    # Stability
    stab_A = d15_F / d85_B
    print(f"  1. Stability (d15F/d85B < 5): {stab_A:.2f} -> {'PASS' if stab_A < 5 else 'FAIL'}")
    
    # Permeability
    perm_A = d15_F / d15_B
    print(f"  2. Permeability (d15F/d15B > 5): {perm_A:.2f} -> {'PASS' if perm_A > 5 else 'FAIL'}")

    # --- INTERFACE B: FILTER -> ARMOUR ---
    print("\nCheck B: Filter -> Armour")
    
    # Stability (Armour holds Filter)
    stab_B = d15_A / d85_F
    print(f"  1. Stability (d15A/d85F < 5): {stab_B:.2f} -> {'PASS' if stab_B < 5 else 'FAIL'}")

    perm_B = d15_A / d15_F
    print(f"  2. Permeability (d15A/d15F > 5): {perm_A:.2f} -> {'PASS' if perm_B > 5 else 'FAIL'}")

    # --- INTERNAL STABILITY ---
    print("\nCheck C: Filter Internal Stability")
    int_stab = d60_F / d10_F
    print(f"  1. Ratio (d60/d10 < 10):      {int_stab:.2f} -> {'PASS' if int_stab < 10 else 'FAIL'}")

    print("-" * 30)
    if stab_A < 5 and perm_A > 5 and stab_B < 5:
        print("CONCLUSION: The 20/40 mm Filter works perfectly.")
    else:
        print("CONCLUSION: Filter adjustment needed.")