from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
from optimizer import optimizer_for_tickers, optimizer_for_assets
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
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - mode
            - tickers
          properties:
            mode:
              type: string
              description: "Выбор метода оптимизации ('tickers' или 'assets')"
              example: "tickers"
            tickers:
              type: array
              items:
                type: string
              description: "Список тикеров"
              example: ["SBER", "GAZP"]
            rf:
              type: number
              description: "Безрисковая ставка"
              example: 0.02
            start_date:
              type: string
              format: date
              description: "Дата начала (YYYY-MM-DD)"
              example: "2020-01-01"
            end_date:
              type: string
              format: date
              description: "Дата окончания (YYYY-MM-DD)"
              example: "2024-04-04"
            objective:
              type: string
              description: "Оптимизационная цель ('max_sharpe', 'min_volatility' и т.д.)"
              example: "max_sharpe"
            risk_aversion:
              type: number
              description: "Коэффициент неприятия риска"
              example: 1.0
            target_volatility:
              type: number
              description: "Целевая волатильность (если указано)"
            target_return:
              type: number
              description: "Целевая доходность (если указано)"
            short_positions:
              type: boolean
              description: "Разрешены ли короткие позиции"
              example: false
            l2_reg:
              type: boolean
              description: "Использовать ли L2-регуляризацию"
              example: false
            gamma:
              type: number
              description: "Параметр гамма для L2-регуляризации"
              example: 1.0
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
    
    mode = data.get("mode", "tickers")  # По умолчанию "tickers"
    tickers = data.get("tickers", [])
    rf = data.get("rf", 0.02)
    start_date = data.get("start_date", "2000-01-01")
    end_date = data.get("end_date", datetime.today().strftime("%Y-%m-%d"))
    objective = data.get("objective", "max_sharpe")
    risk_aversion = data.get("risk_aversion", 1.0)
    target_volatility = data.get("target_volatility")
    target_return = data.get("target_return")
    short_positions = data.get("short_positions", False)
    l2_reg = data.get("l2_reg", False)
    gamma = data.get("gamma", 1.0)

    if mode == "tickers":
        result = optimizer_for_tickers(
            tickers, rf, start_date, end_date, objective,
            risk_aversion, target_volatility, target_return,
            short_positions, l2_reg, gamma
        )
    elif mode == "assets":
        result = optimizer_for_assets(
            tickers, rf, start_date, end_date, objective,
            risk_aversion, target_volatility, target_return,
            short_positions, l2_reg, gamma
        )
    else:
        return jsonify({"error": "Invalid mode"}), 400

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
