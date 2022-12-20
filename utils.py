import os

from sympy import solve  # resolver sistemas
from dotenv import load_dotenv

load_dotenv("sample.env")

verbose = os.getenv("verbose")


def comma_string_to_float(value):
    if not isinstance(value, str):
        return value
    return float(value.replace(",", "."))


def get_set_attr(cls, attr, value):
    if getattr(cls, attr) is None:
        if verbose:
            print(f"{attr}={value}")
        setattr(cls, attr, value)


def minutes_to_secconds(m):
    return m / 60


def solve_chemistry_equation(reagent, product):
    equation = reagent - product

    system_eqs = []
    for element in equation.elements():
        system_eqs.append(equation[element])

    return solve(system_eqs)


def rpm_to_rps(value):
    return value / 60


def celsius_to_kelvin(T):
    return T + 273.15