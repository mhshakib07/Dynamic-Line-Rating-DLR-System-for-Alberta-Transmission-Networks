import os
import sys

# ===== EDIT THESE =====
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"
sav_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"

sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

FROM_BUS = 1303
TO_BUS = 1304
CKT_ID = "05"

ierr = psspy.case(sav_file)
print("Open case ierr =", ierr)

# read branch integer data
for fld in ["STATUS", "METBUS", "NMETBUS", "OWN1", "OWN2", "OWN3", "OWN4"]:
    try:
        ierr, val = psspy.brnint(FROM_BUS, TO_BUS, CKT_ID, fld)
        print(f"{fld}: ierr={ierr}, val={val}")
    except Exception as e:
        print(f"{fld}: failed -> {e}")

# read branch real data
for fld in ["R", "X", "B", "RATEA", "RATEB", "RATEC", "LEN"]:
    try:
        ierr, val = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, fld)
        print(f"{fld}: ierr={ierr}, val={val}")
    except Exception as e:
        print(f"{fld}: failed -> {e}")