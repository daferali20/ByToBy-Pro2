import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container

def show_portfolio(services):
    """Display portfolio management page"""
    
    colored_header(
        label="💼 Portfolio Management",
        description="Track and manage your investment portfolio",
        color_name="blue-70"
    )
    
    portfolio = services['portfolio'].get_portfolio()
    
    # Portfolio summary
    col1, col2, col3, col4 = st.columns(4)
    
    total_value = services['portfolio'].get_total_value()
    daily_change = services['portfolio'].get_daily_change()
    allocation = services['portfolio'].get_allocation()
    
    with col1:
        st.metric(
            label="Total Value",
            value=f"${total_value:,.2f}",
            delta=f"{daily_change:.2f}%",
            delta_color="normal"
        )
    
    with col2:
        # Number of holdings
        num_holdings = len(portfolio.get('holdings', {}))
        st.metric(
            label="Holdings",
            value=num_holdings
        )
    
    with col3:
        # Cash
        cash = portfolio.get('cash', 0)
        st.metric(
            label="Cash",
            value=f"${cash:,.2f}",
            delta=f"{cash/total_value*100:.1f}% of portfolio" if total_value > 0 else "0%"
        )
    
    with col4:
        # Best performer
        best_performer = get_best_performer(services, portfolio)
        if best_performer:
            st.metric(
                label="Best Performer",
                value=best_performer['symbol'],
                delta=f"{best_performer['change']:.2f}%"
            )
    
    style_metric_cards()
    
    st.markdown("---")
    
    # Portfolio charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Allocation")
        if allocation:
            fig = go.Figure(data=[go.Pie(
                labels=list(allocation.keys()),
                values=list(allocation.values()),
                hole=0.6,
                marker=dict(colors=['#00b4d8', '#0077b6', '#00b894', '#fdcb6e', '#6c5ce7', '#ff6b6b'])
            )])
            fig.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Performance")
        performance_data = services['portfolio'].get_performance_data("3mo")
        if not performance_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=performance_data['date'],
                y=performance_data['value'],
                mode='lines',
                name='Portfolio',
                line=dict(color='#00b4d8', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 180, 216, 0.1)'
            ))
            fig.update_layout(
                template='plotly_dark',
                height=400,
                xaxis_title="Date",
                yaxis_title="Value ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Holdings table
    st.markdown("### 📋 Holdings")
    
    holdings = portfolio.get('holdings', {})
    if holdings:
        data = []
        for symbol, holding in holdings.items():
            price = services['stock'].get_current_price(symbol)
            if price:
                value = price * holding['shares']
                cost = holding['avg_price'] * holding['shares']
                profit = value - cost
                profit_pct = (profit / cost) * 100 if cost > 0 else 0
                
                info = services['stock'].get_company_info(symbol)
                
                data.append({
                    'Symbol': symbol,
                    'Name': info.get('name', symbol),
                    'Shares': holding['shares'],
                    'Avg Price': f"${holding['avg_price']:.2f}",
                    'Current Price': f"${price:.2f}",
                    'Value': f"${value:,.2f}",
                    'Profit/Loss': f"${profit:,.2f}",
                    'Return %': f"{profit_pct:.1f}%"
                })
        
        df = pd.DataFrame(data)
        
        # Color coding for returns
        def color_return(val):
            if 'Return' in df.columns:
                return val
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                "Shares": st.column_config.NumberColumn("Shares", format="%.0f"),
                "Value": st.column_config.TextColumn("Value"),
                "Profit/Loss": st.column_config.TextColumn("Profit/Loss"),
                "Return %": st.column_config.TextColumn("Return %"),
            }
        )
        
        # Add/Remove holdings
        st.markdown("---")
        st.markdown("### ✏️ Manage Holdings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with stylable_container(
                key="add_holding",
                css_styles="""
                {
                    background-color: rgba(20, 27, 45, 0.6);
                    border-radius: 10px;
                    padding: 20px;
                }
                """
            ):
                st.markdown("#### Add Holding")
                add_symbol = st.text_input("Symbol", key="add_symbol")
                add_shares = st.number_input("Shares", min_value=0.01, step=0.01, key="add_shares")
                add_price = st.number_input("Purchase Price", min_value=0.01, step=0.01, key="add_price")
                
                if st.button("➕ Add to Portfolio"):
                    if add_symbol and add_shares and add_price:
                        if services['portfolio'].add_holding(add_symbol.upper(), add_shares, add_price):
                            st.success(f"✅ Added {add_shares} shares of {add_symbol.upper()}")
                            st.rerun()
                        else:
                            st.error("❌ Error adding holding")
        
        with col2:
            with stylable_container(
                key="remove_holding",
                css_styles="""
                {
                    background-color: rgba(20, 27, 45, 0.6);
                    border-radius: 10px;
                    padding: 20px;
                }
                """
            ):
                st.markdown("#### Remove Holding")
                remove_symbol = st.selectbox(
                    "Select Symbol",
                    options=list(holdings.keys()),
                    key="remove_symbol"
                )
                
                if remove_symbol:
                    max_shares = holdings[remove_symbol]['shares']
                    remove_shares = st.number_input(
                        "Shares to Remove",
                        min_value=0.01,
                        max_value=float(max_shares),
                        step=0.01,
                        key="remove_shares"
                    )
                    
                    if st.button("➖ Remove from Portfolio"):
                        if remove_symbol and remove_shares:
                            if services['portfolio'].remove_holding(remove_symbol, remove_shares):
                                st.success(f"✅ Removed {remove_shares} shares of {remove_symbol}")
                                st.rerun()
                            else:
                                st.error("❌ Error removing holding")
    
    else:
        st.info("ℹ️ No holdings in portfolio. Add your first holding above.")

def get_best_performer(services, portfolio) -> dict:
    """Get the best performing stock in portfolio"""
    try:
        holdings = portfolio.get('holdings', {})
        best = None
        best_return = -float('inf')
        
        for symbol, holding in holdings.items():
            price = services['stock'].get_current_price(symbol)
            if price and holding['avg_price'] > 0:
                ret = ((price - holding['avg_price']) / holding['avg_price']) * 100
                if ret > best_return:
                    best_return = ret
                    best = {'symbol': symbol, 'change': ret}
        
        return best
    except:
        return None
