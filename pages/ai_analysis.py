import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container

def show_ai_analysis(services):
    """Display AI analysis page"""
    
    colored_header(
        label="🤖 AI Analysis",
        description="Advanced AI-powered stock analysis and predictions",
        color_name="blue-70"
    )
    
    # AI Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Overall Confidence",
            value=f"{services['ai'].get_overall_confidence():.1f}%",
            delta="Based on all stocks"
        )
    
    with col2:
        # Number of AI recommendations
        recommendations = services['ai'].get_recommendations()
        buy_count = sum(1 for r in recommendations if 'BUY' in r['Action'])
        st.metric(
            label="Buy Signals",
            value=buy_count,
            delta=f"out of {len(recommendations)} stocks"
        )
    
    with col3:
        # Average predicted return
        avg_return = np.mean([r['Return %'] for r in recommendations])
        st.metric(
            label="Avg Predicted Return",
            value=f"{avg_return:.1f}%",
            delta="Next 30 days"
        )
    
    with col4:
        # Highest confidence stock
        if recommendations:
            best = max(recommendations, key=lambda x: x['Confidence'])
            st.metric(
                label="Best AI Pick",
                value=best['Symbol'],
                delta=f"{best['Return %']:.1f}% predicted"
            )
    
    st.markdown("---")
    
    # AI Recommendations
    st.markdown("### 🎯 AI Recommendations")
    
    if recommendations:
        df = pd.DataFrame(recommendations)
        
        # Add color coding
        def color_action(val):
            if 'STRONG BUY' in val:
                return 'background-color: rgba(0, 184, 148, 0.3); color: #00b894; font-weight: bold'
            elif 'BUY' in val:
                return 'background-color: rgba(0, 184, 148, 0.15); color: #00b894;'
            elif 'HOLD' in val:
                return 'background-color: rgba(253, 203, 110, 0.15); color: #fdcb6e;'
            elif 'SELL' in val:
                return 'background-color: rgba(255, 107, 107, 0.15); color: #ff6b6b;'
            return ''
        
        styled_df = df.style.applymap(color_action, subset=['Action'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                "Price": st.column_config.TextColumn("Price"),
                "Target": st.column_config.TextColumn("Target Price"),
                "Return %": st.column_config.TextColumn("Return %"),
                "Confidence": st.column_config.TextColumn("Confidence"),
                "Action": st.column_config.TextColumn("Action"),
            }
        )
        
        # AI Score visualization
        st.markdown("### 📊 AI Confidence Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                df,
                x='Symbol',
                y='Confidence',
                color='Action',
                title='AI Confidence Scores',
                labels={'Confidence': 'Confidence (%)'}
            )
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                df,
                x='Confidence',
                y='Return %',
                color='Action',
                hover_name='Symbol',
                title='Confidence vs Predicted Return',
                labels={'Confidence': 'Confidence (%)', 'Return %': 'Predicted Return (%)'}
            )
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # AI Model Performance
    st.markdown("### 📈 Model Performance Metrics")
    
    # Sample performance data
    performance_metrics = {
        'Accuracy': 0.72,
        'Precision': 0.68,
        'Recall': 0.71,
        'F1 Score': 0.69,
        'Sharpe Ratio': 1.45,
        'Max Drawdown': -8.2
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Core Metrics")
        for metric, value in list(performance_metrics.items())[:3]:
            st.metric(
                label=metric,
                value=f"{value:.2f}" if isinstance(value, float) else value
            )
    
    with col2:
        st.markdown("#### 📈 Risk Metrics")
        for metric, value in list(performance_metrics.items())[3:5]:
            st.metric(
                label=metric,
                value=f"{value:.2f}" if isinstance(value, float) else value
            )
    
    with col3:
        st.markdown("#### 🎯 Target Metrics")
        st.metric(
            label="Min Confidence",
            value="60%"
        )
        st.metric(
            label="Min Return",
            value="5%"
        )
        st.metric(
            label="Max Risk",
            value="15%"
        )
    
    st.markdown("---")
    
    # Detailed stock analysis
    st.markdown("### 🔍 Detailed Stock Analysis")
    
    selected_symbol = st.selectbox(
        "Select stock for detailed analysis",
        options=df['Symbol'].tolist() if recommendations else ['AAPL']
    )
    
    if selected_symbol:
        with st.spinner(f"Analyzing {selected_symbol}..."):
            # Get detailed data
            info = services['stock'].get_company_info(selected_symbol)
            indicators = services['stock'].calculate_indicators(selected_symbol)
            prediction = services['ai'].predict(selected_symbol)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Price chart with predictions
                data = services['data'].get_historical_data(selected_symbol, period="3mo")
                if not data.empty:
                    fig = go.Figure()
                    
                    # Candlestick chart
                    fig.add_trace(go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name='Price'
                    ))
                    
                    # Prediction markers
                    if prediction:
                        fig.add_trace(go.Scatter(
                            x=[data.index[-1], data.index[-1] + pd.Timedelta(days=30)],
                            y=[data['Close'].iloc[-1], prediction.get('price', 0)],
                            mode='lines+markers',
                            name='AI Prediction',
                            line=dict(color='#fdcb6e', dash='dash', width=2),
                            marker=dict(size=10, color='#fdcb6e')
                        ))
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=500,
                        xaxis_rangeslider_visible=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Analysis Summary")
                
                # Show key metrics
                metrics = {
                    'Current Price': f"${prediction.get('current_price', 0):.2f}",
                    'AI Target': f"${prediction.get('price', 0):.2f}",
                    'Potential Return': f"{prediction.get('predicted_return', 0):.1f}%",
                    'Confidence': f"{prediction.get('confidence', 0)*100:.1f}%",
                    'Recommendation': prediction.get('recommendation', 'HOLD'),
                    'RSI': f"{indicators.get('rsi', 50):.1f}"
                }
                
                for key, value in metrics.items():
                    color = '#00b894' if 'BUY' in value or 'STRONG BUY' in value else '#ff6b6b' if 'SELL' in value else '#fdcb6e' if 'HOLD' in value else '#888'
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="color: #888;">{key}</span>
                        <span style="color: {color}; font-weight: bold;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
