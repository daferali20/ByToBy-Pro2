import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import warnings
warnings.filterwarnings('ignore')

# Import backend modules
from backend.data_service import DataService
from backend.stock_service import StockService
from backend.screener_service import ScreenerService
from backend.portfolio_service import PortfolioService
from backend.ai_service import AIService
from backend.news_service import NewsService
from backend.utils import format_currency, format_percentage, get_stock_emoji

# Page configuration
st.set_page_config(
    page_title="ByToBy Pro2 AI - منصة تحليل الأسهم الذكية",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open('assets/css/style.css', 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Initialize services
@st.cache_resource
def init_services():
    return {
        'data': DataService(),
        'stock': StockService(),
        'screener': ScreenerService(),
        'portfolio': PortfolioService(),
        'ai': AIService(),
        'news': NewsService()
    }

services = init_services()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/0a0e17/00b4d8?text=ByToBy+Pro2", use_column_width=True)
    
    st.markdown("---")
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["📊 Dashboard", "🔍 Screener", "💼 Portfolio", "🤖 AI Analysis", "🔔 Alerts", "📰 News"],
        icons=["house", "search", "briefcase", "robot", "bell", "newspaper"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00b4d8", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#00b4d8", "color": "white"},
        }
    )
    
    st.markdown("---")
    
    # Market status
    market_status = services['data'].get_market_status()
    st.markdown(f"""
    <div style="background: rgba(0, 180, 216, 0.1); padding: 10px; border-radius: 10px; border-left: 3px solid #00b4d8;">
        <small style="color: #888;">Market Status</small><br>
        <span style="color: {'#00b894' if market_status['is_open'] else '#ff6b6b'}; font-weight: bold;">
            {market_status['status']}
        </span><br>
        <small style="color: #888;">{market_status['time']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick watchlist
    st.markdown("### ⭐ Watchlist")
    for symbol in st.session_state.watchlist[:5]:
        price = services['data'].get_current_price(symbol)
        change = services['data'].get_price_change(symbol)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{symbol}**")
        with col2:
            color = "#00b894" if change >= 0 else "#ff6b6b"
            st.markdown(f"<span style='color: {color};'>{format_currency(price)}</span>", unsafe_allow_html=True)

# Main content
if selected == "📊 Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard(services)
elif selected == "🔍 Screener":
    from pages.screener import show_screener
    show_screener(services)
elif selected == "💼 Portfolio":
    from pages.portfolio import show_portfolio
    show_portfolio(services)
elif selected == "🤖 AI Analysis":
    from pages.ai_analysis import show_ai_analysis
    show_ai_analysis(services)
elif selected == "🔔 Alerts":
    from pages.alerts import show_alerts
    show_alerts(services)
elif selected == "📰 News":
    from pages.news import show_news
    show_news(services)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("© 2024 ByToBy Pro2 AI")
with col2:
    st.markdown("[Privacy Policy] | [Terms of Service]")
with col3:
    st.markdown("v2.0.0")
