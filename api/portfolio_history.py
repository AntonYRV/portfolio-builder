from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime, timedelta
from core.history import get_portfolio_history


history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['POST'])
@swag_from('../docs/history.yml')
def portfolio_history():
    data = request.get_json()
    weights = data.get("weights")
    start_date = data.get("start_date", "2000-01-01")
    end_date = data.get("end_date", datetime.today().strftime("%Y-%m-%d"))

    if not weights:
        return jsonify({"error": "Отсутствуют веса портфеля"}), 400

    df_history, message = get_portfolio_history(weights, start_date, end_date)
    return jsonify({
        "history": df_history.to_dict(orient="records"),
        "history_message": message
    })