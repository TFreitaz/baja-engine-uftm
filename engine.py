import numpy as np  # ferramentas matemáticas

from sympy import symbols  # resolver sistemas

from stage import Stage
from utils import get_set_attr, solve_chemistry_equation, minutes_to_secconds, rpm_to_rps
from chemistry import carbon_dioxide, water, nitrogen, oxygen, AIR, octane, anhydrous, OCTANE
from input_parameters import n, z, x, rv, T1, p1, Vd, fuel_pci, rho_fuel, W_rate, m_comb


class IdealCycle:
    fuel = None
    q23 = None
    _q41 = None
    _w = None
    _w12 = None
    _w34 = None
    _stage1 = None
    _stage2 = None
    _stage3 = None
    _stage4 = None
    _k = None
    __verbose = False

    def __init__(self, fuel, T1, p1, q23, verbose=False):
        self.fuel = fuel
        self.q23 = q23
        self.__verbose = verbose
        self.__set_stage_1(T1, p1)

    @property
    def k(self):
        if self._k is None:
            self._k = self.fuel.cp()[0] / self.fuel.cv()[0]
        return self._k

    def __set_stage_1(self, T1, p1):
        self.stage1 = Stage(1, T=T1, p=p1, verbose=self.__verbose)
        self.stage1.set_property_function("v", lambda cls: self.fuel.v(cls.T, cls.p)[0])

    @property
    def stage2(self):
        if self._stage2 is None:
            self._stage2 = Stage(2, verbose=self.__verbose)
            self._stage2.set_property_function("v", lambda cls: self.stage1.v / rv)
            self._stage2.set_property_function("p", lambda cls: self.stage1.p * (self.stage1.v / cls.v) ** self.k)
            self._stage2.set_property_function("T", lambda cls: self.fuel.T(p=cls.p, v=cls.v)[0])
        return self._stage2

    @property
    def stage3(self):
        if self._stage3 is None:
            self._stage3 = Stage(3, verbose=self.__verbose)
            self._stage3.set_property_function("v", lambda cls: self.stage2.v)
            self._stage3.set_property_function("T", lambda cls: self.q23 / self.fuel.cv()[0] + self.stage2.T)
            self._stage3.set_property_function("p", lambda cls: self.fuel.p(T=cls.T, v=cls.v)[0])
        return self._stage3

    @property
    def stage4(self):
        if self._stage4 is None:
            self._stage4 = Stage(4, verbose=self.__verbose)
            self._stage4.set_property_function("v", lambda cls: self.stage1.v)
            self._stage4.set_property_function("p", lambda cls: self.stage3.p * (self.stage3.v / cls.v) ** self.k)
            self._stage4.set_property_function("T", lambda cls: self.fuel.T(p=cls.p, v=cls.v)[0])
        return self._stage4

    @property
    def w12(self):
        value = self.fuel.cv()[0] * (self.stage1.T - self.stage2.T)
        get_set_attr(self, "_w12", value)
        return self._w12

    @property
    def w34(self):
        value = self.fuel.cv()[0] * (self.stage3.T - self.stage4.T)
        get_set_attr(self, "_w34", value)
        return self._w34

    @property
    def w(self):
        value = self.w12 + self.w34
        get_set_attr(self, "_w", value)
        return self._w

    @property
    def q41(self):
        value = self.fuel.cv()[0] * (self.stage1.T - self.stage4.T)
        get_set_attr(self, "_q41", value)
        return self._q41


class Engine:
    _fuel = None
    _air = None
    _reagent = None
    _product = None
    _n_air = None
    _n_carbon_dioxide = None
    _n_water = None
    _n_nitrogen = None
    _ac_mol = None
    _ac_mass = None
    _v_air = None
    _v_fuel = None
    _v_total = None
    _v_perc_fuel = None
    _v_fuel_cilinder = None
    _m_fuel = None
    _m_adm_rate = None
    _cycle = None
    _q23 = None
    _q_rate = None
    _ni = None
    _thermic_efficiency = None
    _q_fuel_rate = None
    _real_thermic_efficiency = None
    _global_efficiency = None
    _effective_efficiency = None

    def __init__(self, n, octane_ratio, anhydrous_ratio, nitrogen_oxygen_ratio):
        self.n = n
        self.octane_ratio = octane_ratio
        self.anhydrous_ratio = anhydrous_ratio
        self.nitrogen_oxygen_ratio = nitrogen_oxygen_ratio

    @property
    def cycle(self):
        value = IdealCycle(self.air, T1, p1, self.q23)
        get_set_attr(self, "_cycle", value)
        return self._cycle

    @property
    def reagent(self):
        value = self.fuel + symbols("a") * self.air
        get_set_attr(self, "_reagent", value)
        return self._reagent

    @property
    def product(self):
        value = symbols("b") * carbon_dioxide + symbols("c") * water + symbols("d") * nitrogen
        get_set_attr(self, "_product", value)
        return self._product

    @property
    def air(self):
        value = oxygen + self.nitrogen_oxygen_ratio * nitrogen
        get_set_attr(self, "_air", value)
        self._air.set_element(AIR)
        self._air.set_property("d", 1.2041)
        return self._air

    def set_chemistry_coefficients(self):
        self._n_air, self._n_carbon_dioxide, self._n_water, self._n_nitrogen = solve_chemistry_equation(
            self.reagent, self.product
        ).values()

    @property
    def fuel(self):
        if self._fuel is None:
            self._fuel = self.octane_ratio * octane + self.anhydrous_ratio * anhydrous
            self._fuel.set_element(OCTANE)
            self._fuel.set_property("d", 743.2)
        return self._fuel

    @property
    def q23(self):
        if self._q23 is None:
            self._q23 = self.m_adm_rate * fuel_pci
        return self._q23

    @property
    def v_perc_fuel(self):
        value = self.v_fuel / self.v_total
        get_set_attr(self, "_v_perc_fuel", value)
        return self._v_perc_fuel

    @property
    def v_total(self):
        value = self.v_fuel + self.v_air
        get_set_attr(self, "_v_total", value)
        return self._v_total

    @property
    def v_fuel(self):
        value = 1 / rho_fuel
        get_set_attr(self, "_v_fuel", value)
        return self._v_fuel

    @property
    def v_air(self):
        value = self.ac_mass / self.air.d()[0]
        get_set_attr(self, "_v_air", value)
        return self._v_air

    @property
    def ac_mass(self):
        a = self.n_air * oxygen.mw()  # mw = 31.9988
        b = self.n_nitrogen * nitrogen.mw()  # mw = 28.01348
        c = self.octane_ratio * octane.mw()  # mw = 114.23092
        d = self.anhydrous_ratio * anhydrous.mw()  # mw = 46.06904
        value = (a + b) / (c + d)
        get_set_attr(self, "_ac_mass", value)
        return self._ac_mass

    @property
    def ac_mol(self):
        value = self.n_air + (self.n_air * self.nitrogen_oxygen_ratio)
        get_set_attr(self, "_ac_mol", value)
        return self._ac_mol

    @property
    def n_air(self):
        if self._n_air is None:
            self.set_chemistry_coefficients()
        return self._n_air

    @property
    def n_nitrogen(self):
        if self._n_nitrogen is None:
            self.set_chemistry_coefficients()
        return self._n_nitrogen

    @property
    def n_water(self):
        if self._n_water is None:
            self.set_chemistry_coefficients()
        return self._n_water

    @property
    def n_carbon_dioxide(self):
        if self._n_carbon_dioxide is None:
            self.set_chemistry_coefficients()
        return self._n_carbon_dioxide

    @property
    def v_fuel_cilinder(self):
        value = Vd * self.v_perc_fuel
        get_set_attr(self, "_v_fuel_cilinder", value)
        return self._v_fuel_cilinder

    @property
    def m_fuel(self):
        value = self.fuel.d()[0] * self.v_fuel_cilinder
        get_set_attr(self, "_m_fuel", value)
        return self._m_fuel

    @property
    def m_adm_rate(self):
        value = minutes_to_secconds(self.n) * self.m_fuel
        get_set_attr(self, "_m_adm_rate", value)
        return self._m_adm_rate

    @property
    def q_rate(self):
        n_dot_comb = self.m_adm_rate * m_comb
        value = n_dot_comb * (
            (W_rate / n_dot_comb)
            + (
                (
                    self.n_carbon_dioxide * carbon_dioxide.h_abs(25, self.cycle.stage3.T, True)
                    + self.n_water * water.h_abs(25, self.cycle.stage3.T, True)
                    + self.n_nitrogen * nitrogen.h_abs(25, self.cycle.stage3.T, True)
                )
                - (self.octane_ratio * octane.h_abs() + self.anhydrous_ratio * anhydrous.h_abs())
            )
            * 1e3
        )
        get_set_attr(self, "_q_rate", value)
        return self._q_rate

    @property
    def w_cycle_total(self):
        value = self.cycle.w * self.m_fuel
        get_set_attr(self, "_w_cycle_total", value)
        return self._w_cycle_total

    @property
    def ni(self):
        value = self.cycle.w * rpm_to_rps(n) * z / x
        get_set_attr(self, "_ni", value)
        return self._ni

    @property
    def thermic_efficiency(self):
        value = self.cycle.w / self.q_fuel_rate
        get_set_attr(self, "_thermic_efficiency", value)
        return self._thermic_efficiency

    def real_thermic_efficiency(self):
        value = self.cycle.ni / self.q_fuel_rate
        get_set_attr(self, "_real_thermic_efficiency", value)
        return self._real_thermic_efficiency

    @property
    def q_fuel_rate(self):
        value = self.m_adm_rate * fuel_pci
        get_set_attr(self, "_q_fuel_rate", value)
        return self._q_fuel_rate

    @property
    def global_efficiency(self):
        value = self.effective_efficiency / self.q_fuel_rate
        get_set_attr(self, "_global_efficiency", value)
        return self._global_efficiency

    @property
    def effective_efficiency(self):
        value = self.torque * 2 * np.pi * self.n
        get_set_attr(self, "_effective_efficiency", value)
        return self._effective_efficiency

    @property
    def torque(self):
        value = self.pme * self.V / (2 * np.pi * x)
        get_set_attr(self, "_torque", value)
        return self._torque
