import sqlite3
from datetime import datetime
from urllib.parse import quote_plus
from urllib.request import urlopen


def read_db_net(symbol, start, end):
    url = "http://www.google.com/finance/historical?q={0}&startdate={1}&enddate={2}&output=csv"
    url = url.format(symbol.upper(), quote_plus(start.strftime('%b %d, %Y')), quote_plus(end.strftime('%b %d, %Y')))
    b_data = urlopen(url).readlines()
    dataset = {'data': {}, 'meta': {
            'columns': {'float': ['open', 'close', 'high', 'low'], 'int': ['volume']}
        }}
    for row in b_data[1:]:  # Пропускаем первую строку с именами колонок
        line = row.decode().strip().split(',')
        d = datetime.strptime(line[0], '%d-%m-%Y')
        date = datetime.date(d)
        # date = datetime.datetime.strptime(row[0], '%d-%m-%Y').date()
        dataset['data'][date] = {
            'date': date,
            'open': float(row[1]),
            'close': float(row[2]),
            'high': float(row[3]),
            'low': float(row[4]),
            'volume': int(row[5])
        }
    return dataset


def get_data(symbol, start, end):
    conn = sqlite3.connect('data/test.db')
    c = conn.cursor()
    # Создаем таблицы акций соответствующих компаний и таблицу компаний и лет, по кот. есть данные
    c.execute('''CREATE TABLE IF NOT EXISTS {symbol}
                 (date DATE UNIQUE, open REAL, close REAL, high REAL, low REAL, volume INTEGER)'''.format(symbol=symbol))
    c.execute('CREATE TABLE IF NOT EXISTS history (symbol TEXT, start DATE, end DATE)')

    # проверка, есть ли информация по symbol за интервал start и end
    check_history = list(c.execute('SELECT * FROM history WHERE symbol=? AND start>=? AND end<=?', (symbol, start, end)))
    if check_history:
       data = load_from_db(symbol, start, end)
    else:
        # записываем в историю
        c.execute('INSERT INTO history VALUES (?, ?, ?)', (symbol, start, end))
        # получаем информацию из сети
        data = read_db_net(symbol, start, end)
        print('Обновили базу данных.')
        for row in data:
            stocks = map(lambda x: (x['date'], x['open'], x['close'], x['high'], x['low'], x['volume']),
                         data['data'].values())
            c.executemany('REPLACE INTO {symbol} VALUES (?, ?, ?, ?, ?, ?)'.format(symbol=symbol), stocks)
            # c.execute('''INSERT INTO {symbol} VALUES (?, ?, ?, ?, ?, ?);''', row)
        # data = load_from_db(symbol, start, end)
    conn.commit()
    conn.close()
    return data


def load_from_db(symbol, start, end):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    data = c.execute('SELECT * FROM {symbol} WHERE date BETWEEN ? AND ?'.format(symbol=symbol), (start, end))
    dataset = {'data': {}, 'meta': {
        'columns': {'float': ['open', 'close', 'high', 'low'], 'int': ['volume']}
    }}
    for row in data:
        date = row[0]
        dataset['data'][date] = {
            'date': date,
            'open': float(row[1]),
            'close': float(row[2]),
            'high': float(row[3]),
            'low': float(row[4]),
            'volume': int(row[5]),
        }
    conn.commit()
    conn.close()
    return dataset


def write_data(data, width=15, title=''):
    # Форматированный вывод исходнных данных, если пользователь указал флаг
    columns_count = 1
    head = 'DATE'.center(width)

    row_format = '{date!s:^{width}}'
    columns = data['meta']['columns']
    for type in columns:
        columns_count += len(columns[type])
        for column in columns[type]:
            head += column.upper().center(width)
            if type == 'float':
                row_format += '{' + column + ':^{width}.3f}'
            else:
                row_format += '{' + column + ':^{width}}'
    print(title.center(columns_count * width))
    print(head.center(columns_count * width))
    # Сортируем ключи и выводим
    for date in sorted(data['data'].keys()):
        print(row_format.format(**data['data'][date], width=width))