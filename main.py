from flask import Flask, render_template, request, jsonify
from optimizer import optimize_portfolio
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # HTML-шаблон

@app.route('/api/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    tickers = data.get('tickers', [])
    start_date = datetime.today() - timedelta(days=5*365)
    end_date = datetime.today()
    result = optimize_portfolio(tickers, start_date, end_date, rf=0.02)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
