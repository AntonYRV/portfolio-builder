from sqlalchemy import Column, String, Float, Date, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class StockValue(Base):
    __tablename__ = "stock_values"
    tradedate = Column(Date, primary_key=True)
    ticker = Column(String, primary_key=True)
    close = Column(Float)

class IndexValue(Base):
    __tablename__ = "index_values"
    tradedate = Column(Date, primary_key=True)
    secid = Column(String, primary_key=True)
    close = Column(Float)

class CurrencyValue(Base):
    __tablename__ = "currency_values"
    tradedate = Column(Date, primary_key=True)
    secid = Column(String, primary_key=True)
    close = Column(Float)

class AllAssetValue(Base):
    __tablename__ = 'all_assets'
    __table_args__ = {'extend_existing': True}  # важно для view

    tradedate = Column(Date, primary_key=True)
    ticker = Column(String, primary_key=True)
    close = Column(Float)
    asset_type = Column(String)  # 'stock', 'index', 'currency', ...

    def __repr__(self):
        return (
            f"<AllAssetValue(ticker='{self.ticker}', date='{self.tradedate}', "
            f"close={self.close}, type='{self.asset_type}')>"
        )
    
class AssetClass(Base):
    __tablename__ = 'asset_classes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_ru = Column(String)   # Группа, например "Рынок акций"
    asset_en = Column(String)   # Перевод
    name_ru = Column(String)    # Полное название индекса
    ticker = Column(String, unique=True)  # Тикер

    def __repr__(self):
        return f"<AssetClass(ticker={self.ticker}, asset_ru={self.asset_ru})>"

