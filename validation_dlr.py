import os
import sys
import math

# =========================================================
# 1) EDIT THESE PATHS
# =========================================================
PSSE_PY_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSPY37"
PSSE_BIN_PATH = r"C:\Program Files\PTI\PSSE35\35.0\PSSBIN"

BENCHMARK_CASE = r"C:\Users\monjurul.haque\Documents\DLR Project\2021RC_2025SP_South-High_Tie-Econ_Solar-0.95_p.sav"
TEST_CASE      = r"C:\Users\monjurul.haque\Documents\DLR Project\case_dlr_1241-1242-15.sav"

# =========================================================
# 2) CHOOSE WHAT TO VALIDATE
# =========================================================
# Buses: voltage magnitude comparison
BUSES_TO_CHECK = [1241, 1242, 1164, 1160]

# Branches: MVA flow / loading / rating comparison
BRANCHES_TO_CHECK = [
    {"from_bus": 1241, "to_bus": 1242, "ckt": "15", "name": "1241-1242-15"},
    {"from_bus": 1164, "to_bus": 1160, "ckt": "32", "name": "1164-1160-32"},
]

THRESHOLD_PERCENT = 1.0

# =========================================================
# 3) PSSE SETUP
# =========================================================
sys.path.append(PSSE_PY_PATH)
os.environ["PATH"] += ";" + PSSE_BIN_PATH

import psspy
import redirect

redirect.psse2py()
psspy.psseinit(14000)

# =========================================================
# 4) HELPERS
# =========================================================
def pct_error(ref, test):
    """Relative percent error. Handles near-zero safely."""
    if abs(ref) < 1e-9:
        return 0.0 if abs(test) < 1e-9 else float("inf")
    return abs((test - ref) / ref) * 100.0

def open_and_solve(casefile, label):
    ierr = psspy.case(casefile)
    print(f"{label} open ierr = {ierr}")

    ierr = psspy.fnsl([0, 0, 0, 1, 1, 0, 99, 0])
    print(f"{label} solve ierr = {ierr}")
    return ierr

def get_bus_voltage(busnum):
    ierr, pu = psspy.busdat(busnum, "PU")
    if ierr != 0:
        raise RuntimeError(f"Could not read bus voltage for bus {busnum}, ierr={ierr}")
    return pu

def get_branch_data(from_bus, to_bus, ckt):
    ierr, ratea = psspy.brndat(from_bus, to_bus, ckt, "RATEA")
    ierr2, rateb = psspy.brndat(from_bus, to_bus, ckt, "RATEB")
    ierr3, ratec = psspy.brndat(from_bus, to_bus, ckt, "RATEC")
    ierr4, p = psspy.brnmsc(from_bus, to_bus, ckt, "P")
    ierr5, q = psspy.brnmsc(from_bus, to_bus, ckt, "Q")
    ierr6, pct = psspy.brnmsc(from_bus, to_bus, ckt, "PCTMVA")

    if any(i != 0 for i in [ierr, ierr2, ierr3, ierr4, ierr5, ierr6]):
        raise RuntimeError(
            f"Could not read branch data for {from_bus}-{to_bus}-{ckt}, "
            f"ierrs={[ierr, ierr2, ierr3, ierr4, ierr5, ierr6]}"
        )

    mva = math.sqrt(p ** 2 + q ** 2)

    return {
        "ratea": ratea,
        "rateb": rateb,
        "ratec": ratec,
        "p": p,
        "q": q,
        "mva": mva,
        "pct": pct,
    }

def read_case_snapshot(casefile, label):
    open_and_solve(casefile, label)

    bus_data = {}
    for bus in BUSES_TO_CHECK:
        bus_data[bus] = {
            "vpu": get_bus_voltage(bus)
        }

    branch_data = {}
    for br in BRANCHES_TO_CHECK:
        key = (br["from_bus"], br["to_bus"], br["ckt"])
        branch_data[key] = get_branch_data(br["from_bus"], br["to_bus"], br["ckt"])

    return bus_data, branch_data

# =========================================================
# 5) READ BOTH CASES
# =========================================================
benchmark_buses, benchmark_branches = read_case_snapshot(BENCHMARK_CASE, "BENCHMARK")
test_buses, test_branches = read_case_snapshot(TEST_CASE, "TEST")

# =========================================================
# 6) VALIDATE BUSES
# =========================================================
print("\n" + "=" * 80)
print("BUS VOLTAGE VALIDATION AGAINST 1% THRESHOLD")
print("=" * 80)

bus_pass_all = True

print(f"{'Bus':<10} {'Benchmark PU':>15} {'Test PU':>15} {'Error %':>12} {'Status':>10}")
for bus in BUSES_TO_CHECK:
    ref_v = benchmark_buses[bus]["vpu"]
    tst_v = test_buses[bus]["vpu"]
    err = pct_error(ref_v, tst_v)
    status = "PASS" if err <= THRESHOLD_PERCENT else "FAIL"
    if status == "FAIL":
        bus_pass_all = False

    print(f"{bus:<10} {ref_v:>15.6f} {tst_v:>15.6f} {err:>12.4f} {status:>10}")

# =========================================================
# 7) VALIDATE BRANCHES
# =========================================================
print("\n" + "=" * 80)
print("BRANCH VALIDATION AGAINST 1% THRESHOLD")
print("=" * 80)

branch_pass_all = True

for br in BRANCHES_TO_CHECK:
    key = (br["from_bus"], br["to_bus"], br["ckt"])
    ref = benchmark_branches[key]
    tst = test_branches[key]

    err_mva = pct_error(ref["mva"], tst["mva"])
    err_pct = pct_error(ref["pct"], tst["pct"])
    err_ratea = pct_error(ref["ratea"], tst["ratea"])

    # For DLR studies:
    # - MVA should usually remain close if dispatch/topology unchanged
    # - Loading % and RATEA are expected to change after DLR
    # So benchmark the right things depending on your goal.
    print(f"\nBranch: {br['name']} ({br['from_bus']}->{br['to_bus']}, ckt {br['ckt']})")
    print(f"  Benchmark RATEA = {ref['ratea']:.6f}")
    print(f"  Test RATEA      = {tst['ratea']:.6f}")
    print(f"  RATEA Error %   = {err_ratea:.4f}")
    print(f"  Benchmark MVA   = {ref['mva']:.6f}")
    print(f"  Test MVA        = {tst['mva']:.6f}")
    print(f"  MVA Error %     = {err_mva:.4f}")
    print(f"  Benchmark %Load = {ref['pct']:.6f}")
    print(f"  Test %Load      = {tst['pct']:.6f}")
    print(f"  %Load Error %   = {err_pct:.4f}")

    # Use MVA as the real steady-state benchmark check
    status_mva = "PASS" if err_mva <= THRESHOLD_PERCENT else "FAIL"
    print(f"  MVA 1% Check    = {status_mva}")
    if status_mva == "FAIL":
        branch_pass_all = False

# =========================================================
# 8) FINAL DECISION
# =========================================================
print("\n" + "=" * 80)
print("FINAL VALIDATION SUMMARY")
print("=" * 80)

print(f"Bus voltage 1% validation  : {'PASS' if bus_pass_all else 'FAIL'}")
print(f"Branch MVA 1% validation   : {'PASS' if branch_pass_all else 'FAIL'}")

overall = bus_pass_all and branch_pass_all
print(f"Overall benchmark result   : {'PASS' if overall else 'FAIL'}")