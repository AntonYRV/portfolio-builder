from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import datetime
from core.optimizer import optimizer_for_tickers
from core.history import get_portfolio_history, calculate_max_drawdown_and_recovery

compare_bp = Blueprint('compare_portfolios', __name__)

@compare_bp.route('/api/compare_portfolios', methods=['POST'])
@swag_from('../docs/compare_portfolios.yml')
def compare_portfolios():
    try:
        data = request.get_json()
        tickers = data.get("tickers", [])
        mode = data.get("mode", "tickers")
        user_weights = data.get("weights")  # Может быть None
        benchmark = data.get("benchmark")  # Может быть None

        # Обязательные параметры
        if not tickers:
            return jsonify({"error": "Список активов (tickers) обязателен"}), 400

        # Общие параметры
        rf = data.get("rf", 0.0)
        start_date = data.get("start_date", "1995-01-01")
        end_date = data.get("end_date", datetime.today().strftime("%Y-%m-%d"))
        objective = data.get("objective", "max_sharpe")
        risk_aversion = data.get("risk_aversion", 1.0)
        target_volatility = data.get("target_volatility")
        target_return = data.get("target_return")
        short_positions = data.get("short_positions", False)
        l2_reg = data.get("l2_reg", False)
        gamma = data.get("gamma", 1.0)
        frequency = data.get("frequency", 252)

        result = {}

        # 1. Пользовательский портфель (если есть веса)
        if user_weights:
            df_user_hist, msg = get_portfolio_history(user_weights, start_date, end_date, mode="tickers", frequency=frequency)
            ret, vol = df_user_hist['portfolio_value'].pct_change().mean() * frequency, df_user_hist['portfolio_value'].pct_change().std() * (frequency ** 0.5)
            sharpe = (ret - rf) / vol if vol > 0 else None
            dd, dd_dates, recovery_days = calculate_max_drawdown_and_recovery(df_user_hist)

            result["user"] = {
                "weights_dict": user_weights,
                "history": df_user_hist.to_dict(orient="records"),
                "metrics": {
                    "return": ret,
                    "volatility": vol,
                    "sharpe_ratio": sharpe,
                    "max_drawdown": dd,
                    "max_drawdown_date": dd_dates[0],
                    "recovery_date": dd_dates[1],
                    "recovery_days": recovery_days
                }
            }

        # 2. Оптимизированный портфель (всегда)
        opt_result = optimizer_for_tickers(
            tickers, rf, start_date, end_date, objective,
            risk_aversion, target_volatility, target_return,
            short_positions, l2_reg, gamma, frequency
        )

        opt_weights = opt_result["weights_dict"]
        df_opt_hist, msg = get_portfolio_history(opt_weights, start_date, end_date, mode="tickers", frequency=frequency)
        dd, dd_dates, recovery_days = calculate_max_drawdown_and_recovery(df_opt_hist)

        result["optimized"] = {
            "weights_dict": opt_weights,
            "history": df_opt_hist.to_dict(orient="records"),
            "metrics": {
                "return": opt_result["performance"]["return"],
                "volatility": opt_result["performance"]["volatility"],
                "sharpe_ratio": opt_result["performance"]["sharpe_ratio"],
                "max_drawdown": dd,
                "max_drawdown_date": dd_dates[0],
                "recovery_date": dd_dates[1],
                "recovery_days": recovery_days
            }
        }

        # 3. Бенчмарк (опционально)
        if benchmark:
            df_bench_hist, msg = get_portfolio_history({benchmark: 1.0}, start_date, end_date, mode="assets")
            ret, vol = df_bench_hist['portfolio_value'].pct_change().mean() * frequency, df_bench_hist['portfolio_value'].pct_change().std() * (frequency ** 0.5)
            sharpe = (ret - rf) / vol if vol > 0 else None
            dd, dd_dates, recovery_days = calculate_max_drawdown_and_recovery(df_bench_hist)

            result["benchmark"] = {
                "weights_dict": {benchmark: 1.0},
                "history": df_bench_hist.to_dict(orient="records"),
                "metrics": {
                    "return": ret,
                    "volatility": vol,
                    "sharpe_ratio": sharpe,
                    "max_drawdown": dd,
                    "max_drawdown_date": dd_dates[0],
                    "recovery_date": dd_dates[1],
                    "recovery_days": recovery_days
                }
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
