from engine import Engine
from input_parameters import n, octane_ratio, anhydrous_ratio, nitrogen_oxygen_ratio


engine = Engine(n=n, octane_ratio=octane_ratio, anhydrous_ratio=anhydrous_ratio, nitrogen_oxygen_ratio=nitrogen_oxygen_ratio)
engine.thermic_efficiency
