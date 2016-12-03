import csv
import logging
import sys
from urllib.parse import quote_plus
from urllib.request import urlopen
from datetime import datetime


def process(data):
    by_month_max = {month: -1 for month in range(1, 13)}
    global by_month_max
    try:
        for date, close in data.items():
            if by_month_max[date] < close:
                by_month_max[date] = close
    except:
        logging.error('Неправильный формат данных')


def write_file(filename):
    try:
        f = open(filename, 'w')
        print('{0:5} {1:10}'.format('Месяц', 'MAX значение'))
        f.write('Выведены максимальное значение для цены закрытия по месяцам.\nМесяц   MAX значение\n')
        for k, v in by_month_max.items():
            f.write('{0:5} {1:10}'.format(k, v)+'\n')
            print('{0:5} {1:10}'.format(k, v))
        f.close()
    except:
        logging.error("Ошибка при записи файла ", sys.exc_info()[0])


def load_data_file(file_name, start, end):
    try:
        f = open(file_name, 'r')
    except IOError:
        print('Не может открыть файл ', file_name)
        logging.error("Не может открыть файл", file_name)
        return
    data = {}
    f.readline()
    for row in csv.reader(f, delimiter=','):
        data[int(row[0].split('-')[1])] = float(row[4])
    return data
    process(data)


def load_data_network(symbol, start, end):
    url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv"
    url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y')))
    b_data = urlopen(url).readlines()
    data = {}
    for row in b_data[1:]:  # Пропускаем первую строку с именами колонок
        smth = row.decode().strip().split(',')
        time = datetime.strptime(smth[0], '%d-%b-%y')
        data[int(datetime.strftime(time, '%m'))] = float(smth[4])
    return data
    process(data)
