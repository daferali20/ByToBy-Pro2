import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger
from backend.stock_service import StockService
from backend.ai_service import AIService
from backend.data_service import DataService

class ScreenerService:
    def __init__(self):
        self.stock_service = StockService()
        self.ai_service = AIService()
        self.data_service = DataService()
        self.cache = {}
    
    def scan(self, filters: Dict[str, Any], sort_by: str = "market_cap", 
             sort_order: str = "desc") -> List[Dict]:
        """Scan stocks based on filters"""
        try:
            # Get list of stocks to scan
            stocks = self._get_stock_list()
            results = []
            
            for symbol in stocks:
                try:
                    # Get stock data
                    info = self.stock_service.get_company_info(symbol)
                    indicators = self.stock_service.calculate_indicators(symbol)
                    ai_pred = self.ai_service.predict(symbol)
                    
                    # Apply filters
                    if self._matches_filters(info, indicators, ai_pred, filters):
                        results.append({
                            'symbol': symbol,
                            'name': info.get('name', symbol),
                            'sector': info.get('sector', 'N/A'),
                            'price': info.get('current_price', 0),
                            'change': indicators.get('change_1d', 0),
                            'market_cap': info.get('market_cap', 0),
                            'pe_ratio': info.get('pe_ratio', 0),
                            'dividend_yield': info.get('dividend_yield', 0),
                            'rsi': indicators.get('rsi', 50),
                            'volume': indicators.get('volume_ratio', 1),
                            'ai_score': ai_pred.get('confidence', 0),
                            'predicted_return': ai_pred.get('predicted_return', 0),
                            'recommendation': ai_pred.get('recommendation', 'HOLD')
                        })
                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {e}")
                    continue
            
            # Sort results
            if sort_by == "market_cap":
                results.sort(key=lambda x: x.get('market_cap', 0), 
                           reverse=(sort_order == "desc"))
            elif sort_by == "price":
                results.sort(key=lambda x: x.get('price', 0), 
                           reverse=(sort_order == "desc"))
            elif sort_by == "pe_ratio":
                results.sort(key=lambda x: x.get('pe_ratio', float('inf')), 
                           reverse=(sort_order == "desc"))
            elif sort_by == "dividend_yield":
                results.sort(key=lambda x: x.get('dividend_yield', 0), 
                           reverse=(sort_order == "desc"))
            elif sort_by == "ai_score":
                results.sort(key=lambda x: x.get('ai_score', 0), 
                           reverse=(sort_order == "desc"))
            elif sort_by == "volume":
                results.sort(key=lambda x: x.get('volume', 0), 
                           reverse=(sort_order == "desc"))
            
            return results[:100]  # Limit results
            
        except Exception as e:
            logger.error(f"Error in screener: {e}")
            return []
    
    def _get_stock_list(self) -> List[str]:
        """Get list of stocks to scan"""
        # This is a sample list - in production use a real stock database
        return [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'VTI', 'SPY', 'QQQ', 'DIA', 'IWM', 'BND', 'GLD', 'SLV',
            'KO', 'PEP', 'MCD', 'DIS', 'NFLX', 'ADBE', 'CRM', 'ORCL',
            'IBM', 'CSCO', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU'
        ]
    
    def _matches_filters(self, info: Dict, indicators: Dict, 
                         ai_pred: Dict, filters: Dict) -> bool:
        """Check if stock matches all filters"""
        
        # Sector filter
        if filters.get('sector'):
            if info.get('sector') != filters['sector']:
                return False
        
        # Market cap filter
        if filters.get('market_cap_min') or filters.get('market_cap_max'):
            market_cap = info.get('market_cap', 0)
            if filters.get('market_cap_min') and market_cap < filters['market_cap_min']:
                return False
            if filters.get('market_cap_max') and market_cap > filters['market_cap_max']:
                return False
        
        # Price filter
        if filters.get('price_min') or filters.get('price_max'):
            price = info.get('current_price', 0)
            if filters.get('price_min') and price < filters['price_min']:
                return False
            if filters.get('price_max') and price > filters['price_max']:
                return False
        
        # P/E filter
        if filters.get('pe_min') or filters.get('pe_max'):
            pe = info.get('pe_ratio', 0)
            if filters.get('pe_min') and pe < filters['pe_min']:
                return False
            if filters.get('pe_max') and pe > filters['pe_max']:
                return False
        
        # Dividend filter
        if filters.get('dividend_min'):
            dividend = info.get('dividend_yield', 0)
            if dividend < filters['dividend_min']:
                return False
        
        # RSI filter
        if filters.get('rsi_min') or filters.get('rsi_max'):
            rsi = indicators.get('rsi', 50)
            if filters.get('rsi_min') and rsi < filters['rsi_min']:
                return False
            if filters.get('rsi_max') and rsi > filters['rsi_max']:
                return False
        
        # AI confidence filter
        if filters.get('ai_confidence_min'):
            confidence = ai_pred.get('confidence', 0)
            if confidence < filters['ai_confidence_min']:
                return False
        
        return True
