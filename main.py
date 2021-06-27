from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import PySimpleGUI as sg
import db
import simulation

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


# Главное окно
sg.theme('Default1')
window = sg.Window('Бесперебойное снабжение', [
    [sg.Multiline(size=(60, 15), key='LOG ELEMENT', do_not_clear=not DO_CLEAN_WINDOW),
     sg.Canvas(key='-CANVAS-')],
    [sg.Button('Поехали'),
     sg.Button('Настройки'),
     sg.Button('Выход')]
])

settings_active = False
while True:
    event, value = window.read()

    if event in (sg.WIN_CLOSED, 'Выход'):
        break

    if event == 'Поехали':
        if DO_CLEAN_WINDOW:
            sp.clear()
        sp.plot(*simulation.start(print_func))  # построение графика
        sp.axhline(simulation.CHARGE // 1000, color='r', linestyle='--')
        draw_figure(window['-CANVAS-'].TKCanvas)

    if event == 'Настройки' and not settings_active:
        settings_active = True

        # массив словарей с полями data и headers
        tables_data = [db.get_data(table) for table in ('purveyor', 'purveyance')]

        layout_settings = [
            [sg.Table(values=table_data['data'],
                      headings=table_data['headers'],
                      display_row_numbers=True,
                      auto_size_columns=False,
                      num_rows=5) for table_data in tables_data],
            [sg.Input(key='-IN-')],
            [sg.Button('Сохранить'), sg.Button('Выход')]
        ]
        window_settings = sg.Window('Настройки', layout_settings)
    if settings_active:
        event, values = window_settings.read(timeout=100)
        if event != sg.TIMEOUT_KEY:
            if event in (sg.WIN_CLOSED, 'Выход'):
                settings_active = False
                window_settings.close()
            if event == 'Сохранить':
                sg.popup('You entered ', values['-IN-'])
        # Исполнить

window.close()
