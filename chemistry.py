import re
import pandas as pd  # manipular tabelas

import pyromat as pm  # propriedades térmicas
from scipy.interpolate import interp1d  # interpolação

from utils import comma_string_to_float, celsius_to_kelvin, get_set_attr

pm.config["unit_pressure"] = "kPa"

AIR = "ig.air"
ANHYDROUS = "ig.C2H6O"
CARBON_DIOXIDE = "ig.CO2"
N2 = "ig.N2"
O2 = "ig.O2"
OCTANE = "ig.C8H18"
WATER = "ig.H2O"

substances_map = {
    CARBON_DIOXIDE: "Carbon Dioxide (CO2)",
    N2: "Nitrogen (N2)",
    O2: "Oxygen (O2)",
    WATER: "Water (H2O)",
}

h_form = {OCTANE: -249.92, ANHYDROUS: -277.8, O2: 0, N2: 0, CARBON_DIOXIDE: -393.52, WATER: -241.82}

mol_mass_dict = {ANHYDROUS: 46.0681, N2: 28.16, O2: 32, OCTANE: 114.22}

# chamando tabela shapiro

shapiro_a23 = pd.read_csv("Tabelas Shapiro - A23.csv", skiprows=[1, 2], index_col="Temperature (K)")
shapiro_a23.columns = list(map(lambda col_name: re.sub(r"\s+", " ", col_name), shapiro_a23.columns))
for col in shapiro_a23.columns:
    shapiro_a23[col] = shapiro_a23[col].map(comma_string_to_float)


class EmptyMolecule:
    _d = None

    def set_property(self, prop, value):
        if not prop.startswith("_"):
            prop = "_" + prop
        setattr(self, prop, value)

    def T(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def p(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def v(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def h(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def d(self, *args, **kwargs):
        if self._d is not None:
            return [self._d]
        raise Exception("Method not implemented.")

    def mw(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def cp(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def cv(self, *args, **kwargs):
        raise Exception("Method not implemented.")

    def h_form(self, *args, **kwargs):
        raise Exception("Method not implemented.")


class Molecule(object):
    elements_list = ["C", "N", "O", "H"]
    not_element_keys = ["name"]
    _d = None
    __pm = EmptyMolecule()

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            subs_name = args[0]
        else:
            subs_name = kwargs.get("name")
        self.__set_atoms(**kwargs)
        if subs_name is not None:
            self.__set_element(subs_name)

    def __set_atoms(self, **kwargs):
        for element in self.elements_list.copy():
            setattr(self, element, kwargs.get(element, 0))
            if element in kwargs:
                kwargs.pop(element)
        for key in kwargs:
            if key not in self.not_element_keys:
                raise Exception(f"The key {key} is not a chemistry element")

    def __set_element(self, name):
        self.name = name
        self.__pm = pm.get(name)
        if name in substances_map:
            self.__enthalpy_from_temperature = interp1d(shapiro_a23.index, shapiro_a23[substances_map[name]].values)
        if len(self.elements()) == 0:
            self.__set_atoms(**self.__pm.atoms())

    def set_element(self, name):
        self.__set_element(name)

    def set_property(self, prop, value):
        if isinstance(self.__pm, EmptyMolecule):
            self.__pm.set_property(prop, value)
        else:
            if not prop.startswith("_"):
                prop = "_" + prop
            setattr(self, prop, value)

    #             raise Exception("It is not possible to set property on defined molecule.")

    def T(self, *args, **kwargs):
        return self.__pm.T(*args, **kwargs)

    def p(self, *args, **kwargs):
        return self.__pm.p(*args, **kwargs)

    def v(self, *args, **kwargs):
        return self.__pm.v(*args, **kwargs)

    def h(self, T, source="pm"):
        if source == "shapiro":
            return [float(self.__enthalpy_from_temperature(T))]
        if source == "pm":
            return self.__pm.h(T)

    def h_form(self, *args, **kwargs):
        return h_form[self.name]

    def h_abs(self, T_ref=None, T_des=None, product=False):
        delta = 0
        if product:
            h_ref = self.h(T=celsius_to_kelvin(float(T_ref)), source="shapiro")[0]
            h_des = self.h(T=float(T_des), source="shapiro")[0]
            delta = h_des - h_ref
        return self.h_form() + delta

    def mw(self, source="pm", *args, **kwargs):
        if source == "shapiro":
            return mol_mass_dict[self.name]
        if source == "pm":
            return self.__pm.mw(*args, **kwargs)

    def cp(self, *args, **kwargs):
        return self.__pm.cp(*args, **kwargs)

    def cv(self, *args, **kwargs):
        return self.__pm.cv(*args, **kwargs)

    def d(self, source="pm", *args, **kwargs):
        value = self.__pm.d(*args, **kwargs)
        get_set_attr(self, "_d", value)
        if not isinstance(self._d, list):
            self._d = [float(self._d)]
        return self._d

    def __mul__(self, other):
        result = self.elements_dict.copy()
        for element in result:
            result[element] *= other
        return Molecule(**result)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        result = self.elements_dict.copy()
        for element in result:
            result[element] += other.elements_dict[element]
        return Molecule(**result)

    def __sub__(self, other):
        return self.__add__(-1 * other)

    def __getitem__(self, value):
        return self.elements_dict[value]

    def __repr__(self):
        return str(self.elements())

    @property
    def elements_dict(self):
        elements = self.__dict__
        return {key: elements[key] for key in elements if key in self.elements_list}

    def elements(self):
        elements = self.elements_dict.copy()
        for element in elements.copy():
            if elements[element] == 0:
                elements.pop(element)
        return elements


octane = Molecule(OCTANE)
anhydrous = Molecule(ANHYDROUS)
oxygen = Molecule(O2)
carbon_dioxide = Molecule(CARBON_DIOXIDE)
water = Molecule(WATER)
nitrogen = Molecule(N2)