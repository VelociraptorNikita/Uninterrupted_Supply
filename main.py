from tkinter import Label
from PySimpleGUI.PySimpleGUI import Exit
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
    # time.sleep(0.1)

def change_color_point(point, color):
    map.TKCanvas.itemconfig(point, fill = color)
    window.refresh()

# Главное окно
# sg.theme('Dark2')
# sg.theme('DarkAmber')
sg.theme('DarkBlue3') # +
# sg.theme('Default1')
# sg.theme('Kayak')
# sg.theme('LightGreen1') # +
# sg.theme('LightGreen5')
# sg.theme('LightGrey3')
window = sg.Window('Бесперебойное снабжение', [
    [sg.Graph(
            canvas_size=(800, 400),
            graph_bottom_left=(0, 0),
            graph_top_right=(800, 400),
            key="-MAP-"
        ), sg.Canvas(key='-CANVAS-')],
    [sg.Multiline(size=(60, 15), key='LOG ELEMENT', do_not_clear=not DO_CLEAN_WINDOW)],
    [sg.Button('Запуск'),
     sg.Button('Настройки'),
    sg.CloseButton('Выход')]
],
resizable=True, finalize=True)
window.Maximize()
map = window.Element("-MAP-")
map.DrawImage(filename="map_800x400.png", location=(0, 400))
settings_active = False
while True:
    event, value = window.read()

    if event in (sg.WIN_CLOSED, 'Выход'):
        break

    if event == 'Запуск':
        if DO_CLEAN_WINDOW:
            sp.clear()
        tables_data = db.get_data('purveyor')
        points_suppliers = dict()
        for table_data in tables_data['data']:
            points_suppliers[table_data[1]] = map.DrawPoint((table_data[7], table_data[8]), 10, color='Red')

        sp.plot(*simulation.start(print_func, tables_data['data'], change_color_point, points_suppliers))  # построение графика
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
            key="-MAP_SETTING-",
            enable_events=True)],
                [sg.Table(values=tables_data['data'],
                      headings=tables_data['headers'],
                      display_row_numbers=False,
                      auto_size_columns=False,
                      num_rows=10,
                      key='-TABLE-', enable_events=True)],
            [sg.Text('Название:'), sg.Input(key='-NAME-'), sg.Text('Цена:'), sg.Input(key='-PRICE-'), sg.Text('Время доставки:'), sg.Input(key='-TIME-')],
            [sg.Text('Размер поставок:'), sg.Input(key='-MATERIAL-'), sg.Text('Периодичность:'), sg.Input(key='-PERIODICIITY-'), sg.Text('Время разгрузки:'), sg.Input(key='-DISCHARGE-')],
            [sg.Text('x:'), sg.Input(key='-X-', readonly=True), sg.Text('y:'), sg.Input(key='-Y-', readonly=True), sg.Text('id:'), sg.Input(key='-ID-', readonly=True)],
            [sg.Button('Сохранить'), sg.Button('Удалить'), sg.Button('Очистить'), sg.CloseButton('Выход')]
        ]
        window_settings = sg.Window('Настройки', layout_settings, resizable=True, finalize=True)
        window_settings.maximize()
        map_setting = window_settings.Element("-MAP_SETTING-")
        map_setting.DrawImage(filename="map_800x400.png", location=(0, 400))
    if settings_active:
        while True:
            event, values = window_settings.read(timeout=100)
            if event != sg.TIMEOUT_KEY:
                if event in (sg.WIN_CLOSED, 'Выход'):
                    settings_active = False
                    window_settings.close()
                    break
                if event == 'Очистить':
                    window_settings['-NAME-'].update('')
                    window_settings['-PRICE-'].update('')
                    window_settings['-TIME-'].update('')
                    window_settings['-MATERIAL-'].update('')
                    window_settings['-PERIODICIITY-'].update('')
                    window_settings['-DISCHARGE-'].update('')
                    window_settings['-X-'].update('')
                    window_settings['-Y-'].update('')
                    window_settings['-ID-'].update('')
                if event == '-TABLE-':
                    window_settings['-NAME-'].update(tables_data['data'][values['-TABLE-'][0]][1])
                    window_settings['-PRICE-'].update(tables_data['data'][values['-TABLE-'][0]][2])
                    window_settings['-TIME-'].update(tables_data['data'][values['-TABLE-'][0]][3])
                    window_settings['-MATERIAL-'].update(tables_data['data'][values['-TABLE-'][0]][4])
                    window_settings['-PERIODICIITY-'].update(tables_data['data'][values['-TABLE-'][0]][5])
                    window_settings['-DISCHARGE-'].update(tables_data['data'][values['-TABLE-'][0]][6])
                    window_settings['-X-'].update(tables_data['data'][values['-TABLE-'][0]][7])
                    window_settings['-Y-'].update(tables_data['data'][values['-TABLE-'][0]][8])
                    window_settings['-ID-'].update(tables_data['data'][values['-TABLE-'][0]][0])
                if event == '-MAP_SETTING-':
                    window_settings['-X-'].update(value=values[event][0])
                    window_settings['-Y-'].update(value=values[event][1])
                if event == 'Сохранить':
                    if values['-ID-'] == '':
                        id = tables_data['data'][-1][0] + 1 if len(tables_data['data']) > 0 else 1
                        if values['-X-'] != '' and values['-Y-'] != '' and values['-NAME-'] != '' and values['-PRICE-'] != '' and values['-TIME-'] != ''\
                                and values['-MATERIAL-'] != '' and values['-PERIODICIITY-'] != '' and values['-DISCHARGE-'] != '':
                            db.set_data('purveyor', [id, values['-NAME-'], values['-PRICE-'], values['-TIME-'],
                            values['-MATERIAL-'], values['-PERIODICIITY-'], values['-DISCHARGE-'], values['-X-'], values['-Y-']])
                            tables_data = db.get_data('purveyor')
                            window_settings['-TABLE-'].update(values=tables_data['data'])
                        else:
                            sg.popup_error('Внимание! Не заполнены все поля.')
                    else:
                        if sg.popup_ok_cancel(f'Вы точно хотите изменить запись с id {values["-ID-"]}?') == 'OK':
                            db.update_date('purveyor', values['-ID-'], [values['-NAME-'], values['-PRICE-'], values['-TIME-'],
                                values['-MATERIAL-'], values['-PERIODICIITY-'], values['-DISCHARGE-'], values['-X-'], values['-Y-']])
                            tables_data = db.get_data('purveyor')
                            window_settings['-TABLE-'].update(values=tables_data['data'])
                if event == 'Удалить' and values['-ID-'] != '':
                    if sg.popup_ok_cancel(f'Вы точно хотите удалить запись с id {values["-ID-"]}?') == 'OK':
                        db.delete('purveyor', values['-ID-'])
                        tables_data = db.get_data('purveyor')
                        window_settings['-TABLE-'].update(values=tables_data['data'])

window.close()
