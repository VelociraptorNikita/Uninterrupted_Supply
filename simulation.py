import json
import random
import simpy

# Настройки и подгрузка файлов с данными
RAW_MATERIAL_WAREHOUSE = 100 * 1000  # Кг
CHARGE = 8000  # Кг
PYROLYSIS_CYCLE = 24  # Часы
SIM_TIME = 30 * 24  # Часы
with open('suppliers.json', encoding='utf8') as f:
    suppliers = json.load(f)
idle_hours = 0
count_break = 0


def reactor_cycle(env, raw_material):
    """
    Берёт CHARGE килограмм сырья и запускает цикл длительностью PYROLYSIS_CYCLE часов
    Реактор может сломаться. Вероятность поломки 20%, поломка может произойти во время (фактически перед) запуска цикла.
    """
    global idle_hours
    global count_break
    while True:
        if raw_material.level >= CHARGE:
            if random.randint(1, 100) > 20:
                yield raw_material.get(CHARGE)
                print(f'Началась загрузка реактора в {env.now}')
                yield env.timeout(PYROLYSIS_CYCLE)
                print(f'Реактор закночил цикл переработки в {env.now}.')
                print(f'На складе осталось: {raw_material.level} тонн')
            else:
                print(f'Реактор сломался в {env.now}', 'red')
                count_break += 1
                yield env.timeout(8)
                print(f'Реактор починен в {env.now}', 'red')
        else:
            print('ВНИМАНИЕ! ПРОСТОЙ В РАБОТЕ!', 'red')
            print(f'Реактор ждёт появление материалов в {env.now}', 'red')
            print(f'На складе: {raw_material.level} тонн')
            idle_hours += 1
            yield env.timeout(1)


def raw_material_control(env, raw_material):
    """Вызываем фуры по графику поставок. У шинного завода каждые 2 дня, у остальных каждую неделю"""
    while True:
        if env.now > 0 and env.now % (2 * 24) == 0:  # график поставок, каждые 2 дня
            # Вызываем фуру
            print(f'Вызываем фуру из Ярославского шинного завода в {env.now}')
            yield env.process(truck(env, raw_material, 'Ярославский шинный завод'))
            yield env.timeout(2)
            print(f'Теперь на складе {raw_material.level} килограмм')
        elif env.now > 0 and env.now % (7 * 24) == 0:  # график поставок, каждые 7 дней
            for supplier in suppliers:
                if supplier == 'Ярославский шинный завод':  # у него свой график
                    continue
                env.process(truck(env, raw_material, supplier))
            yield env.timeout(3)
            print(f'Теперь на складе {raw_material.level} килограмм')
        yield env.timeout(1)  # Проверять каждый час


def truck(env, raw_material, supplier_name):
    """Прибывает на склад с задержкой (время в пути) и пополняет склад."""
    yield env.timeout(suppliers[supplier_name]['delivery_time'])
    print(f'Фура прибыла в {env.now}')
    ammount = suppliers[supplier_name]['raw_materials_kg']
    print(f'Фура привезла {ammount} килограмм')
    yield raw_material.put(ammount)


def log_data(env, raw_material, data):
    while True:
        data.append(raw_material.level // 1000)
        yield env.timeout(1)


def start(print_func):
    # Переопределяем функцию вывода текста
    global print
    print = print_func

    data = []

    env = simpy.Environment()
    reactor = simpy.Resource(env, 1)
    raw_material = simpy.Container(env, RAW_MATERIAL_WAREHOUSE, init=50000)
    env.process(log_data(env, raw_material, data))
    env.process(raw_material_control(env, raw_material))
    env.process(reactor_cycle(env, raw_material))
    env.run(until=SIM_TIME)
    print(f'Часов простоя {idle_hours}')
    print(f'Количество поломок {count_break}')
    return data
