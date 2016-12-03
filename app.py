import argparse
import datetime
import logging

from process import write_file, process, load_data_file, load_data_network
from indicator import indicator_read_file, indicator_read_net
from db import get_data, write_data

if __name__ == "__main__":
    logging.info('Программа запущена')  # Вывод информационных соообщений
    # проверка аргументов
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-sb", "--symbol", help="работает с интернет-документом")
    group.add_argument("-f", "--file", help="работает с файлом")
    parser.add_argument("-s", "--save", help="сохранит результат в файл")
    parser.add_argument("-lf", "--logfile", help="определяет имя лог файла")
    parser.add_argument("-l", "--log", help="уровень логирования")
    parser.add_argument("-y", "--year", help="год, запрашиваемой информации")
    parser.add_argument("-max", "--max", help="выводит max цены закрытия по месяцам")
    parser.add_argument("-i", "--indicator", help="считает Стохасти́ческий осциллятор")
    parser.add_argument("-db", "--data_base", help="работа с базой данных")
    args = parser.parse_args()

    # настройка логирования

    # try:
    #     level = getattr(logging, args.log.upper(), None)
    #     logging.basicConfig(filename='app.log', level=level)
    # except:
    #     logging.error("Проблема с настройкой логирования")

    # инициализация дат
    if args.year:
        start, end = datetime.date(int(args.year), 1, 1), datetime.date(int(args.year), 12, 31)
    else:
        y = datetime.datetime.now().year
        start, end = datetime.date(y, 1, 1), datetime.date(y, 12, 31)

    #print('Данная программа выводит максимальное значение для цены закрытия по месяцам.')
    if args.file:
        if args.indicator:
            indicator_read_file(args.file)
        if args.max:
            process(load_data_file(args.file, start, end))  # функция выполняет обработку файла
    elif args.symbol:
        if args.indicator:
           indicator_read_net(args.symbol)
        if args.max:
            process(load_data_network(args.symbol, start, end))  # читать данные по сети
        if args.data_base:
            data = get_data(args.symbol, start, end)
            write_data(data)


    #запись в файл
    try:
        if args.save():
            write_file('out.txt')
    except:
        logging.info("Не удалось записать в файл")






