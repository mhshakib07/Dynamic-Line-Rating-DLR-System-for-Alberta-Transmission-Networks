import os
import sys

PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

base_case = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
dlr_case  = r"C:\Users\kibria.muttakin\Documents\DLR Project\case_dlr_1303_1304_final.sav"

FROM_BUS = 1303
TO_BUS = 1304
CKT_ID = "05"

sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

def get_data(casefile, label):
    ierr = psspy.case(casefile)
    print(f"\n{label} open ierr =", ierr)

    ierr = psspy.fnsl([0,0,0,1,1,0,99,0])
    print(f"{label} solve ierr =", ierr)

    ierr, ratea = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEA")
    ierr, rateb = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEB")
    ierr, ratec = psspy.brndat(FROM_BUS, TO_BUS, CKT_ID, "RATEC")

    ierr, p = psspy.brnmsc(FROM_BUS, TO_BUS, CKT_ID, "P")
    ierr, q = psspy.brnmsc(FROM_BUS, TO_BUS, CKT_ID, "Q")
    ierr, pct = psspy.brnmsc(FROM_BUS, TO_BUS, CKT_ID, "PCTMVA")

    mva = (p**2 + q**2) ** 0.5

    print(f"{label} RATEA = {ratea}")
    print(f"{label} RATEB = {rateb}")
    print(f"{label} RATEC = {ratec}")
    print(f"{label} P = {p}")
    print(f"{label} Q = {q}")
    print(f"{label} MVA = {mva}")
    print(f"{label} Loading % = {pct}")

    return ratea, mva, pct

base_rate, base_mva, base_pct = get_data(base_case, "BASE")
dlr_rate, dlr_mva, dlr_pct = get_data(dlr_case, "DLR")

print("\n========== FINAL COMPARISON ==========")
print("Base RATEA   =", base_rate)
print("DLR  RATEA   =", dlr_rate)
print("Base MVA     =", base_mva)
print("DLR  MVA     =", dlr_mva)
print("Base Loading =", base_pct)
print("DLR  Loading =", dlr_pct)