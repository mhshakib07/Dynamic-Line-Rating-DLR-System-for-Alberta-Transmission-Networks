import pandas as pd

excel_file = r"C:\Users\kibria.muttakin\Documents\DLR Project\dlr_log_20260224_172353.xlsx"

df = pd.read_excel(excel_file)

print("COLUMNS:")
print(df.columns.tolist())
print()

print("MAX dynamic_ampacity_A =", df["dynamic_ampacity_A"].max())
print()

top10 = df.sort_values("dynamic_ampacity_A", ascending=False)[
    ["timestamp", "temp_c", "light_percent", "wind_ms", "dynamic_ampacity_A", "static_ampacity_A", "extra_margin_A"]
].head(10)

print("TOP 10 ROWS BY dynamic_ampacity_A:")
print(top10.to_string(index=False))