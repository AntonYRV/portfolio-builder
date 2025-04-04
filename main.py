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
      - name: mode
        in: body
        type: string
        required: true
        description: "Выбор метода оптимизации ('tickers' или 'assets')"
        example: "tickers"
      - name: tickers
        in: body
        type: array
        items:
          type: string
        required: true
        description: "Список тикеров"
        example: ["SBER", "GAZP"]
      - name: rf
        in: body
        type: number
        required: false
        description: "Безрисковая ставка"
        example: 0.02
      - name: start_date
        in: body
        type: string
        format: date
        required: false
        description: "Дата начала (YYYY-MM-DD)"
        example: "2020-01-01"
      - name: end_date
        in: body
        type: string
        format: date
        required: false
        description: "Дата окончания (YYYY-MM-DD)"
        example: "2024-04-04"
      - name: objective
        in: body
        type: string
        required: false
        description: "Оптимизационная цель ('max_sharpe', 'min_volatility' и т.д.)"
        example: "max_sharpe"
      - name: risk_aversion
        in: body
        type: number
        required: false
        description: "Коэффициент неприятия риска"
        example: 1.0
      - name: target_volatility
        in: body
        type: number
        required: false
        description: "Целевая волатильность (если указано)"
      - name: target_return
        in: body
        type: number
        required: false
        description: "Целевая доходность (если указано)"
      - name: short_positions
        in: body
        type: boolean
        required: false
        description: "Разрешены ли короткие позиции"
        example: false
      - name: l2_reg
        in: body
        type: boolean
        required: false
        description: "Использовать ли L2-регуляризацию"
        example: false
      - name: gamma
        in: body
        type: number
        required: false
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
