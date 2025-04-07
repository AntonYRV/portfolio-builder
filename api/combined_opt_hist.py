from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime
from core.optimizer import optimizer_for_tickers, optimizer_for_assets
from core.history import get_portfolio_history


# Создаем Blueprint для объединенного эндпоинта
combined_bp = Blueprint('combined_opt_hist', __name__)

@combined_bp.route('/api/optimize_with_history', methods=['POST'])
@swag_from('../docs/combined.yml')
def optimize_with_history():
    data = request.get_json()
    return run_optimizer(data, include_history=True)

def run_optimizer(data, include_history=False):
    # Извлекаем данные из запроса
    mode = data.get("mode", "tickers")
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

    # Выбираем, какой метод оптимизации использовать
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

    # Добавляем историю портфеля, если это нужно
    if include_history:
        weights = result.get("weights", {})
        df_history, message = get_portfolio_history(weights, start_date, end_date)
        result["history"] = df_history.to_dict(orient="records")
        result["history_message"] = message

    return jsonify(result)