from typing import Union, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def format_currency(value: Union[int, float, None]) -> str:
    """Format value as currency"""
    if value is None:
        return "N/A"
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    if abs(value) >= 1e3:
        return f"${value/1e3:.2f}K"
    return f"${value:.2f}"

def format_percentage(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format value as percentage"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"

def get_stock_emoji(symbol: str) -> str:
    """Get emoji for stock symbol"""
    emojis = {
        'AAPL': '🍎',
        'GOOGL': '🔍',
        'MSFT': '💻',
        'AMZN': '📦',
        'TSLA': '🚗',
        'META': '👁️',
        'NVDA': '🎮',
        'JPM': '🏦',
        'SPY': '📊',
        'QQQ': '📈',
        'DIA': '🏛️',
        'IWM': '📊',
        'BND': '📜',
        'GLD': '🪙'
    }
    return emojis.get(symbol.upper(), '📊')

def get_trend_icon(value: float) -> str:
    """Get trend icon based on value"""
    if value > 0:
        return '📈'
    elif value < 0:
        return '📉'
    return '➖'

def get_trend_color(value: float) -> str:
    """Get color for trend indicator"""
    if value > 0:
        return '#00b894'
    elif value < 0:
        return '#ff6b6b'
    return '#888'

def calculate_position_size(price: float, risk: float, account_size: float, 
                           stop_loss_pct: float = 0.02) -> float:
    """Calculate position size based on risk management"""
    risk_amount = account_size * risk
    stop_loss = price * stop_loss_pct
    if stop_loss > 0:
        return risk_amount / stop_loss
    return 0

def get_market_status() -> Dict[str, Any]:
    """Get current market status"""
    now = datetime.now()
    
    # US market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # Check if today is a weekend
    is_weekend = now.weekday() >= 5
    
    # Check if market is open
    is_open = (not is_weekend and market_open <= now <= market_close)
    
    status = "Open" if is_open else "Closed" if not is_weekend else "Weekend"
    status += " 🟢" if is_open else " 🔴"
    
    return {
        'status': status,
        'is_open': is_open,
        'time': now.strftime('%H:%M %Z'),
        'date': now.strftime('%Y-%m-%d')
    }

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    if len(returns) < 2:
        return 0
    
    excess_returns = returns - risk_free_rate / 252  # Daily
    if excess_returns.std() > 0:
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    return 0

def calculate_max_drawdown(returns: pd.Series) -> float:
    """Calculate maximum drawdown"""
    if len(returns) < 2:
        return 0
    
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_win_rate(trades: List[Dict]) -> float:
    """Calculate win rate from trades"""
    if not trades:
        return 0
    
    wins = sum(1 for t in trades if t.get('profit', 0) > 0)
    return wins / len(trades)

def calculate_profit_factor(trades: List[Dict]) -> float:
    """Calculate profit factor"""
    if not trades:
        return 0
    
    total_profit = sum(t.get('profit', 0) for t in trades if t.get('profit', 0) > 0)
    total_loss = abs(sum(t.get('profit', 0) for t in trades if t.get('profit', 0) < 0))
    
    if total_loss == 0:
        return float('inf')
    return total_profit / total_loss

def get_sector_etf(sector: str) -> str:
    """Get ETF symbol for a sector"""
    sector_etfs = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Finance': 'XLF',
        'Energy': 'XLE',
        'Consumer': 'XLP',
        'Industrial': 'XLI',
        'Materials': 'XLB',
        'Real Estate': 'XLRE',
        'Utilities': 'XLU'
    }
    return sector_etfs.get(sector, 'SPY')

def is_market_hours() -> bool:
    """Check if currently in market hours"""
    status = get_market_status()
    return status['is_open']

def get_time_until_market_open() -> Optional[timedelta]:
    """Get time until market opens"""
    now = datetime.now()
    next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    # If today is weekend or after close, get next day
    if now.weekday() >= 5 or now > next_open.replace(hour=16):
        days_until = (7 - now.weekday()) if now.weekday() >= 5 else 1
        next_open = next_open + timedelta(days=days_until)
    
    if next_open > now:
        return next_open - now
    return None
