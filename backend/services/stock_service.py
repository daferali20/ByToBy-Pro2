import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import ta
from sklearn.preprocessing import MinMaxScaler
from loguru import logger

from .data_service import DataService
from backend.indicators import TechnicalIndicators
from backend.valuation import ValuationCalculator
from backend.news import NewsAnalyzer
from backend.ml_models import StockPredictor

class StockService:
    def __init__(self):
        self.data_service = DataService()
        self.tech_indicators = TechnicalIndicators()
        self.valuation_calc = ValuationCalculator()
        self.news_analyzer = NewsAnalyzer()
        self.predictor = StockPredictor()
    
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical data for a stock"""
        return await self.data_service.get_historical_data(symbol, period, interval)
    
    async def calculate_indicators(
        self, 
        symbol: str,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """Calculate technical indicators for a stock"""
        try:
            data = await self.get_historical_data(symbol, period)
            if data.empty:
                return {}
            
            # Calculate various indicators
            indicators = {}
            
            # Trend indicators
            indicators["sma_20"] = ta.trend.sma_indicator(data['Close'], window=20).iloc[-1]
            indicators["sma_50"] = ta.trend.sma_indicator(data['Close'], window=50).iloc[-1]
            indicators["sma_200"] = ta.trend.sma_indicator(data['Close'], window=200).iloc[-1]
            indicators["ema_12"] = ta.trend.ema_indicator(data['Close'], window=12).iloc[-1]
            indicators["ema_26"] = ta.trend.ema_indicator(data['Close'], window=26).iloc[-1]
            
            # MACD
            macd = ta.trend.MACD(data['Close'])
            indicators["macd"] = macd.macd().iloc[-1]
            indicators["macd_signal"] = macd.macd_signal().iloc[-1]
            indicators["macd_diff"] = macd.macd_diff().iloc[-1]
            
            # Momentum indicators
            indicators["rsi"] = ta.momentum.rsi(data['Close'], window=14).iloc[-1]
            indicators["stoch_k"] = ta.momentum.stochrsi_k(data['Close'], window=14).iloc[-1]
            indicators["stoch_d"] = ta.momentum.stochrsi_d(data['Close'], window=14).iloc[-1]
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
            indicators["bb_high"] = bb.bollinger_hband().iloc[-1]
            indicators["bb_low"] = bb.bollinger_lband().iloc[-1]
            indicators["bb_mid"] = bb.bollinger_mavg().iloc[-1]
            indicators["bb_width"] = (bb.bollinger_hband().iloc[-1] - bb.bollinger_lband().iloc[-1]) / bb.bollinger_mavg().iloc[-1]
            
            # Volume indicators
            indicators["volume_sma"] = data['Volume'].rolling(window=20).mean().iloc[-1]
            indicators["volume_ratio"] = data['Volume'].iloc[-1] / indicators["volume_sma"]
            
            # Price changes
            indicators["price_change_1d"] = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
            indicators["price_change_1w"] = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
            indicators["price_change_1m"] = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    async def get_valuation_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get valuation metrics for a stock"""
        try:
            info = await self.data_service.get_company_info(symbol)
            if not info:
                return {}
            
            metrics = self.valuation_calc.calculate_metrics(symbol, info)
            return metrics
        except Exception as e:
            logger.error(f"Error getting valuation metrics for {symbol}: {e}")
            return {}
    
    async def get_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get news sentiment for a stock"""
        try:
            sentiment = await self.news_analyzer.analyze_stock_news(symbol)
            return sentiment
        except Exception as e:
            logger.error(f"Error getting news sentiment for {symbol}: {e}")
            return {}
    
    async def get_ai_prediction(self, symbol: str) -> Dict[str, Any]:
        """Get AI-based prediction for a stock"""
        try:
            data = await self.get_historical_data(symbol, "2y")
            if data.empty:
                return {}
            
            # Prepare features
            features = self.prepare_features(data)
            
            # Get prediction
            prediction = await self.predictor.predict(features)
            
            return {
                "predicted_price": prediction['price'],
                "confidence": prediction['confidence'],
                "target_low": prediction['target_low'],
                "target_high": prediction['target_high'],
                "recommendation": prediction['recommendation'],
                "time_horizon": "1 week"
            }
        except Exception as e:
            logger.error(f"Error getting AI prediction for {symbol}: {e}")
            return {}
    
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for AI prediction"""
        # Calculate technical indicators
        indicators = pd.DataFrame()
        indicators['rsi'] = ta.momentum.rsi(data['Close'], window=14)
        indicators['macd'] = ta.trend.MACD(data['Close']).macd()
        indicators['sma_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        indicators['sma_50'] = ta.trend.sma_indicator(data['Close'], window=50)
        indicators['bb_high'] = ta.volatility.BollingerBands(data['Close']).bollinger_hband()
        indicators['bb_low'] = ta.volatility.BollingerBands(data['Close']).bollinger_lband()
        
        # Add returns
        indicators['returns'] = data['Close'].pct_change()
        indicators['returns_5d'] = data['Close'].pct_change(periods=5)
        indicators['returns_20d'] = data['Close'].pct_change(periods=20)
        
        # Add volume
        indicators['volume_ratio'] = data['Volume'] / data['Volume'].rolling(window=20).mean()
        
        # Drop NaN values
        indicators = indicators.dropna()
        
        # Normalize
        scaler = MinMaxScaler()
        features = scaler.fit_transform(indicators)
        
        return features[-60:]  # Last 60 days
    
    async def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for stocks"""
        # This is a simplified version - in production, use a proper API
        import yfinance as yf
        
        try:
            # Get all stock symbols (this is simplified)
            # In production, use a proper stock database
            all_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'VTI', 'SPY']
            
            results = []
            for symbol in all_stocks:
                if query.upper() in symbol or query.lower() in symbol:
                    info = await self.data_service.get_company_info(symbol)
                    if info:
                        results.append(info)
                        if len(results) >= limit:
                            break
            
            return results
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
    
    async def get_technical_summary(self, symbol: str) -> Dict[str, Any]:
        """Get technical summary with signals"""
        try:
            indicators = await self.calculate_indicators(symbol)
            data = await self.get_historical_data(symbol, "1mo")
            
            if data.empty:
                return {}
            
            current_price = data['Close'].iloc[-1]
            
            # Generate signals
            signals = []
            
            # RSI signal
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                signals.append({"indicator": "RSI", "signal": "BUY", "value": rsi})
            elif rsi > 70:
                signals.append({"indicator": "RSI", "signal": "SELL", "value": rsi})
            else:
                signals.append({"indicator": "RSI", "signal": "NEUTRAL", "value": rsi})
            
            # MACD signal
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                signals.append({"indicator": "MACD", "signal": "BUY", "value": macd})
            else:
                signals.append({"indicator": "MACD", "signal": "SELL", "value": macd})
            
            # SMA signal
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            if sma_20 > sma_50:
                signals.append({"indicator": "SMA", "signal": "BULLISH", "value": sma_20})
            else:
                signals.append({"indicator": "SMA", "signal": "BEARISH", "value": sma_20})
            
            # Bollinger Bands signal
            bb_high = indicators.get('bb_high', 0)
            bb_low = indicators.get('bb_low', 0)
            if current_price > bb_high:
                signals.append({"indicator": "Bollinger", "signal": "OVERSOLD", "value": current_price})
            elif current_price < bb_low:
                signals.append({"indicator": "Bollinger", "signal": "OVERBOUGHT", "value": current_price})
            else:
                signals.append({"indicator": "Bollinger", "signal": "NEUTRAL", "value": current_price})
            
            # Calculate overall recommendation
            buy_signals = sum(1 for s in signals if s['signal'] in ['BUY', 'BULLISH'])
            sell_signals = sum(1 for s in signals if s['signal'] in ['SELL', 'BEARISH'])
            
            if buy_signals > sell_signals:
                recommendation = "BUY"
            elif sell_signals > buy_signals:
                recommendation = "SELL"
            else:
                recommendation = "HOLD"
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "signals": signals,
                "recommendation": recommendation,
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting technical summary for {symbol}: {e}")
            return {}
