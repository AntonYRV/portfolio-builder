from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime
from core.history import get_portfolio_history
import logging

#logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history', methods=['POST'])
@swag_from('../docs/history.yml')
def portfolio_history():
    data = request.get_json()
    mode = data.get("mode", "tickers")  # По умолчанию "tickers"
    weights = data.get("weights_dict")
    start_date = data.get("start_date", "2000-01-01")
    end_date = data.get("end_date", datetime.today().strftime("%Y-%m-%d"))

    # Проверка на mode и weights
    if mode == 'assets' and weights is None:
        # Для 'assets' возможно отсутствие весов, в этом случае возвращаем сообщение
        #logger.debug("В режиме 'assets' веса не требуются.")
        return jsonify({"error": "Для режима 'assets' веса не требуются."}), 400

    if not weights:
        #logger.error("Отсутствуют веса портфеля.")
        return jsonify({"error": "Отсутствуют веса портфеля"}), 400

    # Попытка получить историю портфеля
    try:
        df_history, message = get_portfolio_history(weights, start_date=start_date, end_date=end_date, mode=mode)
    except Exception as e:
        #logger.error(f"Ошибка при получении данных по истории портфеля: {str(e)}")
        return jsonify({"error": f"Ошибка при получении данных: {str(e)}"}), 500

    # Возвращаем результат
    return jsonify({
        "history": df_history.to_dict(orient="records"),
        "history_message": message
    })
