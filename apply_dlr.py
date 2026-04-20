import os
import sys
import math
import pandas as pd

# ====================================
# 1. EDIT THESE PSSE PATHS
# ====================================
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

# Default placeholders
_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()
_s = psspy.getdefaultchar()

# ====================================
# 2. EDIT THESE FILE PATHS
# ====================================
sav_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
excel_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\dlr_log_20260224_172353.xlsx"
out_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\case_dlr_1303_1304_fixed.sav"

# ====================================
# 3. CHOSEN LINE
# ====================================
FROM_BUS = 1303
TO_BUS = 1304
CKT_ID = "05"
LINE_KV = 138.0

# Exact PSSE rates from your branch-data output
RATEA_OLD = 157.1666717529297
RATEB_OLD = 190.70834350585938
RATEC_OLD = 157.1666717529297

# Cap DLR at 130% of original RATEA
MAX_DLR_RATE_MVA = RATEA_OLD * 1.30

# ====================================
# 4. READ EXCEL AND PICK BEST ROW
# ====================================
df = pd.read_excel(excel_file)

best_row = df.sort_values("dynamic_ampacity_A", ascending=False).iloc[0]
dyn_ampacity_A = float(best_row["dynamic_ampacity_A"])

print("Best dynamic ampacity (A) =", dyn_ampacity_A)

# ====================================
# 5. CONVERT A TO MVA
# ====================================
dyn_mva = math.sqrt(3) * LINE_KV * (dyn_ampacity_A / 1000.0)
new_rate_mva = min(dyn_mva, MAX_DLR_RATE_MVA)

print("Old RATEA =", round(RATEA_OLD, 3))
print("Old RATEB =", round(RATEB_OLD, 3))
print("Old RATEC =", round(RATEC_OLD, 3))
print("Raw DLR MVA =", round(dyn_mva, 3))
print("New capped DLR rate =", round(new_rate_mva, 3))

# ====================================
# 6. OPEN CASE
# ====================================
ierr = psspy.case(sav_file)
print("Open case ierr =", ierr)

ierr = psspy.fnsl([0,0,0,1,1,0,99,0])
print("Base solve ierr =", ierr)

# ====================================
# 7. CHANGE ONLY THE RATINGS
# Leave all other values unchanged using defaults
# ====================================
intgar = [_i, _i, _i, _i, _i, _i]
realar = [_f, _f, _f, new_rate_mva, new_rate_mva, new_rate_mva, _f, _f, _f, _f, _f, _f]

ierr = psspy.branch_chng_3(FROM_BUS, TO_BUS, CKT_ID, intgar, realar)
print("branch_chng_3 ierr =", ierr)

# ====================================
# 8. SOLVE AGAIN
# ====================================
ierr = psspy.fnsl([0,0,0,1,1,0,99,0])
print("DLR solve ierr =", ierr)

# ====================================
# 9. SAVE NEW CASE
# ====================================
ierr = psspy.save(out_file)
print("Save ierr =", ierr)

print("DONE. New case saved.")