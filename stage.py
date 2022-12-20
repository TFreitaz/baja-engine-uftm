class Stage(object):
    _v = None
    _T = None
    _p = None
    verbose = False

    def __init__(self, name, T=None, p=None, v=None, verbose=False):
        self._T = T
        self._p = p
        self._v = v
        self.name = name
        self.verbose = verbose

    def set_property_function(self, prop, f):
        if prop == "v":
            self.v_func = f
        elif prop == "T":
            self.T_func = f
        elif prop == "p":
            self.p_func = f
        else:
            raise Exception(f"Property {prop} does not exist.")

    @property
    def v(self):
        if self._v is None:
            self._v = self.v_func(self)
        if self.verbose:
            print(f"Stage[{self.name}].v={self._v}")
        return self._v

    @property
    def T(self):
        if self._T is None:
            self._T = self.T_func(self)
        if self.verbose:
            print(f"Stage[{self.name}].T={self._T}")
        return self._T

    @property
    def p(self):
        if self._p is None:
            self._p = self.p_func(self)
        if self.verbose:
            print(f"Stage[{self.name}].p={self._p}")
        return self._p