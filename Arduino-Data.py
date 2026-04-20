import serial
from datetime import datetime
from openpyxl import Workbook
import math
import os

# ---------------- SERIAL SETTINGS ----------------
PORT = "COM4"
BAUD = 9600

# ---------------- DLR PARAMETERS ----------------
D_m = 0.0143         # conductor diameter (m)
R20_km = 0.261       # resistance at 20°C (ohm/km)
alpha_R = 0.00403    # temperature coefficient
emissivity = 0.5
alpha_solar = 0.5
Tc_max = 75.0

STATIC_AMPACITY = 357.0  # Static rating (A)

# Light% -> solar irradiance
K_SOLAR = 10.0

# convection constant
K_CONV = 10.0


# ---------------- DLR FUNCTION ----------------
def compute_ampacity(Ta_C, wind_ms, G_solar_Wm2):

    R20_m = R20_km / 1000.0
    R_T = R20_m * (1.0 + alpha_R * (Tc_max - 20.0))

    if wind_ms < 0:
        wind_ms = 0.0

    qc = K_CONV * wind_ms * (Tc_max - Ta_C)

    sigma = 5.670374419e-8
    Tc_K = Tc_max + 273.15
    Ta_K = Ta_C + 273.15

    qr = sigma * emissivity * math.pi * D_m * (Tc_K**4 - Ta_K**4)

    qs = alpha_solar * G_solar_Wm2 * D_m

    net_cooling = qc + qr - qs

    if net_cooling <= 0:
        return 0.0

    I_max = math.sqrt(net_cooling / R_T)

    return I_max


# ---------------- MAIN PROGRAM ----------------
def main():

    ser = serial.Serial(PORT, BAUD, timeout=1)

    # Save file in same directory as script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    filename = os.path.join(
        script_dir,
        f"dlr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "DLR Log"

    # Excel headers
    ws.append([
        "timestamp",
        "temp_c",
        "wind_ms",
        "wind_voltage",
        "light_percent",
        "G_solar_Wm2",
        "dynamic_ampacity_A",
        "static_ampacity_A"
    ])

    print(f"Listening on {PORT} at {BAUD} baud...")
    print("Press Ctrl+C to stop.\n")

    try:

        while True:

            line = ser.readline().decode("utf-8").strip()

            if not line:
                continue

            print("RAW:", line)

            # Skip Arduino header
            if line.startswith("temp_c"):
                continue

            parts = line.split(",")

            if len(parts) != 4:
                print("Skipped malformed line")
                continue

            try:
                temp_c = float(parts[0])
                wind_ms = float(parts[1])
                wind_voltage = float(parts[2])
                light_percent = float(parts[3])

            except ValueError:
                print("Skipped non-numeric line")
                continue

            # Solar irradiance
            G_solar = max(light_percent, 0.0) * K_SOLAR

            # Compute DLR
            dyn_ampacity = compute_ampacity(temp_c, wind_ms, G_solar)

            ts = datetime.now().isoformat(timespec="seconds")

            # Write to Excel
            ws.append([
                ts,
                temp_c,
                wind_ms,
                wind_voltage,
                light_percent,
                G_solar,
                dyn_ampacity,
                STATIC_AMPACITY
            ])

            print(
                f"{ts}  T={temp_c:.1f}°C  "
                f"Light={light_percent:.1f}%  "
                f"Wind={wind_ms:.2f} m/s  "
                f"G={G_solar:.0f} W/m²  "
                f"Dyn={dyn_ampacity:.1f} A  "
                f"Static={STATIC_AMPACITY:.0f} A"
            )

    except KeyboardInterrupt:

        print("\nStopped by user.")

    finally:

        wb.save(filename)
        ser.close()

        print("\nExcel file saved at:")
        print(filename)


if __name__ == "__main__":
    main()