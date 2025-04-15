from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime
from core.history import get_portfolio_history, calculate_max_drawdown_and_recovery
import logging

#logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['POST'])
@swag_from('../docs/history.yml')
def portfolio_history():
    data = request.get_json()
    mode = data.get("mode", "tickers")
    weights = data.get("weights_dict")
    start_date = data.get("start_date", "1995-01-01")
    end_date = data.get("end_date", datetime.today().strftime("%Y-%m-%d"))
    frequency = data.get("frequency", 252)

    if not weights:
        return jsonify({"error": "Отсутствуют веса портфеля"}), 400

    try:
        df_history, message = get_portfolio_history(
            weights, start_date=start_date, end_date=end_date,
            frequency=252, mode=mode
        )

        max_dd, dd_dates, recovery_days = calculate_max_drawdown_and_recovery(df_history)

        metrics = {
            "max_drawdown": max_dd,
            "max_drawdown_date": dd_dates[0],
            "recovery_date": dd_dates[1],
            "recovery_days": recovery_days
        }

    except Exception as e:
        return jsonify({"error": f"Ошибка при получении данных: {str(e)}"}), 500


    return jsonify({
        "history": df_history.to_dict(orient="records"),
        "history_message": message,
        "metrics": metrics
    })

