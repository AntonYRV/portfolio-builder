from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime
from core.optimizer import optimizer_for_tickers, optimizer_for_assets

optimize_bp = Blueprint('optimize', __name__)

@optimize_bp.route('/api/optimize', methods=['POST'])
@swag_from('../docs/optimize.yml')
def optimize():
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
