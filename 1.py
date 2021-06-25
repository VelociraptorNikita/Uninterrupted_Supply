import simpy
import sys
import time
from termcolor import colored
import random
import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt

def print(string, color = 'white'):
  __builtins__.print(colored(string, color), '\n')
    #sys.stdout.flush()
    #time.sleep(0.03)
  #sys.stdout.write('\n')

'''
TODO:
Объём склада 30 тонн +
шинный - 3т в день.+ раз в 2 дня (48 часов)+
рти - 1т в день+ раз в неделю+
резинотехника 500 кг в день.+ раз в неделю (168 часов)+
атп посчтиать из количества авто. 200 тыс км на одних шина. раз в неделю - принял как патп
патп шины изнашиваются за ~70 дней. в год изнашиваются 5 раз. 150 машин * 5 раз * 4 шины = 3000. шина весит 24 кг. 72000 кг в год. в неделю 7200 / 52 = 140 кг+
шиномонтаж в неделю 200 кг. раз в неделю+
поставляют с опр вероятностью (пуассоновский процесс)
вероятность выхода из строя реактора 20%, на починку +- 8 часов+-
построить график заполнения склада
'''

RAW_MATERIAL_WAREHOUSE = 1000000 # Kg
max_raw = 0
CHARGE = 8000 # Kg
PYROLYSIS_CYCLE = 24 # Hours
SIM_TIME = 9000 # Hours
suppliers = {'Ярославский шинный завод' : {'Delivery time' : 2, 'raw_materials_kg' : 3000 * 2}, 
            'Ярославский завод РТИ': {'Delivery time' : 2, 'raw_materials_kg' : 61500},
            }
idle_hours = 0
count_break = 0
x = [i for i in range(SIM_TIME)]
y1 = []
y2 = [8000 for i in range(SIM_TIME)]

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
        print(f'На складе осталось: {raw_material.level} кг')
      else:
        print(f'Реактор сломался в {env.now}', 'red')
        count_break += 1
        yield env.timeout(8)
        print(f'Реактор починен в {env.now}', 'red')
    else:
      print('ВНИМАНИЕ! ПРОСТОЙ В РАБОТЕ!', 'red')
      print(f'Реактор ждёт появление материалов в {env.now}', 'red')
      print(f'На складе: {raw_material.level} кг')
      idle_hours += 1
      yield env.timeout(1)



def raw_material_control(env, raw_material):
  """Вызываем фуры по графику поставок. У шинного завода каждые 2 дня, у остальных каждую неделю"""
  while True:
    if env.now > 0 and env.now % 48 == 0: # график поставок, каждые 2 дня
      # Вызываем фуру
      print(f'Вызываем фуру из Ярославского шинного завода в {env.now}')
      yield env.process(truck(env, raw_material, 'Ярославский шинный завод'))
      yield env.timeout(2)
      print(f'Теперь на складе {raw_material.level} килограмм')
    elif env.now > 0 and env.now % 168 == 0: # график поставок, каждые 7 дней
      for supplier in suppliers:
        if supplier == 'Ярославский шинный завод': # у него свой график
          continue
        env.process(truck(env, raw_material, supplier))
      yield env.timeout(3)
      print(f'Теперь на складе {raw_material.level} килограмм')
    yield env.timeout(1) # Проверять каждый час


def truck(env, raw_material, supplier_name):
  """Прибывает на склад с задержкой (время в пути) и пополняет склад."""
  yield env.timeout(suppliers[supplier_name]['Delivery time'])
  print(f'Фура прибыла в {env.now}')
  ammount = suppliers[supplier_name]['raw_materials_kg']
  print(f'Фура привезла {ammount} килограмм')
  yield raw_material.put(ammount)
  

def fix_y(env, raw_material):
  global y1
  while True:
    y1.append(raw_material.level)
    yield env.timeout(1)


# Создать Environment и запустить процессы
env = simpy.Environment()
reactor = simpy.Resource(env, 1)
raw_material = simpy.Container(env, RAW_MATERIAL_WAREHOUSE, init=50000)
env.process(fix_y(env, raw_material))
env.process(raw_material_control(env, raw_material))
env.process(reactor_cycle(env, raw_material))

# Исполнить
env.run(until=SIM_TIME)
print(f'Часов простоя {idle_hours}')
print(f'Количество поломок {count_break}')
plt.title("Заполнение склада") # заголовок
plt.xlabel("время") # ось абсцисс
plt.ylabel("кг") # ось ординат
plt.grid()      # включение отображение сетки
plt.plot(x, y1, x, y2, 'r--')  # построение графика
plt.show()