"""
Lagrange's Interpolation class File - from scypy
"""
from scipy.interpolate import lagrange
import numpy as np
import sympy as sp
from time import process_time as timer


class LagrangeScipy:

    def __init__(self):
        self.P = 0
        self.time_ellapsed = 0
        self.x = np.array([])
        self.y = np.array([])
        self._x = sp.symbols('x', real=True)

    def clear_data(self):
        self.P = 0

    def start(self, data=[]):

        if len(data) == 0:
            raise ValueError("Dados Inválidos!!!")

        self.clear_data()

        self.x = np.array(data[0].copy())
        self.y = np.array(data[1].copy())

        self.treat_data()

        sp.init_printing()
        x = self._x

        time0 = timer()

        poly = lagrange(self.x, self.y)
        print(f'scipy poli:\n{poly}')

        degree = len(poly.coef) - 1
        for c in poly.coef:
            self.P += c*x**degree
            degree -= 1

        self.time_ellapsed = timer() - time0
        return self.x, self.y, 'original data'

    def get_y(self):
        return self.y

    def get_poli(self):
        eq = sp.expand(self.P)
        print('Lagrange (Scipy):\t' + str(eq))
        for a in sp.preorder_traversal(eq):
            if isinstance(a, sp.Float):
                eq = eq.subs(a, round(a, 4))
        return sp.lambdify(self._x, eq), self.time_ellapsed, eq

    def treat_data(self):
        if self.x.size > 15:
            step = self.x.size // int(5+self.x.size/10)
            x = []
            y = []
            for i in range(self.x.size+step+1):
                if i % step == 0:
                    if i >= self.x.size-1:
                        x.append(self.x[-1])
                        y.append(self.y[-1])
                        break
                    x.append(self.x[i])
                    y.append(self.y[i])
                    i += step
            self.x = np.array(x)
            self.y = np.array(y)