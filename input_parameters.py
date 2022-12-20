import os
from dotenv import load_dotenv

load_dotenv("sample.env")

n = float(os.getenv("n", ""))
z = float(os.getenv("z", ""))
x = float(os.getenv("x", ""))
rv = float(os.getenv("rv", ""))
T1 = float(os.getenv("T1", ""))
p1 = float(os.getenv("p1", ""))
Vd = float(os.getenv("Vd", ""))
fuel_pci = float(os.getenv("fuel_pci", ""))
rho_fuel = float(os.getenv("rho_fuel", ""))
W_rate = float(os.getenv("W_rate", ""))
m_comb = float(os.getenv("m_comb", ""))
octane_ratio = float(os.getenv("octane_ratio", ""))
anhydrous_ratio = float(os.getenv("anhydrous_ratio", ""))
nitrogen_oxygen_ratio = float(os.getenv("nitrogen_oxygen_ratio", ""))
