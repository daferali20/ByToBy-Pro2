import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock
from backend.services import StockService
from backend.services.data_service import DataService

@pytest.mark.asyncio
async def test_get_historical_data():
    # Create mock
    mock_data_service = AsyncMock(spec=DataService)
    mock_data_service.get_historical_data.return_value = pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [101, 102, 103],
        'Low': [99, 100, 101],
        'Close': [100.5, 101.5, 102.5],
        'Volume': [1000000, 1100000, 1200000]
    })
    
    stock_service = StockService()
    stock_service.data_service = mock_data_service
    
    result = await stock_service.get_historical_data('AAPL', '1d')
    
    assert not result.empty
    assert 'Close' in result.columns
    assert len(result) == 3

@pytest.mark.asyncio
async def test_calculate_indicators():
    stock_service = StockService()
    mock_data = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'Volume': [1000000] * 10
    })
    
    stock_service.data_service.get_historical_data = AsyncMock(return_value=mock_data)
    
    result = await stock_service.calculate_indicators('AAPL')
    
    assert 'rsi' in result
    assert 'macd' in result
    assert 'sma_20' in result
    assert result['sma_20'] is not None
