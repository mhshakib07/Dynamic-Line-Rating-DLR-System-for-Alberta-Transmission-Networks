report_file = report_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\report-allbus.txt"

current_bus = None
current_bus_name = None
current_bus_kv = None

results = []

with open(report_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        s = line.strip()

        # Detect BUS header
        # Example:
        # BUS 76502 B23S_01_2 34.500 CKT ...
        if s.startswith("BUS"):
            parts = s.split()
            if len(parts) >= 5 and parts[0] == "BUS":
                try:
                    current_bus = int(parts[1])
                    current_bus_kv = float(parts[3])
                    current_bus_name = parts[2]
                except:
                    current_bus = None
                    current_bus_name = None
                    current_bus_kv = None
            continue

        # Detect branch rows
        # Example:
        # TO 533 VICTORIA 69.000 21 12.6 1.8 12.7 17 ...
        if s.startswith("TO") and current_bus is not None:
            parts = s.split()

            # Skip non-branch rows
            if len(parts) < 9:
                continue
            if parts[1] in ["LOAD-PQ", "GENERATION", "SWITCHED"]:
                continue
            if not parts[1].isdigit():
                continue

            try:
                to_bus = int(parts[1])
                to_name = parts[2]
                to_kv = float(parts[3])
                ckt = parts[4]
                mw = float(parts[5])
                mvar = float(parts[6])
                mva = float(parts[7])
                pct = float(parts[8])

                # Keep transmission-level branches only
                if current_bus_kv >= 69 and to_kv >= 69:
                    results.append({
                        "from_bus": current_bus,
                        "from_name": current_bus_name,
                        "from_kv": current_bus_kv,
                        "to_bus": to_bus,
                        "to_name": to_name,
                        "to_kv": to_kv,
                        "ckt": ckt,
                        "mw": mw,
                        "mvar": mvar,
                        "mva": mva,
                        "pct": pct
                    })
            except:
                continue

# Sort by highest loading
results.sort(key=lambda x: x["pct"], reverse=True)

print(f"Total candidate branches found: {len(results)}\n")
print("Top 30 loaded branches:\n")

for r in results[:30]:
    print(
        f"{r['from_bus']} {r['from_name']} ({r['from_kv']} kV) -> "
        f"{r['to_bus']} {r['to_name']} ({r['to_kv']} kV), "
        f"ckt={r['ckt']}, MVA={r['mva']}, loading={r['pct']}%"
    )