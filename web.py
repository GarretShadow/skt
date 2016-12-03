import datetime

from flask import Flask, render_template
from flask import redirect, url_for, request
from data_base import get_data

app = Flask(__name__)


@app.route('/')
def start_page():
    return render_template('start_page.html')


@app.route('/counting')
def counting():
    symbol = request.args.get('symbol', '')
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    return redirect(url_for("stocks", symbol=symbol, start=start, end=end))
#@app.route('/stocks/<symbol>/<int:year>')


@app.route('/stocks/<string:symbol>/<string:start>/<string:end>')
def stocks(symbol, start, end):

    # symbol = request.args.get('symbol', '')
    # start_d = request.args.get('start', '')
    # end_d = request.args.get('end', '')

    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()  # задаем временной промежуток
    end = datetime.datetime.strptime(end, '%Y-%m-%d').date()

    #start = None
    #end = None
    year = datetime.datetime.now().year
    if not start:
        start = datetime.date(year, 1, 1)
    if not end:
        end = datetime.date(year, 12, 31)
    # start, end = datetime.date(2015, 12, 1), datetime.date(2015, 12, 31)
    data = get_data(symbol, start, end)
    return render_template('stocks.html', data=data['data'], symbol=symbol, year=year)


if __name__ == '__main__':
    app.run(debug=True)
