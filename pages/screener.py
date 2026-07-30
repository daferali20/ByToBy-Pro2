import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
from streamlit_aggrid import AgGrid, GridOptionsBuilder, JsCode
import numpy as np

def show_screener(services):
    """Display the stock screener"""
    
    st.markdown("### 🔍 Advanced Stock Screener")
    st.markdown("Filter stocks using advanced criteria and AI-powered insights")
    
    # Filters section
    with st.expander("🔧 Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sector = st.selectbox(
                "Sector",
                ["All", "Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"]
            )
            
            market_cap_range = st.slider(
                "Market Cap (B)",
                min_value=0.0,
                max_value=1000.0,
                value=(0.0, 1000.0),
                step=10.0
            )
        
        with col2:
            min_price = st.number_input("Min Price ($)", min_value=0.0, value=0.0)
            max_price = st.number_input("Max Price ($)", min_value=0.0, value=1000.0)
            
            pe_range = st.slider(
                "P/E Ratio",
                min_value=0,
                max_value=100,
                value=(0, 50)
            )
        
        with col3:
            min_dividend = st.slider(
                "Min Dividend Yield (%)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.5
            )
            
            rsi_range = st.slider(
                "RSI Range",
                min_value=0,
                max_value=100,
                value=(30, 70)
            )
        
        with col4:
            ai_confidence = st.slider(
                "AI Confidence Score",
                min_value=0,
                max_value=100,
                value=50,
                step=5
            )
            
            sort_by = st.selectbox(
                "Sort By",
                ["Market Cap", "Price", "P/E Ratio", "Dividend Yield", "AI Score", "Volume"]
            )
            
            sort_order = st.radio(
                "Sort Order",
                ["Descending", "Ascending"],
                horizontal=True
            )
        
        # Search button
        if st.button("🔍 Scan Stocks", use_container_width=True):
            with st.spinner("Scanning stocks..."):
                # Get filtered stocks
                filters = {
                    'sector': sector if sector != "All" else None,
                    'market_cap_min': market_cap_range[0] * 1e9,
                    'market_cap_max': market_cap_range[1] * 1e9,
                    'price_min': min_price,
                    'price_max': max_price,
                    'pe_min': pe_range[0],
                    'pe_max': pe_range[1],
                    'dividend_min': min_dividend,
                    'rsi_min': rsi_range[0],
                    'rsi_max': rsi_range[1],
                    'ai_confidence_min': ai_confidence / 100
                }
                
                results = services['screener'].scan(filters, sort_by, sort_order)
                st.session_state['screener_results'] = results
    
    # Display results
    if 'screener_results' in st.session_state and st.session_state['screener_results']:
        results = st.session_state['screener_results']
        
        st.markdown(f"### 📊 Results: {len(results)} stocks found")
        
        # Metrics summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_ai_score = np.mean([r.get('ai_score', 0) for r in results]) * 100
            st.metric("Avg AI Score", f"{avg_ai_score:.1f}%")
        with col2:
            avg_return = np.mean([r.get('predicted_return', 0) for r in results])
            st.metric("Avg Predicted Return", f"{avg_return:.1f}%")
        with col3:
            total_market_cap = sum([r.get('market_cap', 0) for r in results]) / 1e9
            st.metric("Total Market Cap", f"${total_market_cap:.1f}B")
        with col4:
            high_confidence = len([r for r in results if r.get('ai_score', 0) > 0.7])
            st.metric("High Confidence Stocks", high_confidence)
        
        # Create dataframe for display
        df = pd.DataFrame(results)
        
        # Add color highlighting
        def highlight_ai_score(val):
            if val > 0.7:
                return 'background-color: rgba(0, 184, 148, 0.2); color: #00b894; font-weight: bold'
            elif val > 0.5:
                return 'background-color: rgba(253, 203, 110, 0.2); color: #fdcb6e;'
            return ''
        
        def highlight_recommendation(val):
            if val == 'STRONG BUY':
                return 'background-color: rgba(0, 184, 148, 0.3); color: #00b894; font-weight: bold'
            elif val == 'BUY':
                return 'background-color: rgba(0, 184, 148, 0.15); color: #00b894;'
            elif val == 'HOLD':
                return 'background-color: rgba(253, 203, 110, 0.15); color: #fdcb6e;'
            elif val in ['SELL', 'STRONG SELL']:
                return 'background-color: rgba(255, 107, 107, 0.15); color: #ff6b6b;'
            return ''
        
        # Format columns
        display_df = df.copy()
        display_df['Market Cap'] = display_df['market_cap'].apply(
            lambda x: f"${x/1e9:.2f}B" if x > 1e9 else f"${x/1e6:.2f}M"
        )
        display_df['AI Score'] = display_df['ai_score'].apply(lambda x: f"{x*100:.1f}%")
        display_df['Predicted Return'] = display_df['predicted_return'].apply(
            lambda x: f"{x*100:.1f}%"
        )
        
        # Select columns for display
        display_columns = ['symbol', 'name', 'price', 'change', 'Market Cap', 
                         'pe_ratio', 'dividend_yield', 'rsi', 'AI Score', 
                         'Predicted Return', 'recommendation']
        
        # Filter columns that exist
        display_columns = [col for col in display_columns if col in display_df.columns]
        display_df = display_df[display_columns]
        
        # Rename columns
        display_df.columns = ['Symbol', 'Name', 'Price', 'Change %', 'Market Cap',
                             'P/E', 'Div Yield %', 'RSI', 'AI Score',
                             'Predicted Return', 'Recommendation']
        
        # Display with AgGrid
        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_selection('single', use_checkbox=False)
        
        # Column configurations
        gb.configure_column('Symbol', pinned=True, width=80)
        gb.configure_column('Name', width=150)
        gb.configure_column('Price', type=["numericColumn", "numberColumnFilter"], 
                           valueFormatter="'$' + value.toFixed(2)")
        gb.configure_column('Change %', type=["numericColumn", "numberColumnFilter"],
                           valueFormatter="value.toFixed(2) + '%'")
        gb.configure_column('Market Cap', width=100)
        gb.configure_column('P/E', type=["numericColumn", "numberColumnFilter"])
        gb.configure_column('Div Yield %', type=["numericColumn", "numberColumnFilter"],
                           valueFormatter="value.toFixed(2) + '%'")
        gb.configure_column('RSI', type=["numericColumn", "numberColumnFilter"])
        gb.configure_column('AI Score', type=["numericColumn", "numberColumnFilter"])
        gb.configure_column('Predicted Return', type=["numericColumn", "numberColumnFilter"],
                           valueFormatter="value.toFixed(1) + '%'")
        
        grid_options = gb.build()
        
        grid_response = AgGrid(
            display_df,
            gridOptions=grid_options,
            height=400,
            width='100%',
            theme='dark',
            enable_enterprise_modules=False,
            allow_unsafe_jscode=True,
            key='screener_grid'
        )
        
        # Selected stock
        if grid_response['selected_rows']:
            selected = grid_response['selected_rows']
            stock_symbol = selected[0]['Symbol']
            show_stock_detail(stock_symbol, services)
        
        # Visualization of results
        st.markdown("### 📊 Screener Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # AI Score distribution
            fig = px.histogram(
                df,
                x='ai_score',
                nbins=20,
                title='AI Score Distribution',
                labels={'ai_score': 'AI Score', 'count': 'Number of Stocks'},
                color_discrete_sequence=['#00b4d8']
            )
            fig.update_layout(template='plotly_dark', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sector distribution
            sector_counts = df['sector'].value_counts()
            fig = px.pie(
                values=sector_counts.values,
                names=sector_counts.index,
                title='Sector Distribution',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_layout(template='plotly_dark', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot
        fig = px.scatter(
            df,
            x='pe_ratio',
            y='predicted_return',
            size='market_cap',
            color='sector',
            hover_name='symbol',
            title='P/E Ratio vs Predicted Return',
            labels={'pe_ratio': 'P/E Ratio', 'predicted_return': 'Predicted Return (%)'}
        )
        fig.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("🔍 Click 'Scan Stocks' to find investment opportunities")
        st.image("https://via.placeholder.com/800x400/0a0e17/00b4d8?text=Scan+for+Investment+Opportunities", use_column_width=True)

def show_stock_detail(symbol, services):
    """Display detailed view of selected stock"""
    
    with st.expander(f"📈 {symbol} - Detailed Analysis", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Price chart
            data = services['data'].get_historical_data(symbol, period="3mo")
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
                
                # Add moving averages
                for period, color in [(20, '#fdcb6e'), (50, '#6c5ce7')]:
                    ma = data['Close'].rolling(period).mean()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=ma,
                        name=f'SMA {period}',
                        line=dict(color=color, width=1)
                    ))
                
                fig.update_layout(
                    title=f"{symbol} - Price Chart",
                    template='plotly_dark',
                    height=400,
                    xaxis_rangeslider_visible=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Key metrics
            info = services['data'].get_company_info(symbol)
            indicators = services['stock'].calculate_indicators(symbol)
            ai_prediction = services['ai'].predict(symbol)
            
            st.markdown("#### 📊 Key Metrics")
            
            metrics = {
                "Price": f"${info.get('current_price', 0):.2f}",
                "Market Cap": f"${info.get('market_cap', 0)/1e9:.2f}B",
                "P/E Ratio": f"{info.get('pe_ratio', 0):.2f}",
                "Dividend Yield": f"{info.get('dividend_yield', 0):.2f}%",
                "RSI": f"{indicators.get('rsi', 0):.1f}",
                "AI Confidence": f"{ai_prediction.get('confidence', 0)*100:.1f}%",
                "Recommendation": f"{ai_prediction.get('recommendation', 'HOLD')}"
            }
            
            for key, value in metrics.items():
                color = '#00b894' if 'Buy' in value or 'STRONG BUY' in value or value == 'HOLD' else '#ff6b6b' if 'Sell' in value else '#888'
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span style="color: #888;">{key}</span>
                    <span style="color: {'#00b894' if 'Buy' in value or 'STRONG BUY' in value else '#ff6b6b' if 'Sell' in value else '#fdcb6e'}; font-weight: bold;">{value}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Add to watchlist button
            if st.button(f"⭐ Add {symbol} to Watchlist"):
                if symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(symbol)
                    st.success(f"✅ {symbol} added to watchlist")
                else:
                    st.info(f"ℹ️ {symbol} is already in watchlist")
