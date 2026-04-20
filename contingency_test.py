import os
import sys

# =========================================================
# 1) EDIT THESE PATHS
# =========================================================
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

BASE_CASE = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
DLR_CASE  = r"C:\Users\kibria.muttakin\Documents\DLR Project\case_dlr_1303-1304-05.sav"

BASE_OUTAGE_CASE = r"C:\Users\kibria.muttakin\Documents\DLR Project\base_case_outage_1241_1242_15.sav"
DLR_OUTAGE_CASE  = r"C:\Users\kibria.muttakin\Documents\DLR Project\dlr_case_outage_1241_1242_15.sav"

# =========================================================
# 2) TARGET LINE = line you want to monitor
# =========================================================
TARGET_FROM = 1303
TARGET_TO   = 1304
TARGET_CKT  = "05"

# =========================================================
# 3) OUTAGE LINE = milder candidate
# =========================================================
OUT_FROM = 1241
OUT_TO   = 1242
OUT_CKT  = "15"

# =========================================================
# 4) PSSE SETUP
# =========================================================
sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

_i = psspy.getdefaultint()
_f = psspy.getdefaultreal()

# =========================================================
# 5) HELPER FUNCTIONS
# =========================================================
def open_and_solve(casefile, label):
    ierr = psspy.case(casefile)
    print(f"\n{label} open ierr =", ierr)

    ierr = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0])
    print(f"{label} solve ierr =", ierr)
    return ierr

def get_branch_results(from_bus, to_bus, ckt, label):
    ierr, ratea = psspy.brndat(from_bus, to_bus, ckt, "RATEA")
    ierr, rateb = psspy.brndat(from_bus, to_bus, ckt, "RATEB")
    ierr, ratec = psspy.brndat(from_bus, to_bus, ckt, "RATEC")

    ierr, p = psspy.brnmsc(from_bus, to_bus, ckt, "P")
    ierr, q = psspy.brnmsc(from_bus, to_bus, ckt, "Q")
    ierr, pct = psspy.brnmsc(from_bus, to_bus, ckt, "PCTMVA")

    mva = (p**2 + q**2) ** 0.5

    print(f"{label} RATEA = {ratea}")
    print(f"{label} RATEB = {rateb}")
    print(f"{label} RATEC = {ratec}")
    print(f"{label} P     = {p}")
    print(f"{label} Q     = {q}")
    print(f"{label} MVA   = {mva}")
    print(f"{label} Load% = {pct}")

    return {
        "ratea": ratea,
        "rateb": rateb,
        "ratec": ratec,
        "p": p,
        "q": q,
        "mva": mva,
        "pct": pct
    }

def outage_branch_safely(from_bus, to_bus, ckt):
    ierr, rx = psspy.brndt2(from_bus, to_bus, ckt, "RX")
    if ierr != 0:
        raise RuntimeError(f"Could not read RX for outage line {from_bus}-{to_bus}-{ckt}, ierr={ierr}")

    r = rx.real
    x = rx.imag

    ierr, charg = psspy.brndat(from_bus, to_bus, ckt, "CHARG")
    if ierr != 0:
        raise RuntimeError(f"Could not read CHARG for outage line {from_bus}-{to_bus}-{ckt}, ierr={ierr}")

    # First integer = STATUS, set to 0 for out of service
    intgar = [0, _i, _i, _i, _i, _i]
    realar = [r, x, charg, _f, _f, _f]

    ierr = psspy.branch_chng(from_bus, to_bus, ckt, intgar, realar)
    print(f"Outage branch_chng ierr = {ierr}")
    return ierr

def run_contingency(casefile, savefile, label):
    open_and_solve(casefile, label)

    pre = get_branch_results(TARGET_FROM, TARGET_TO, TARGET_CKT, f"{label} PRE-OUTAGE TARGET")

    ierr = outage_branch_safely(OUT_FROM, OUT_TO, OUT_CKT)
    if ierr != 0:
        raise RuntimeError(f"Outage failed for {label}, ierr={ierr}")

    ierr = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0])
    print(f"{label} POST-OUTAGE solve ierr =", ierr)

    post = get_branch_results(TARGET_FROM, TARGET_TO, TARGET_CKT, f"{label} POST-OUTAGE TARGET")

    ierr = psspy.save(savefile)
    print(f"{label} save ierr =", ierr)

    return pre, post

# =========================================================
# 6) RUN BASE CASE CONTINGENCY
# =========================================================
base_pre, base_post = run_contingency(BASE_CASE, BASE_OUTAGE_CASE, "BASE CASE")

# =========================================================
# 7) RUN DLR CASE CONTINGENCY
# =========================================================
dlr_pre, dlr_post = run_contingency(DLR_CASE, DLR_OUTAGE_CASE, "DLR CASE")

# =========================================================
# 8) FINAL SUMMARY
# =========================================================
print("\n" + "=" * 75)
print("FINAL CONTINGENCY SUMMARY")
print("=" * 75)

print("\nTarget line monitored: 1303 -> 1304, ckt 05")
print("Outaged line:          1241 -> 1242, ckt 15")

print("\n---------------- BASE CASE ----------------")
print(f"Pre-outage RATEA   = {base_pre['ratea']}")
print(f"Pre-outage MVA     = {base_pre['mva']}")
print(f"Pre-outage Loading = {base_pre['pct']}")
print(f"Post-outage RATEA   = {base_post['ratea']}")
print(f"Post-outage MVA     = {base_post['mva']}")
print(f"Post-outage Loading = {base_post['pct']}")

print("\n---------------- DLR CASE ----------------")
print(f"Pre-outage RATEA   = {dlr_pre['ratea']}")
print(f"Pre-outage MVA     = {dlr_pre['mva']}")
print(f"Pre-outage Loading = {dlr_pre['pct']}")
print(f"Post-outage RATEA   = {dlr_post['ratea']}")
print(f"Post-outage MVA     = {dlr_post['mva']}")
print(f"Post-outage Loading = {dlr_post['pct']}")

print("\n---------------- COMPARISON ----------------")
print("Base post-outage loading =", base_post['pct'])
print("DLR  post-outage loading =", dlr_post['pct'])