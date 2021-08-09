"""
Lagrange's Interpolation class File
"""
import sympy as sp
import numpy as np
from time import process_time as timer


class Neville:

    def __init__(self):
        self.Q = []
        self.time_ellapsed = 0
        self.x = np.array([])
        self.y = np.array([])
        self._x = sp.symbols('x', real=True)

    def clear_data(self):
        self.Q = []

    def start(self, data=[]):

        if len(data) == 0:
            raise ValueError("Dados Inválidos!!")

        self.clear_data()

        self.x = np.array(data[0].copy())
        self.y = np.array(data[1].copy())

        self.treat_data()

        sp.init_printing()
        x = self._x

        qtd = self.x.size

        for idx in range(qtd):
            self.Q.append([0] * (qtd - idx))
        self.Q = np.array(self.Q, dtype="object")

        for idx in range(qtd):
            self.Q[0][idx] = self.y[idx]
        time0 = timer()

        for degree in range(1, qtd):
            for idx in range(len(self.Q[degree - 1]) - 1):
                # Q[d][i] = ((x - self.x[idx])*self.Q[degree-1][idx+1] - (x - self.x[idx+degree])*self.Q[degree-1][idx])
                #           --------------------------------------------------------------------------------------------
                #                                   self.x[idx+degree] - self.x[idx]
                self.Q[degree][idx] = (x - self.x[idx]) * self.Q[degree - 1][idx + 1]
                self.Q[degree][idx] -= (x - self.x[idx + degree]) * self.Q[degree - 1][idx]
                self.Q[degree][idx] /= self.x[idx + degree] - self.x[idx]
        self.time_ellapsed = timer() - time0

    def get_poli(self):
        eq = sp.expand(self.Q[-1][-1])
        print('Neville:\t' + str(eq))
        for a in sp.preorder_traversal(eq):
            if isinstance(a, sp.Float):
                eq = eq.subs(a, round(a, 4))
        return sp.lambdify(self._x, sp.expand(self.Q[-1][-1])), self.time_ellapsed, eq

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
