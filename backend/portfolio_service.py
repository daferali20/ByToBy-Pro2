from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from backend.stock_service import StockService
from backend.data_service import DataService

class PortfolioService:
    def __init__(self):
        self.stock_service = StockService()
        self.data_service = DataService()
        self.portfolio_data = {}
    
    def get_portfolio(self, user_id: str = None) -> Dict[str, Any]:
        """Get user portfolio"""
        # This is a sample portfolio - in production, get from database
        if not self.portfolio_data:
            self.portfolio_data = {
                'holdings': {
                    'AAPL': {'shares': 50, 'avg_price': 150.00},
                    'GOOGL': {'shares': 10, 'avg_price': 1400.00},
                    'MSFT': {'shares': 30, 'avg_price': 330.00},
                    'AMZN': {'shares': 5, 'avg_price': 3500.00},
                    'TSLA': {'shares': 20, 'avg_price': 250.00}
                },
                'cash': 10000.00
            }
        
        return self.portfolio_data
    
    def get_total_value(self) -> float:
        """Get total portfolio value"""
        portfolio = self.get_portfolio()
        total = portfolio.get('cash', 0)
        
        for symbol, holding in portfolio.get('holdings', {}).items():
            price = self.stock_service.get_current_price(symbol)
            if price:
                total += price * holding['shares']
        
        return total
    
    def get_daily_change(self) -> float:
        """Get daily change percentage"""
        try:
            portfolio = self.get_portfolio()
            total_value = self.get_total_value()
            
            # Calculate yesterday's value
            yesterday_value = portfolio.get('cash', 0)
            for symbol, holding in portfolio.get('holdings', {}).items():
                data = self.stock_service.get_historical_data(symbol, period="2d")
                if len(data) >= 2:
                    yester_price = data['Close'].iloc[-2]
                    yesterday_value += yester_price * holding['shares']
            
            if yesterday_value > 0:
                change = ((total_value - yesterday_value) / yesterday_value) * 100
                return change
            return 0
        except Exception as e:
            logger.error(f"Error calculating daily change: {e}")
            return 0
    
    def get_allocation(self) -> Dict[str, float]:
        """Get portfolio allocation by sector"""
        try:
            portfolio = self.get_portfolio()
            total_value = self.get_total_value()
            
            if total_value == 0:
                return {}
            
            sector_values = {}
            for symbol, holding in portfolio.get('holdings', {}).items():
                price = self.stock_service.get_current_price(symbol)
                if price:
                    value = price * holding['shares']
                    info = self.stock_service.get_company_info(symbol)
                    sector = info.get('sector', 'Other')
                    sector_values[sector] = sector_values.get(sector, 0) + value
            
            # Add cash
            cash = portfolio.get('cash', 0)
            if cash > 0:
                sector_values['Cash'] = cash
            
            # Convert to percentages
            for sector in sector_values:
                sector_values[sector] = (sector_values[sector] / total_value) * 100
            
            return sector_values
        except Exception as e:
            logger.error(f"Error calculating allocation: {e}")
            return {}
    
    def get_performance_data(self, period: str = "1y") -> pd.DataFrame:
        """Get portfolio performance data"""
        try:
            portfolio = self.get_portfolio()
            holdings = portfolio.get('holdings', {})
            
            if not holdings:
                return pd.DataFrame()
            
            # Get historical data for all holdings
            data = {}
            for symbol in holdings.keys():
                df = self.stock_service.get_historical_data(symbol, period)
                if not df.empty:
                    data[symbol] = df['Close']
            
            if not data:
                return pd.DataFrame()
            
            # Create portfolio value series
            dates = data[list(data.keys())[0]].index
            portfolio_values = []
            
            for date in dates:
                total = 0
                for symbol, prices in data.items():
                    if date in prices.index:
                        price = prices[date]
                        shares = holdings[symbol]['shares']
                        total += price * shares
                portfolio_values.append(total)
            
            return pd.DataFrame({
                'date': dates,
                'value': portfolio_values
            })
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return pd.DataFrame()
    
    def add_holding(self, symbol: str, shares: float, price: float) -> bool:
        """Add a holding to portfolio"""
        try:
            portfolio = self.get_portfolio()
            
            if symbol in portfolio['holdings']:
                # Update existing holding
                current = portfolio['holdings'][symbol]
                total_cost = (current['shares'] * current['avg_price']) + (shares * price)
                current['shares'] += shares
                current['avg_price'] = total_cost / current['shares']
            else:
                # Add new holding
                portfolio['holdings'][symbol] = {
                    'shares': shares,
                    'avg_price': price
                }
            
            return True
        except Exception as e:
            logger.error(f"Error adding holding: {e}")
            return False
    
    def remove_holding(self, symbol: str, shares: float) -> bool:
        """Remove shares from a holding"""
        try:
            portfolio = self.get_portfolio()
            
            if symbol in portfolio['holdings']:
                current = portfolio['holdings'][symbol]
                if shares >= current['shares']:
                    # Remove entire holding
                    del portfolio['holdings'][symbol]
                else:
                    # Reduce shares
                    current['shares'] -= shares
            
            return True
        except Exception as e:
            logger.error(f"Error removing holding: {e}")
            return False
