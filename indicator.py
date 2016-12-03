import csv
import logging
import numpy as np
import matplotlib.pyplot as plt
from urllib.request import urlopen

# Стохасти́ческий осциллятор (стоха́стик, стоха́стика от англ. stochastic oscillator) —
# индикатор технического анализа, который показывает положение текущей цены относительно диапазона цен
# за определенный период в прошлом. Измеряется в процентах.
#
# K - быстрый стохастик (сплошная линия, основной график)
# K(t) = (C(t) - Ln) / (Hn - Ln) * 100
# C - цена закрытия текущего периода
# Ln - самая низкая цена за последние n периодов
# Hn - самая высокая цена за последние n периодов
#
# D - медленный стохастик (пунктирная линия, дополнительно усреднённый график)
# D является скользящей средней относительно K с небольшим периодом усреднения.


def stochastic_oscillator (data: list, window: int):
    K, upper_line, bottom_line = [], [], []
    d = data[1][0] - data[1][1]
    N = range(len(data[0]))
    for t in N:
        K.append((data[0][t] - data[1][1]) / d * 100)
    D = moving_average(K, window, 'exp')
    #del(K[0:window])
    N = range(len(K))
    for t in N:
        upper_line.append(80.0)
        bottom_line.append(20.0)
    trading_signals(K, D, data[2])
    plt.plot(N, K, 'r', N, D, 'b--', N, upper_line, 'k--', N, bottom_line, 'k--')
    plt.legend(['K(t)', 'D(t)', '80%', '20%'],
               loc='upper right')
    plt.show()


def moving_average(data: list, window: int, type='simple'):
    # compute an n period moving average.
    # type is 'simple' | 'exponential'
    data = np.asarray(data)
    if type == 'simple':
        weights = np.ones(window)
    else:
        weights = np.exp(np.linspace(-1., 0., window))

    weights /= weights.sum()

    res = np.convolve(data, weights, mode='full')[:len(data)]
    res[:window] = res[window]
    return res

def trading_signals (K: list, D: list, time: list):
    #покупать - K, D СТАЛИ выше 20%, K выше D
    #продавать - K, D СТАЛА ниже 80%, K ниже D
    N = range(1, len(K))
    table = {}
    for t in N:
        if (K[t] > D[t]) or (K[t] > 20.0 and K[t-1] < 20.0) or (D[t] > 20.0 and D[t-1] < 20.0):
            table[time[t]] = 'BUY'
        elif (K[t] < D[t]) or (K[t] < 80.0 and K[t-1] > 80.0) or (D[t] < 80.0 and D[t-1] > 80.0):
            table[time[t]] = 'SELL'
    indicator_write(table)

def indicator_read_file(file_name: str):
    try:
        f = open(file_name, 'r')
    except IOError:
        print('Не может открыть файл ', file_name)
        logging.error("Не может открыть файл", file_name)
        return
    #data = [[C(t)], [Hn, Ln]]
    data = [[], [0.0, 9999999.9], []]
    f.readline()
    for row in csv.reader(f, delimiter=','):
        data[0].append(float(row[4]))
        data[2].append(row[0])
        if data[1][0] < float(row[2]):
            data[1][0] = float(row[2])
        if data[1][1] > float(row[3]):
            data[1][1] = float(row[3])
    stochastic_oscillator(data, 6)

def indicator_read_net(file_name: str):
    try:
        url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv"
        url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y')))
        b_data = urlopen(url).readlines()
        data = [[], [0.0, 9999999.9], []]
        for row in b_data[1:]:  # Пропускаем первую строку с именами колонок
            smth = row.decode().strip().split(',')
            data[0].append(float(smth[4]))
            data[2].append(smth[0])
            if data[1][0] < float(smth[2]):
                data[1][0] = float(smth[2])
            if data[1][1] > float(smth[3]):
                data[1][1] = float(smth[3])
        stochastic_oscillator(data, 6)
    except IOError:
        print('Не может подключиться к сети ', file_name)
        logging.error("Не может подключиться к сети", file_name)
        return

def indicator_write(data):
    f = open("indicator.txt", 'w')
    f.write('{0:10} {1:10}'.format('Дата', 'Торговый сигнал') + '\n')
    for k, v in sorted(data.items()):
        f.write('{0:10} {1:10}'.format(k, v) + '\n')
    f.close()


