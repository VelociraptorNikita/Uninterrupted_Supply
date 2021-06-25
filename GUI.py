# https://realpython.com/pysimplegui-python/
# https://github.com/PySimpleGUI/PySimpleGUI/tree/master/DemoPrograms
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TkAgg')


fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


print = lambda *args, **kwargs: window['-MULTILINE KEY-'].print(*args, **kwargs)

layout = [[sg.Multiline('This is what a Multi-line Text Element looks like', size=(45,5), key='-MULTILINE KEY-')],
[sg.Canvas(key='-CANVAS-')],
            [sg.Button("OK")],
            [sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

# Create the window
window = sg.Window("Demo", layout)
#fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)


# Create an event loop
while True:
    event, value = window.read()
    # End program if user closes window or
    # presses the OK button
    if event in (sg.WIN_CLOSED, 'EXIT'):
        break
    if event == 'OK':
      for i in range(100):
        print('Hello there')
      # add the plot to the window
      

window.close()

