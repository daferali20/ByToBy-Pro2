import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import aiohttp
import asyncio
from loguru import logger

class DataService:
    def __init__(self):
        self.cache = {}
        self.last_update = {}
        self.cache_duration = 300  # 5 minutes
        self.alpha_vantage_key = "YOUR_API_KEY"  # Move to config
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical stock data"""
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            
            # Check cache
            if cache_key in self.cache:
                if (datetime.now() - self.last_update[cache_key]).seconds < self.cache_duration:
                    return self.cache[cache_key]
            
            # Fetch data
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Clean data
            data = data.dropna()
            
            # Cache
            self.cache[cache_key] = data
            self.last_update[cache_key] = datetime.now()
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    async def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "description": info.get("longBusinessSummary", ""),
                "employees": info.get("fullTimeEmployees", 0),
                "website": info.get("website", ""),
                "country": info.get("country", ""),
                "exchange": info.get("exchange", "")
            }
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            return {}
    
    async def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Get data for multiple stocks concurrently"""
        tasks = [self.get_historical_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result if not isinstance(result, Exception) else None
            for symbol, result in zip(symbols, results)
        }
    
    async def get_dividends(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get dividend history"""
        try:
            stock = yf.Ticker(symbol)
            dividends = stock.dividends.tail(limit)
            return [
                {"date": date.strftime("%Y-%m-%d"), "dividend": amount}
                for date, amount in dividends.items()
            ]
        except Exception as e:
            logger.error(f"Error getting dividends for {symbol}: {e}")
            return []
    
    async def get_splits(self, symbol: str) -> List[Dict]:
        """Get stock split history"""
        try:
            stock = yf.Ticker(symbol)
            splits = stock.splits
            return [
                {"date": date.strftime("%Y-%m-%d"), "split": ratio}
                for date, ratio in splits.items()
            ]
        except Exception as e:
            logger.error(f"Error getting splits for {symbol}: {e}")
            return []
