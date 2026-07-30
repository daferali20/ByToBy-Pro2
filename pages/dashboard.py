import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import numpy as np

def show_dashboard(services):
    """Display the main dashboard"""
    
    colored_header(
        label="📊 Dashboard Overview",
        description="Real-time market insights and portfolio performance",
        color_name="blue-70"
    )
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        spy = services['data'].get_current_price('SPY')
        st.metric(
            label="S&P 500",
            value=f"${spy:.2f}" if spy else "N/A",
            delta=f"{services['data'].get_price_change('SPY'):.2f}%",
            delta_color="normal"
        )
    
    with col2:
        qqq = services['data'].get_current_price('QQQ')
        st.metric(
            label="NASDAQ",
            value=f"${qqq:.2f}" if qqq else "N/A",
            delta=f"{services['data'].get_price_change('QQQ'):.2f}%",
            delta_color="normal"
        )
    
    with col3:
        dia = services['data'].get_current_price('DIA')
        st.metric(
            label="Dow Jones",
            value=f"${dia:.2f}" if dia else "N/A",
            delta=f"{services['data'].get_price_change('DIA'):.2f}%",
            delta_color="normal"
        )
    
    with col4:
        # Portfolio value
        total_value = services['portfolio'].get_total_value()
        st.metric(
            label="Portfolio Value",
            value=f"${total_value:,.2f}",
            delta=f"{services['portfolio'].get_daily_change():.2f}%",
            delta_color="normal"
        )
    
    with col5:
        # AI Confidence
        ai_confidence = services['ai'].get_overall_confidence()
        st.metric(
            label="AI Confidence",
            value=f"{ai_confidence:.1f}%",
            delta="Based on 50 stocks",
            delta_color="off"
        )
    
    style_metric_cards(
        background_color="rgba(20, 27, 45, 0.6)",
        border_left_color="#00b4d8",
        border_color="rgba(255, 255, 255, 0.05)",
        box_shadow=True
    )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Market Performance")
        
        # Get market data
        symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
        data = {}
        for symbol in symbols:
            df = services['data'].get_historical_data(symbol, period="1mo")
            if not df.empty:
                data[symbol] = df['Close'] / df['Close'].iloc[0] * 100
        
        if data:
            fig = go.Figure()
            for symbol, values in data.items():
                fig.add_trace(go.Scatter(
                    x=values.index,
                    y=values,
                    mode='lines',
                    name=symbol,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Market Indices Performance (1 Month)",
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                template="plotly_dark",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Portfolio Allocation")
        
        # Get portfolio allocation
        allocation = services['portfolio'].get_allocation()
        
        if allocation:
            fig = go.Figure(data=[go.Pie(
                labels=list(allocation.keys()),
                values=list(allocation.values()),
                hole=0.6,
                marker=dict(colors=['#00b4d8', '#0077b6', '#00b894', '#fdcb6e', '#6c5ce7'])
            )])
            
            fig.update_layout(
                template="plotly_dark",
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Watchlist and Top Movers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⭐ Watchlist")
        
        watchlist_data = []
        for symbol in st.session_state.watchlist:
            price = services['data'].get_current_price(symbol)
            change = services['data'].get_price_change(symbol)
            if price:
                watchlist_data.append({
                    'Symbol': symbol,
                    'Price': price,
                    'Change %': change,
                    'AI Score': services['ai'].get_score(symbol)
                })
        
        if watchlist_data:
            df = pd.DataFrame(watchlist_data)
            
            # Color coding for changes
            def color_change(val):
                color = '#00b894' if val > 0 else '#ff6b6b' if val < 0 else '#888'
                return f'color: {color}; font-weight: bold'
            
            styled_df = df.style.applymap(
                color_change, subset=['Change %']
            ).format({
                'Price': '${:.2f}',
                'Change %': '{:.2f}%',
                'AI Score': '{:.1f}%'
            })
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                height=300
            )
    
    with col2:
        st.markdown("### 🚀 Top Movers")
        
        # Get top gainers and losers
        top_movers = services['data'].get_top_movers()
        
        if top_movers:
            gainers, losers = top_movers
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### 📈 Top Gainers")
                for stock in gainers[:5]:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span><strong>{stock['symbol']}</strong></span>
                        <span style="color: #00b894;">+{stock['change']:.2f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown("#### 📉 Top Losers")
                for stock in losers[:5]:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span><strong>{stock['symbol']}</strong></span>
                        <span style="color: #ff6b6b;">{stock['change']:.2f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI Recommendations
    st.markdown("### 🤖 AI Stock Recommendations")
    
    recommendations = services['ai'].get_recommendations()
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        
        # Create a more visual display
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=rec_df['Symbol'],
            y=rec_df['Confidence'],
            name='Confidence',
            marker_color=rec_df['Confidence'].apply(
                lambda x: '#00b894' if x > 70 else '#fdcb6e' if x > 50 else '#ff6b6b'
            ),
            text=rec_df['Confidence'].apply(lambda x: f'{x:.0f}%'),
            textposition='auto',
        ))
        
        fig.update_layout(
            title="AI Confidence Score by Stock",
            xaxis_title="Stock",
            yaxis_title="Confidence (%)",
            template="plotly_dark",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display recommendations as cards
        cols = st.columns(len(recommendations))
        for idx, rec in enumerate(recommendations[:4]):
            with cols[idx]:
                with stylable_container(
                    key=f"rec_{rec['Symbol']}",
                    css_styles="""
                    {
                        background-color: rgba(20, 27, 45, 0.6);
                        border-radius: 10px;
                        padding: 15px;
                        border-left: 3px solid #00b4d8;
                    }
                    """
                ):
                    st.markdown(f"""
                    **{rec['Symbol']}**
                    <br>
                    <span style="font-size: 24px; font-weight: bold;">{rec['Action']}</span>
                    <br>
                    <small>Confidence: {rec['Confidence']:.1f}%</small>
                    <br>
                    <small>Target: ${rec['Target']:.2f}</small>
                    """, unsafe_allow_html=True)
