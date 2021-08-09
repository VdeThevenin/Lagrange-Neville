from os import path
from Lagrange import Lagrange
from Neville import Neville
from LagrangeScipy import LagrangeScipy
import PySimpleGUI as sg
import numpy as np
from matplotlib import pyplot as pp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import process_time as timer


class GUI:
    def __init__(self):
        self._VARS = {'window': False,
                      'fig_agg': False,
                      'pltFig': False,
                      'values': []}
        self._PLOT_PARAM = {'title': False,
                            'x_label': False,
                            'y_label': False,
                            'grid': True,
                            'y_min': False,
                            'y_max': False}
        self.data = []
        self.c_mean = 0
        self.func = None
        self.styles = {'original data': 'k*'}
        self.methods = ['Lagrange', 'Neville', 'Comparação de Tempo', 'Lagrange (scipy)']

        sg.theme('Reds')
        x_fx_column = [[sg.Text('x: ', size=(5, 0)), sg.Input(key='x_input', enable_events=True)],
                       [sg.Text('f(x): ', size=(5, 0)), sg.Text('', size=(7, 0), key='y_output')]]
        layout = [
            [sg.Text('Arquivo csv:', size=(9, 0)),
             sg.Input(key='csv_input'),
             sg.FileBrowse(button_text='Procurar', key='file_browser')],
            [sg.Text('Método:', size=(9, 0)),
             sg.Combo(values=self.methods, size=(20, len(self.methods)),
                      default_value=self.methods[0],
                      key='method',
                      enable_events=True),
             sg.Text('Nº amostras: ', size=(15, 0), key='n_sample_text', visible=False),
             sg.Input(key='n_sample_in', size=(6, 0), visible=False)],
            [sg.Canvas(key='canvas', size=(300, 400))],
            [sg.Text('Tempo decorrido: ', size=(15, 0)), sg.Text('', size=(30, 0), key='time_text')],
            [sg.Column(x_fx_column, key='x_fx_col', visible=False)],
            [sg.Button('Executar'), sg.Quit('Sair')],
        ]

        self._VARS['window'] = sg.Window('Interpolação Polinomial de Lagrange', layout, finalize=True)

    def start(self):
        self.draw_chart()
        while True:
            event, self._VARS['values'] = self._VARS['window'].Read()

            if event in (None, 'Sair'):
                break
            if event == 'x_input':
                if self._VARS['values']['x_input'] and self._VARS['values']['x_input'][-1] not in ('-0123456789.'):
                    self._VARS['window']['x_input'].Update(self._VARS['window']['x_input'][:-1])
                else:
                    if self._VARS['values']['x_input'] == '':
                        x = 0.0
                    else:
                        x = float(self._VARS['values']['x_input'])
                    y = self.func(x)
                    self._VARS['window']['y_output'].Update('{y:.4f}'.format(y=y))
            elif event == 'method':
                if self._VARS['values']['method'] == self.methods[3]:
                    self._VARS['window']['n_sample_text'].Update(visible=True)
                    self._VARS['window']['n_sample_in'].Update(visible=True)
                else:
                    self._VARS['window']['n_sample_text'].Update(visible=False)
                    self._VARS['window']['n_sample_in'].Update(visible=False)
                if self._VARS['values']['method'] == self.methods[2]:
                    # self._VARS['window']['x_fx_col'].visible
                    self._VARS['window']['x_fx_col'].Update(visible=False)
                else:
                    if self.func is not None:
                        self._VARS['window']['x_fx_col'].Update(visible=True)
            else:
                if self._VARS['values']['method'] == self.methods[2]:
                    # self._VARS['window']['x_fx_col'].visible
                    self._VARS['window']['x_fx_col'].Update(visible=False)
                else:
                    self._VARS['window']['x_fx_col'].Update(visible=True)

                self.data, t_f, self.c_mean = self.play_method()
                t_plot0 = timer()
    
                self.update_chart()
    
                t_plot = timer() - t_plot0
                t_t = self.time_formatter(t_f) + ' + ' + self.time_formatter(t_plot) + ' (para o plot)'
    
                self._VARS['window']['time_text'].Update(t_t)
        self._VARS['window'].close()

    def draw_figure(self, canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    def draw_chart(self, **styles):
        self._VARS['pltFig'] = pp.figure()
        self._prepare_plot(**styles)
        self._VARS['fig_agg'] = self.draw_figure(self._VARS['window']['canvas'].TKCanvas, self._VARS['pltFig'])

    def update_chart(self, **styles):
        self._VARS['fig_agg'].get_tk_widget().forget()
        pp.clf()
        self._prepare_plot(**styles)
        self._VARS['fig_agg'] = self.draw_figure(self._VARS['window']['canvas'].TKCanvas, self._VARS['pltFig'])

    def _prepare_plot(self, **styles):
        if len(self.data) == 0:
            return
        if len(styles) > 0:
            for d in self.data:
                if d[2] == 'original data':
                    pp.plot(d[0], d[1], self.styles['original data'], label=d[2])
                    self._PLOT_PARAM['y_max'] = np.max(d[1])
                    self._PLOT_PARAM['y_min'] = np.min(d[1])
                elif styles.get(d[2]) is not None:
                    pp.plot(d[0], d[1], styles[d[2]], label=d[2])
                else:
                    pp.plot(d[0], d[1], label=d[2])
        else:
            for d in self.data:
                if d[2] == 'original data':
                    pp.plot(d[0], d[1], self.styles['original data'], label=d[2])
                    self._PLOT_PARAM['y_max'] = 1.1*np.max(d[1])
                    self._PLOT_PARAM['y_min'] = np.min(d[1]) - 0.01*np.max(d[1])
                else:
                    pp.plot(d[0], d[1], label=d[2])
        if self._VARS['window']['method'] == self.methods[2]:
            mean = np.ones(d[0].size)*self.c_mean
            pp.plot(d[0], mean, label='média')
        pp.grid(self._PLOT_PARAM['grid'])
        pp.title(self._PLOT_PARAM['title'])
        pp.xlabel(self._PLOT_PARAM['x_label'])
        pp.ylabel(self._PLOT_PARAM['y_label'])
        pp.ylim(ymax=self._PLOT_PARAM['y_max'], ymin=self._PLOT_PARAM['y_min'])
        self._PLOT_PARAM['y_label']
        pp.legend(loc='upper left', prop={'size': 6})

    def play_method(self):
        d = self.get_data()
        if self._VARS['values']['method'] == self.methods[0]:
            m = Lagrange()
            self._PLOT_PARAM['title'] = 'Interpolação de Lagrange'
        elif self._VARS['values']['method'] == self.methods[1]:
            m = Neville()
            self._PLOT_PARAM['title'] = 'Interpolação de Lagrange (por Neville)'
        elif self._VARS['values']['method'] == self.methods[3]:
            m = LagrangeScipy()
            self._PLOT_PARAM['title'] = 'Interpolação de Lagrange (SciPy)'
        else:
            t0 = timer()
            d = []
            result = self.compare_methods()
            d.append([result[0], result[1], 'dt'])
            self._PLOT_PARAM['y_max'] = 1.1*np.max(result[1])
            self._PLOT_PARAM['y_min'] = np.min(result[1]) - 0.01 * np.max(result[1])
            self._PLOT_PARAM['title'] = 'Tempo Lagrange vs Neville'
            self._PLOT_PARAM['x_label'] = 'N [amostras]'
            self._PLOT_PARAM['y_label'] = 'dt [% de t_lagrange]'
            return d, timer() - t0, result[2]
        m.start(d[0])
        result = m.get_poli()
        self._PLOT_PARAM['x_label'] = 'x'
        self._PLOT_PARAM['y_label'] = 'f(x)'
        self.func = np.vectorize(result[0])
        _x = np.linspace(np.min(d[0][0]), np.max(d[0][0]), len(d[0][0]) * 30)
        d.append([_x, self.func(_x), result[2]])
        return d, result[1], 0

    def compare_methods(self, nmax=10):
        dt = np.array([])
        neville = Neville()
        lagrange = Lagrange()
        for n in range(2, nmax + 1):
            _x = np.linspace(0, nmax, n)
            _y = self.__g(_x)
            data = [_x, _y]
            print(f'n: {n}')
            lagrange.start(data=data)
            t_l = lagrange.get_poli()[1]
            neville.start(data=data)
            t_n = neville.get_poli()[1]
            diff = ((t_l - t_n) / t_l) * 100
            dt = np.append(dt, diff)
            # print(f'tl_{n}: {t_l}')
            # print(f'tn_{n}: {t_n}')
            # print(f'diff: {diff}%')
        _x = np.arange(2, nmax + 1)
        return _x, dt, np.mean(dt)

    def get_data(self):
        p = self._VARS['values']['csv_input']
        if path.isfile(p):
            return self.__load_csv(p)
        else:
            if self._VARS['values']['method'] in (self.methods[2], self.methods[3]):
                return []
            raise ValueError("O CAMINHO É INVÁLIDO")

    def __g(self, x):
        #   g(x) = xˆ4 +2xˆ3  -13xˆ2 -14x + 24
        coefs = [1, 2, -13, -14, 24]
        return self.__generic_poli(x, coefs)

    def __generic_poli(self, x, coef_list):
        degree = len(coef_list) - 1
        poli = 0
        for i in range(len(coef_list)):
            poli += coef_list[i] * (x ** (degree - i))
        return poli

    def __load_csv(self, csv_path):
        data = np.genfromtxt(csv_path, delimiter=';')
        data = data.transpose()

        x = np.array(data[0])
        y = np.array(data[1])
        return [[x, y, 'original data']]

    def time_formatter(self, t):
        stime = ''
        t_m = t // 60
        t_h = t_m // 60
        t_s = t % 60
        if t_h > 0 or t_m > 0:
            if t_h > 0:
                stime = "{t}".format(t=int(t_h)) + ' hora'
                if t_h > 1:
                    stime += 's'
                stime += ', '
            if t_m > 0:
                stime = "{t}".format(t=int(t_m)) + ' minuto'
                if t_m > 1:
                    stime += 's'
                stime += ', '
            if t_s > 0:
                stime = "{t}".format(t=int(t_s)) + ' segundo'
                if t_s > 1:
                    stime += 's'
                stime += ', '
        else:
            if t_s >= 1:
                stime = "{t:.2f}".format(t=t_s) + ' segundo'
                if t_s >= 2:
                    stime += 's'
                stime += ', '
            elif not t_s - int(t_s) == 0:
                ok = False
                t_s1 = t_s
                idx = 0
                while not ok:
                    t_s1 = t_s1 * 10
                    idx += 1
                    if t_s1 >= 1:
                        ok = True
                if not idx % 3 == 0:
                    while not idx % 3 == 0:
                        idx += 1
                        t_s1 *= 10
                stime += "{t:.2f}".format(t=t_s1)
                if idx / 3 == 1:
                    stime += ' ms'
                elif idx / 3 == 2:
                    stime += ' µs'
                elif idx / 3 == 3:
                    stime += ' ns'
                elif idx / 3 == 4:
                    stime += ' ps'
                elif idx / 3 == 5:
                    stime += ' fs'
                elif idx / 3 == 6:
                    stime += ' as'
                elif idx / 3 == 7:
                    stime += ' zs'
                elif idx / 3 == 8:
                    stime += ' ys'
        return stime


tela = GUI()
tela.start()
