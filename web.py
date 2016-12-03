import datetime

from flask import Flask, render_template
from flask import redirect, url_for, request
from db import get_data

app = Flask(__name__)


@app.route('/')
def index():
    context = {}
    symbol = request.args.get('symbol')
    start = request.args.get('start')
    end = request.args.get('end')
    if symbol and start and end:
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()  # задаем временной промежуток
        end = datetime.datetime.strptime(end, '%Y-%m-%d').date()

        year = datetime.datetime.now().year
        if not start:
            start = datetime.date(year, 1, 1)
        if not end:
            end = datetime.date(year, 12, 31)
        data = get_data(symbol, start, end)
        context['data'] = data['data']
        context['symbol'] = symbol
        context['year'] = year
    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
