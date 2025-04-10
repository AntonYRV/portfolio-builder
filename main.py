from flask import Flask, render_template
from flasgger import Swagger
from api.optimize import optimize_bp
from api.portfolio_history import history_bp
from api.combined_opt_hist import combined_bp


app = Flask(__name__)
swagger = Swagger(app)

@app.route('/')
def index():
    return render_template('index_3.html')  # HTML-шаблон

# Регистрируем эндпоинты
app.register_blueprint(optimize_bp)
app.register_blueprint(history_bp)
app.register_blueprint(combined_bp)

if __name__ == '__main__':
    app.run(debug=True)
