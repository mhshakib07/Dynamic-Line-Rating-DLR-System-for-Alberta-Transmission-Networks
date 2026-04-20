import os
import sys
import math
import pandas as pd

# =========================================================
# 1) EDIT THESE PATHS
# =========================================================
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

BASE_CASE = r"C:\Users\kibria.muttakin\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
EXCEL_FILE = r"C:\Users\kibria.muttakin\Documents\DLR Project\dlr_log_20260224_172353.xlsx"
OUTPUT_FOLDER = r"C:\Users\kibria.muttakin\Documents\DLR Project"

# =========================================================
# 2) LINES TO STUDY
# =========================================================
LINES = [
    {"from_bus": 1303, "to_bus": 1304, "ckt": "05", "kv": 138.0, "name": "1303-1304-05"},
    {"from_bus": 1241, "to_bus": 1242, "ckt": "15", "kv": 138.0, "name": "1241-1242-15"},
    {"from_bus": 1164, "to_bus": 1160, "ckt": "32", "kv": 138.0, "name": "1164-1160-32"},
]

# =========================================================
# 3) PSSE SETUP
# =========================================================
sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

_i = psspy.getdefaultint()

# =========================================================
# 4) READ BEST DLR VALUE FROM EXCEL
# =========================================================
df = pd.read_excel(EXCEL_FILE)
best_row = df.sort_values("dynamic_ampacity_A", ascending=False).iloc[0]
dyn_ampacity_A = float(best_row["dynamic_ampacity_A"])

print("Best dynamic ampacity from Excel (A) =", dyn_ampacity_A)
print()

# =========================================================
# 5) HELPER FUNCTIONS
# =========================================================
def open_and_solve(casefile, label):
    ierr = psspy.case(casefile)
    print(f"{label} open ierr =", ierr)

    ierr = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0])
    print(f"{label} solve ierr =", ierr)
    return ierr

def get_branch_results(from_bus, to_bus, ckt):
    ierr, ratea = psspy.brndat(from_bus, to_bus, ckt, "RATEA")
    ierr, rateb = psspy.brndat(from_bus, to_bus, ckt, "RATEB")
    ierr, ratec = psspy.brndat(from_bus, to_bus, ckt, "RATEC")

    ierr, p = psspy.brnmsc(from_bus, to_bus, ckt, "P")
    ierr, q = psspy.brnmsc(from_bus, to_bus, ckt, "Q")
    ierr, pct = psspy.brnmsc(from_bus, to_bus, ckt, "PCTMVA")

    mva = (p**2 + q**2) ** 0.5

    return {
        "ratea": ratea,
        "rateb": rateb,
        "ratec": ratec,
        "p": p,
        "q": q,
        "mva": mva,
        "pct": pct
    }

def apply_dlr_to_line(base_case, line, dyn_ampacity_A, output_folder):
    from_bus = line["from_bus"]
    to_bus = line["to_bus"]
    ckt = line["ckt"]
    kv = line["kv"]
    name = line["name"]

    print("=" * 70)
    print(f"Processing line: {name}")

    # ---- Base case results ----
    open_and_solve(base_case, "BASE")

    base_res = get_branch_results(from_bus, to_bus, ckt)

    print("Base RATEA =", base_res["ratea"])
    print("Base RATEB =", base_res["rateb"])
    print("Base RATEC =", base_res["ratec"])
    print("Base MVA   =", base_res["mva"])
    print("Base %Load =", base_res["pct"])

    # ---- Read branch electrical data ----
    ierr, rx = psspy.brndt2(from_bus, to_bus, ckt, "RX")
    if ierr != 0:
        raise RuntimeError(f"Could not read RX for line {name}, ierr={ierr}")

    r = rx.real
    x = rx.imag

    ierr, charg = psspy.brndat(from_bus, to_bus, ckt, "CHARG")
    if ierr != 0:
        raise RuntimeError(f"Could not read CHARG for line {name}, ierr={ierr}")

    # ---- Convert DLR A -> MVA ----
    dyn_mva = math.sqrt(3) * kv * (dyn_ampacity_A / 1000.0)

    # Cap at 130% of original RATEA
    new_rate = min(dyn_mva, base_res["ratea"] * 1.30)

    print("Raw DLR MVA        =", dyn_mva)
    print("Capped DLR RATEA   =", new_rate)

    # ---- Re-open base case before modification ----
    open_and_solve(base_case, "RELOAD")

    intgar = [_i, _i, _i, _i, _i, _i]
    realar = [r, x, charg, new_rate, new_rate, new_rate]

    ierr = psspy.branch_chng(from_bus, to_bus, ckt, intgar, realar)
    print("branch_chng ierr =", ierr)
    if ierr != 0:
        raise RuntimeError(f"branch_chng failed for line {name}, ierr={ierr}")

    # ---- Confirm new ratings ----
    ierr, new_ratea = psspy.brndat(from_bus, to_bus, ckt, "RATEA")
    ierr, new_rateb = psspy.brndat(from_bus, to_bus, ckt, "RATEB")
    ierr, new_ratec = psspy.brndat(from_bus, to_bus, ckt, "RATEC")

    print("NEW RATEA =", new_ratea)
    print("NEW RATEB =", new_rateb)
    print("NEW RATEC =", new_ratec)

    # ---- Solve DLR case ----
    ierr = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0])
    print("DLR solve ierr =", ierr)
    if ierr != 0:
        raise RuntimeError(f"DLR solve failed for line {name}, ierr={ierr}")

    dlr_res = get_branch_results(from_bus, to_bus, ckt)

    print("DLR RATEA =", dlr_res["ratea"])
    print("DLR MVA   =", dlr_res["mva"])
    print("DLR %Load =", dlr_res["pct"])

    # ---- Save line-specific output case ----
    out_file = os.path.join(output_folder, f"case_dlr_{name}.sav")
    ierr = psspy.save(out_file)
    print("Save ierr =", ierr)
    if ierr != 0:
        raise RuntimeError(f"Save failed for line {name}, ierr={ierr}")

    return {
        "line": name,
        "from_bus": from_bus,
        "to_bus": to_bus,
        "ckt": ckt,
        "kv": kv,
        "base_ratea": base_res["ratea"],
        "base_mva": base_res["mva"],
        "base_pct": base_res["pct"],
        "dlr_ratea": dlr_res["ratea"],
        "dlr_mva": dlr_res["mva"],
        "dlr_pct": dlr_res["pct"],
        "saved_case": out_file
    }

# =========================================================
# 6) RUN FOR ALL LINES
# =========================================================
summary = []

for line in LINES:
    try:
        result = apply_dlr_to_line(BASE_CASE, line, dyn_ampacity_A, OUTPUT_FOLDER)
        summary.append(result)
    except Exception as e:
        print(f"\nERROR for line {line['name']}: {e}\n")

# =========================================================
# 7) FINAL SUMMARY TABLE
# =========================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

if summary:
    print(f"{'Line':<18} {'kV':>6} {'Base RATEA':>12} {'DLR RATEA':>12} {'Base %':>10} {'DLR %':>10}")
    for r in summary:
        print(
            f"{r['line']:<18} "
            f"{r['kv']:>6.1f} "
            f"{r['base_ratea']:>12.2f} "
            f"{r['dlr_ratea']:>12.2f} "
            f"{r['base_pct']:>10.2f} "
            f"{r['dlr_pct']:>10.2f}"
        )

    print("\nSaved cases:")
    for r in summary:
        print(r["saved_case"])
else:
    print("No successful line results.")