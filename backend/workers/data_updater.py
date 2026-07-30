from celery import Celery
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta

from backend.services import DataService, StockService
from database import DatabaseManager

app = Celery('bytoby', broker='redis://redis:6379/0')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

class DataUpdater:
    def __init__(self):
        self.data_service = DataService()
        self.stock_service = StockService()
        self.db_manager = DatabaseManager()
    
    @app.task
    def update_all_stocks(self):
        """Update all stocks in the database"""
        logger.info("Starting stock update")
        
        try:
            # Get list of active stocks
            active_stocks = self.db_manager.get_active_stocks()
            
            for symbol in active_stocks:
                try:
                    self.update_stock_data.delay(symbol)
                except Exception as e:
                    logger.error(f"Error queuing update for {symbol}: {e}")
            
            logger.info(f"Queued updates for {len(active_stocks)} stocks")
            return len(active_stocks)
        except Exception as e:
            logger.error(f"Error in update_all_stocks: {e}")
            return 0
    
    @app.task
    def update_stock_data(self, symbol: str):
        """Update data for a single stock"""
        logger.info(f"Updating data for {symbol}")
        
        try:
            # Get latest data
            data = self.data_service.get_historical_data(symbol, "1mo")
            if data.empty:
                logger.warning(f"No data for {symbol}")
                return
            
            # Calculate indicators
            indicators = self.stock_service.calculate_indicators(symbol, "1mo")
            if not indicators:
                logger.warning(f"No indicators for {symbol}")
                return
            
            # Get company info
            company_info = self.data_service.get_company_info(symbol)
            
            # Update database
            self.db_manager.update_stock_data(
                symbol=symbol,
                current_price=data['Close'].iloc[-1],
                indicators=indicators,
                company_info=company_info
            )
            
            logger.info(f"Updated data for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error updating data for {symbol}: {e}")
            return False
    
    @app.task
    def update_market_data(self):
        """Update overall market data"""
        logger.info("Updating market data")
        
        try:
            # Update major indices
            indices = ['SPY', 'QQQ', 'DIA', 'IWM']
            for idx in indices:
                data = self.data_service.get_historical_data(idx, "1mo")
                if not data.empty:
                    self.db_manager.update_market_index(
                        symbol=idx,
                        current_price=data['Close'].iloc[-1],
                        change=data['Close'].pct_change().iloc[-1] * 100
                    )
            
            logger.info("Market data updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            return False
