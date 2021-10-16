import json
import random
from simpy import *

# Общие настройки
SIM_TIME = 30 * 24  # Часы
# Склад
RAW_MATERIAL_WAREHOUSE = 100 * 1000  # Кг
CHARGE = 8000  # Кг
PYROLYSIS_CYCLE = 24  # Часы
# Поломка реактора
BREAKAGE_PROBABILITY = .2  # Вероятность поломки, часть от 1
BREAKAGE_REPAIR_TIME = 8  # Время починки, часы
# Умолчания для поставщиков
DEFAULT_DELIVERY_PERIODICITY = 7  # Периодичность отправки фур по умолчанию, дни
DEFAULT_DISCHARGE_TIME = 3  # Время разгрузки фур по умолчанию, часы

suppliers = dict()
# Подгрузка файлов с данными и глобальные переменные времени исполнения
# with open('suppliers.json', encoding='utf8') as f:
#     suppliers = json.load(f)
#     for supplier_name in suppliers:
#         supplier = suppliers[supplier_name]
#         if 'delivery_periodicity' not in supplier:
#             supplier['delivery_periodicity'] = DEFAULT_DELIVERY_PERIODICITY
#         if 'discharge_time' not in supplier:
#             supplier['discharge_time'] = DEFAULT_DISCHARGE_TIME
idle_hours = 0
count_break = 0


def tf(h: int) -> str:
    return f'{h//24} д {h%24} ч: '


def reactor_cycle(env: Environment, raw_material: Container):
    """
    Берёт CHARGE килограмм сырья и запускает цикл длительностью PYROLYSIS_CYCLE часов
    Реактор может сломаться. Вероятность поломки 20%, поломка может произойти во время (фактически перед) запуска цикла.
    """
    global idle_hours
    global count_break
    while True:
        if raw_material.level >= CHARGE:
            if random.random() > BREAKAGE_PROBABILITY:
                yield raw_material.get(CHARGE)
                print(f'{tf(env.now)}Началась загрузка реактора')
                yield env.timeout(PYROLYSIS_CYCLE)
                print(f'{tf(env.now)}Реактор закночил цикл переработки')
                print(f'На складе осталось: {raw_material.level / 1000} тонн')
            else:
                print(f'{tf(env.now)}Реактор сломался', 'red')
                count_break += 1
                yield env.timeout(BREAKAGE_REPAIR_TIME)
                print(f'{tf(env.now)}Реактор починен', 'red')
        else:
            print('ВНИМАНИЕ! ПРОСТОЙ В РАБОТЕ!', 'red')
            print(f'{tf(env.now)}Реактор ждёт появления материалов', 'red')
            print(f'На складе: {raw_material.level} тонн')
            idle_hours += 1
            yield env.timeout(1)


def raw_material_control(env: Environment, raw_material: Container, points_suppliers: dict, change_color_point):
    """Вызываем фуры по графику поставок"""
    while True:
        day = env.now // 24
        for supplier_name in suppliers:
            supplier = suppliers[supplier_name]
            delivery_periodicity = supplier['delivery_periodicity']
            discharge_time = supplier['discharge_time']

            if 0 == day % delivery_periodicity:
                change_color_point(points_suppliers[supplier_name], 'Green')
                print(f'{tf(env.now)}Вызываем фуру из "{supplier_name}"')
                yield env.process(truck(env, raw_material, supplier_name))
                yield env.timeout(discharge_time)
                change_color_point(points_suppliers[supplier_name], 'Red')
                print(f'{tf(env.now)}На складе {raw_material.level / 1000} тонн')
        yield env.timeout(24)  # Проверять каждые сутки


def truck(env: Environment, raw_material: Container, supplier_name: str):
    """Прибывает на склад с задержкой (время в пути) и пополняет склад."""
    yield env.timeout(suppliers[supplier_name]['delivery_time'])
    cargo = suppliers[supplier_name]['raw_materials_kg']
    print(f'{tf(env.now)}Фура из "{supplier_name}" привезла {cargo / 1000} тонн')
    yield raw_material.put(cargo)


def log_data(env: Environment, raw_material: Container, data):
    while True:
        data.append(raw_material.level / 1000)
        yield env.timeout(1)


def start(print_func, suppliers_data_raw, change_color_point, points_suppliers):
    # Переопределяем функцию вывода текста
    global print
    print = print_func
    
    data = []
    global suppliers
    for supplier in suppliers_data_raw:
        try:
            delivery_time = int(supplier[3])
        except:
            delivery_time = 2
        try:
            raw_materials_kg = int(supplier[4])
        except:
            raw_materials_kg = 100
        try:
            delivery_periodicity = int(supplier[5])
        except:
            delivery_periodicity = DEFAULT_DELIVERY_PERIODICITY
        try:
            discharge_time = int(supplier[6])
        except:
            discharge_time = DEFAULT_DISCHARGE_TIME
        suppliers[supplier[1]] = {"delivery_time": delivery_time, "raw_materials_kg": raw_materials_kg,
                                  "delivery_periodicity": delivery_periodicity, "discharge_time": discharge_time}
    env = Environment()
    reactor = Resource(env, 1)
    raw_material = Container(env, RAW_MATERIAL_WAREHOUSE, init=50000)
    env.process(log_data(env, raw_material, data))
    env.process(raw_material_control(env, raw_material, points_suppliers, change_color_point))
    env.process(reactor_cycle(env, raw_material))
    env.run(until=SIM_TIME)
    print(f'Часов простоя: {idle_hours}')
    print(f'Количество поломок: {count_break}')
    hours_to_days = [x / 24 for x in range(SIM_TIME)]
    return hours_to_days, data
