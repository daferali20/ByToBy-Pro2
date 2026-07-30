import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta
from typing import Dict, Any, Optional, List
from loguru import logger
import asyncio

class StockService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a stock"""
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            
            # Check cache
            if cache_key in self.cache:
                if (datetime.now() - self.cache[cache_key]['timestamp']).seconds < self.cache_duration:
                    return self.cache[cache_key]['data']
            
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                return pd.DataFrame()
            
            # Cache
            self.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            data = self.get_historical_data(symbol, period)
            if data.empty:
                return {}
            
            indicators = {}
            
            # Trend indicators
            if len(data) >= 20:
                indicators['sma_20'] = ta.trend.sma_indicator(data['Close'], window=20).iloc[-1]
                indicators['sma_50'] = ta.trend.sma_indicator(data['Close'], window=50).iloc[-1] if len(data) >= 50 else None
                indicators['sma_200'] = ta.trend.sma_indicator(data['Close'], window=200).iloc[-1] if len(data) >= 200 else None
            
            # Momentum indicators
            if len(data) >= 14:
                indicators['rsi'] = ta.momentum.rsi(data['Close'], window=14).iloc[-1]
                
                macd = ta.trend.MACD(data['Close'])
                indicators['macd'] = macd.macd().iloc[-1]
                indicators['macd_signal'] = macd.macd_signal().iloc[-1]
                indicators['macd_diff'] = macd.macd_diff().iloc[-1]
            
            # Volatility indicators
            if len(data) >= 20:
                bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
                indicators['bb_high'] = bb.bollinger_hband().iloc[-1]
                indicators['bb_low'] = bb.bollinger_lband().iloc[-1]
                indicators['bb_mid'] = bb.bollinger_mavg().iloc[-1]
            
            # Volume indicators
            if len(data) >= 20:
                indicators['volume_sma'] = data['Volume'].rolling(window=20).mean().iloc[-1]
                indicators['volume_ratio'] = data['Volume'].iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1
            
            # Price changes
            if len(data) >= 2:
                indicators['change_1d'] = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
            if len(data) >= 5:
                indicators['change_1w'] = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
            if len(data) >= 20:
                indicators['change_1m'] = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'target_high': info.get('targetHighPrice', 0),
                'target_low': info.get('targetLowPrice', 0),
                'target_mean': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationKey', 'hold').upper(),
                'description': info.get('longBusinessSummary', ''),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'country': info.get('country', '')
            }
        except Exception as e:
            logger.error(f"Error getting company info for {symbol}: {e}")
            return {'symbol': symbol, 'name': symbol}
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            info = self.get_company_info(symbol)
            return info.get('current_price')
        except:
            return None
    
    def get_price_change(self, symbol: str) -> float:
        """Get daily price change percentage"""
        try:
            data = self.get_historical_data(symbol, period="5d")
            if len(data) >= 2:
                return (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
            return 0
        except:
            return 0
    
    def get_top_movers(self, limit: int = 10) -> tuple:
        """Get top gainers and losers"""
        # This is a simplified version - in production, use a real API
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'VTI', 'SPY']
        
        movers = []
        for symbol in symbols:
            change = self.get_price_change(symbol)
            price = self.get_current_price(symbol)
            if price and change:
                movers.append({
                    'symbol': symbol,
                    'change': change,
                    'price': price
                })
        
        # Sort by change
        movers.sort(key=lambda x: x['change'], reverse=True)
        
        gainers = movers[:limit]
        losers = movers[-limit:][::-1]  # Reverse to get most negative first
        
        return gainers, losers
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks"""
        # This is a simplified implementation
        # In production, use a proper stock database or API
        common_stocks = {
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com, Inc.',
            'TSLA': 'Tesla, Inc.',
            'META': 'Meta Platforms, Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'VTI': 'Vanguard Total Stock Market ETF',
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust',
            'DIA': 'SPDR Dow Jones Industrial Average ETF',
            'IWM': 'iShares Russell 2000 ETF'
        }
        
        results = []
        query_lower = query.lower()
        
        for symbol, name in common_stocks.items():
            if query_lower in symbol.lower() or query_lower in name.lower():
                info = self.get_company_info(symbol)
                if info:
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'sector': info.get('sector', 'N/A'),
                        'market_cap': info.get('market_cap', 0)
                    })
                    if len(results) >= limit:
                        break
        
        return results
