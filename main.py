from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
from optimizer import optimize_portfolio
from datetime import datetime, timedelta

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def index():
    return render_template('index.html')  # HTML-шаблон

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """
    Оптимизация портфеля
    ---
    tags:
      - Портфель
    parameters:
      - name: tickers
        in: body
        type: object
        required: true
        schema:
          type: object
          properties:
            tickers:
              type: array
              items:
                type: string
              example: ["SBER", "GAZP"]
    responses:
      200:
        description: Оптимальные веса и показатели портфеля
        schema:
          type: object
          properties:
            weights:
              type: object
              additionalProperties:
                type: number
            expected_return:
              type: number
            volatility:
              type: number
            sharpe_ratio:
              type: number
    """
    data = request.get_json()
    tickers = data.get('tickers', [])
    start_date = datetime.today() - timedelta(days=5*365)
    end_date = datetime.today()
    result = optimize_portfolio(tickers, start_date, end_date, rf=0.02)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
