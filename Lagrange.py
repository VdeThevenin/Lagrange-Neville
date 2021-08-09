"""
Lagrange's Interpolation class File
"""
import numpy as np
import sympy as sp
from time import process_time as timer


class Lagrange:

    def __init__(self):
        self.L = np.array([])
        self.P = 0
        self.time_ellapsed = 0
        self.x = np.array([])
        self.y = np.array([])
        self._x = sp.symbols('x', real=True)

    def clear_data(self):
        self.L = np.array([])
        self.P = 0

    def start(self, data=[]):

        if len(data) == 0:
            raise ValueError("Dados Inválidos!")

        self.clear_data()

        self.x = np.array(data[0].copy())
        self.y = np.array(data[1].copy())

        self.treat_data()

        sp.init_printing()
        x = self._x

        N = [1]*self.x.size
        D = [1]*self.x.size

        time0 = timer()

        for k in range(self.x.size):
            # Nk(x) = prod(x - xi)_i=0_n_i!=k <- poli
            for i in range(self.x.size):
                if i == k:
                    continue
                else:
                    d = x - self.x[i]
                    N[k] *= d

            # Dk(x) = prod(xk - xi)_i=0_n_i!=k <- scalar
            for i in range(self.x.size):
                if i == k:
                    continue
                else:
                    # its a scalar, doesnt need lambda function
                    # d = Lambda(x, self.x[k] - self.x[i])
                    d = self.x[k] - self.x[i]
                    D[k] *= d

            # Lk(x) = Nk(x)/Dk(x) <- poli
            self.L = np.append(self.L, N[k]/D[k])

            # P(x) = sum(yk*Lk(x))_k=0_n
            self.P += self.y[k]*self.L[k]
        self.time_ellapsed = timer() - time0

    def get_poli(self):
        eq = sp.expand(self.P)
        print('Lagrange:\t' + str(eq))
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
