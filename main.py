from tkinter import Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import PySimpleGUI as sg
import db
import simulation
import time

# Настройки
DO_CLEAN_WINDOW = False

matplotlib.use('TkAgg')
fig = matplotlib.figure.Figure(figsize=(6, 5), dpi=100)
sp = fig.add_subplot(111)
sp.set_title('Заполнение склада')  # заголовок
sp.set_xlabel('Время, д')  # ось абсцисс (вправо)
sp.set_ylabel('Заполнение, т')  # ось ординат (вверх)
sp.grid()
figure_canvas_agg = None


def draw_figure(canvas):
    global figure_canvas_agg
    if not figure_canvas_agg:
        figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    figure_canvas_agg.draw()


def print_func(string, color='black'):
    window['LOG ELEMENT'].print(string, text_color=color)
    window.refresh()
    time.sleep(0.1)


# Главное окно
sg.theme('Default1')
window = sg.Window('Бесперебойное снабжение', [
    [sg.Graph(
            canvas_size=(800, 400),
            graph_bottom_left=(0, 0),
            graph_top_right=(800, 400),
            key="map"
        ), sg.Canvas(key='-CANVAS-')],
    [sg.Multiline(size=(60, 15), key='LOG ELEMENT', do_not_clear=not DO_CLEAN_WINDOW)],
    [sg.Button('Запуск'),
     sg.Button('Настройки'),
     sg.Button('Выход')]
]).Finalize()

window.Maximize()
map = window.Element("map")
map.DrawImage(filename="map_800x400.png", location=(0, 400))
point = map.DrawPoint((75,75), 10, color='Red')

settings_active = False
while True:
    event, value = window.read()

    if event in (sg.WIN_CLOSED, 'Выход'):
        break

    if event == 'Запуск':
        if DO_CLEAN_WINDOW:
            sp.clear()
        map.TKCanvas.itemconfig(point, fill = "Green")  
        sp.plot(*simulation.start(print_func))  # построение графика
        sp.axhline(simulation.CHARGE // 1000, color='r', linestyle='--')
        draw_figure(window['-CANVAS-'].TKCanvas)

    if event == 'Настройки' and not settings_active:
        settings_active = True

        # массив словарей с полями data и headers   
        tables_data = db.get_data('purveyor')

        layout_settings = [
            [sg.Graph(
            canvas_size=(800, 400),
            graph_bottom_left=(0, 0),
            graph_top_right=(800, 400),
            key="map_setting",
            enable_events=True)],
                [sg.Table(values=tables_data['data'],
                      headings=tables_data['headers'],
                      display_row_numbers=False,
                      auto_size_columns=False,
                      num_rows=20,
                      key='-TABLE-')],
            [sg.Text('Название:'), sg.Input(key='-NAME-'), sg.Text('Цена:'), sg.Input(key='-PRICE-'), sg.Text('Время доставки:'), sg.Input(key='-TIME-')],
            [sg.Text('x:'), sg.Input(key='-X-', readonly=True), sg.Text('y:'), sg.Input(key='-Y-', readonly=True)],
            [sg.Button('Сохранить'), sg.Button('Очистить'), sg.Button('Выход')]
        ]
        window_settings = sg.Window('Настройки', layout_settings).Finalize()
        window_settings.maximize()
        map_setting = window_settings.Element("map_setting")
        map_setting.DrawImage(filename="map_800x400.png", location=(0, 400))
    if settings_active:
        while True:
            event, values = window_settings.read(timeout=100)
            if event != sg.TIMEOUT_KEY:
                if event in (sg.WIN_CLOSED, 'Выход'):
                    settings_active = False
                    window_settings.close()
                    break
                if event == 'map_setting':
                    window_settings['-X-'].update(value=values[event][0])
                    window_settings['-Y-'].update(value=values[event][1])
                if event == 'Сохранить':
                    id = tables_data['data'][-1][0] + 1 if len(tables_data['data']) > 0 else 1
                    if values['-X-'] != '' and values['-Y-'] != '':
                        db.set_data('purveyor', [id, values['-NAME-'], values['-PRICE-'], values['-TIME-'], values['-X-'], values['-Y-']])
                        tables_data = db.get_data('purveyor')
                        window_settings['-TABLE-'].update(values=tables_data['data'])
                if event == 'Очистить':
                    db.clear('purveyor')
            # Исполнить

window.close()
