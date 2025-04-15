from flasgger import swag_from
from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.table_models import AssetClass
import datetime
import os

asset_list_bp = Blueprint('asset_list', __name__)

# Настройка соединения с базой данных
# Absolute path to the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Full path to the SQLite database file
DATABASE_PATH = os.path.join(BASE_DIR, "moex_data.db")
# SQLite database URL for SQLAlchemy connection
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@asset_list_bp.route('/api/asset_list', methods=['GET'])
@swag_from('../docs/asset_list.yml')
def get_assets():
    """
    Эндпоинт для получения списка всех доступных активов из базы данных.
    Возвращает поля ticker и asset_ru из таблицы asset_classes с кэшированием.
    """
    try:
        result = get_cached_assets()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Переменная для хранения кэша и времени обновления
assets_cache = {
    "data": None,
    "last_update": None
}

def get_cached_assets():
    """Получает список активов с кэшированием на 24 часа"""
    current_time = datetime.datetime.now()
    
    # Если кэш пустой или устарел (прошло больше 24 часов), обновляем его
    if (assets_cache["data"] is None or 
        assets_cache["last_update"] is None or 
        (current_time - assets_cache["last_update"]).total_seconds() > 86400):  # 24 часа
        
        # Создаем сессию
        session = SessionLocal()
        
        # Запрашиваем только нужные поля
        assets = session.query(AssetClass.ticker, AssetClass.asset_ru).all()
        
        # Преобразуем результат в список словарей
        result = [{"ticker": asset.ticker, "asset_ru": asset.asset_ru} for asset in assets]
        
        # Закрываем сессию
        session.close()
        
        # Обновляем кэш
        assets_cache["data"] = result
        assets_cache["last_update"] = current_time
        
    return assets_cache["data"]