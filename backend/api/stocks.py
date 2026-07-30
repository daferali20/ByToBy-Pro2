from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd

from backend.services import StockService, DataService
from backend.schemas import StockData, StockAnalysis, TechnicalIndicators

router = APIRouter()

@router.get("/{symbol}", response_model=StockData)
async def get_stock_data(
    symbol: str,
    period: str = Query("1y", description="Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 1d, 5d, 1wk, 1mo")
):
    """Get stock data for a symbol"""
    stock_service = StockService()
    data = await stock_service.get_historical_data(symbol, period, interval)
    
    if data is None or data.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    
    return {
        "symbol": symbol,
        "data": data.to_dict(orient="records"),
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/{symbol}/analysis", response_model=StockAnalysis)
async def get_stock_analysis(symbol: str):
    """Get comprehensive stock analysis"""
    stock_service = StockService()
    
    # Get technical indicators
    technical = await stock_service.get_technical_indicators(symbol)
    
    # Get valuation metrics
    valuation = await stock_service.get_valuation_metrics(symbol)
    
    # Get news sentiment
    sentiment = await stock_service.get_news_sentiment(symbol)
    
    # Get AI prediction
    prediction = await stock_service.get_ai_prediction(symbol)
    
    return {
        "symbol": symbol,
        "technical": technical,
        "valuation": valuation,
        "sentiment": sentiment,
        "prediction": prediction,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/{symbol}/indicators", response_model=TechnicalIndicators)
async def get_technical_indicators(
    symbol: str,
    period: str = Query("1y", description="Data period")
):
    """Get technical indicators for a stock"""
    stock_service = StockService()
    indicators = await stock_service.calculate_indicators(symbol, period)
    return indicators

@router.get("/search")
async def search_stocks(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Search for stocks by symbol or name"""
    stock_service = StockService()
    results = await stock_service.search_stocks(query, limit)
    return {"results": results, "count": len(results)}
