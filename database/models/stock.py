from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime

from . import Base

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100))
    sector = Column(String(50))
    industry = Column(String(50))
    market_cap = Column(Float)
    current_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Fundamental data
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    dividend_yield = Column(Float)
    eps = Column(Float)
    revenue = Column(Float)
    profit_margin = Column(Float)
    
    # Technical data (cached)
    rsi = Column(Float)
    macd = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    
    # AI data
    ai_score = Column(Float)
    ai_confidence = Column(Float)
    predicted_return = Column(Float)
    recommendation = Column(String(20))
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"
