import os
import sys
import math
import pandas as pd

# ==============================
# EDIT THESE PATHS
# ==============================
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

sav_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
excel_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\dlr_log_20260224_172353.xlsx"
out_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\case_dlr_1303_1304_final.sav"

sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

_i = psspy.getdefaultint()

FROM_BUS = 1303
TO_BUS = 1304
CKT_ID = "05"
LINE_KV = 138.0

# -----------------------------
# Read Excel and get best DLR row
# -----------------------------
df = pd.read_excel(excel_file)
best_row = df.sort_values("dynamic_ampacity_A", ascending=False).iloc[0]
dyn_ampacity_A = float(best_row["dynamic_ampacity_A"])

# -----------------------------
# Open base case
# -----------------------------
ierr = psspy.case(sav_file)
print("Open case ierr =", ierr)

ierr = psspy.fnsl([0,0,0,1,1,0,99,0])
print("Base solve ierr =", ierr)

# -----------------------------
# Read existing line data
# -----------------------------
ierr, rx = psspy.brndt2(FROM_BUS, TO_BUS, CKT_ID, "RX")
print("RX ierr =", ierr, " value =", rx)

r = rx.real
x = rx.imag

ierr, charg = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "CHARG")
print("CHARG ierr =", ierr, " value =", charg)

ierr, ratea_old = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEA")
ierr, rateb_old = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEB")
ierr, ratec_old = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEC")

print("Old RATEA =", ratea_old)
print("Old RATEB =", rateb_old)
print("Old RATEC =", ratec_old)

# -----------------------------
# Convert DLR A -> MVA
# -----------------------------
dyn_mva = math.sqrt(3) * LINE_KV * (dyn_ampacity_A / 1000.0)

# cap at 130% of old RATEA
new_rate = min(dyn_mva, ratea_old * 1.30)

print("Best dynamic ampacity A =", dyn_ampacity_A)
print("Raw DLR MVA =", dyn_mva)
print("New capped DLR rate =", new_rate)

# -----------------------------
# Change line rating using branch_chng
# Keep R, X, CHARG same
# -----------------------------
intgar = [_i, _i, _i, _i, _i, _i]
realar = [r, x, charg, new_rate, new_rate, new_rate]

ierr = psspy.branch_chng(FROM_BUS, TO_BUS, CKT_ID, intgar, realar)
print("branch_chng ierr =", ierr)

# -----------------------------
# Read back the new ratings immediately
# -----------------------------
ierr, ratea_new = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEA")
ierr, rateb_new = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEB")
ierr, ratec_new = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEC")

print("NEW RATEA =", ratea_new)
print("NEW RATEB =", rateb_new)
print("NEW RATEC =", ratec_new)

# -----------------------------
# Solve again
# -----------------------------
ierr = psspy.fnsl([0,0,0,1,1,0,99,0])
print("DLR solve ierr =", ierr)

# -----------------------------
# Save
# -----------------------------
ierr = psspy.save(out_file)
print("Save ierr =", ierr)

print("DONE")