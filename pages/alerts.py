import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container

def show_alerts(services):
    """Display alerts and notifications page"""
    
    colored_header(
        label="🔔 Alerts & Notifications",
        description="Set up and manage your stock alerts",
        color_name="blue-70"
    )
    
    # Create new alert
    with stylable_container(
        key="create_alert",
        css_styles="""
        {
            background-color: rgba(20, 27, 45, 0.6);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        """
    ):
        st.markdown("### ➕ Create New Alert")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            alert_symbol = st.text_input("Stock Symbol", placeholder="e.g., AAPL")
        
        with col2:
            alert_type = st.selectbox(
                "Alert Type",
                ["Price Above", "Price Below", "Volume Spike", "RSI Overbought", "RSI Oversold", "News Alert"]
            )
        
        with col3:
            alert_value = st.number_input(
                "Trigger Value",
                min_value=0.0,
                step=0.01,
                placeholder="Enter trigger value"
            )
        
        col4, col5, col6 = st.columns([2, 2, 1])
        
        with col4:
            alert_frequency = st.selectbox(
                "Frequency",
                ["Once", "Hourly", "Daily", "Weekly"]
            )
        
        with col5:
            alert_channel = st.selectbox(
                "Channel",
                ["In-App", "Email", "Both"]
            )
        
        with col6:
            if st.button("🔔 Create Alert", use_container_width=True):
                if alert_symbol and alert_value:
                    # Add alert to session state
                    new_alert = {
                        'symbol': alert_symbol.upper(),
                        'type': alert_type,
                        'value': alert_value,
                        'frequency': alert_frequency,
                        'channel': alert_channel,
                        'created_at': datetime.now(),
                        'status': 'Active',
                        'id': len(st.session_state.alerts) + 1
                    }
                    st.session_state.alerts.append(new_alert)
                    st.success(f"✅ Alert created for {alert_symbol.upper()}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all fields")
    
    # Active alerts
    st.markdown("### 📋 Active Alerts")
    
    if st.session_state.alerts:
        # Filter alerts
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Active", "Triggered", "Paused"]
            )
        with col2:
            filter_symbol = st.text_input("Filter by Symbol", placeholder="Symbol")
        
        # Display alerts
        alerts_df = pd.DataFrame(st.session_state.alerts)
        
        if filter_status != "All":
            alerts_df = alerts_df[alerts_df['status'] == filter_status]
        
        if filter_symbol:
            alerts_df = alerts_df[alerts_df['symbol'].str.contains(filter_symbol.upper())]
        
        if not alerts_df.empty:
            # Format dataframe
            display_df = alerts_df.copy()
            display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Add action buttons
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "symbol": st.column_config.TextColumn("Symbol", width="small"),
                    "type": st.column_config.TextColumn("Type"),
                    "value": st.column_config.NumberColumn("Value", format="%.2f"),
                    "frequency": st.column_config.TextColumn("Frequency", width="small"),
                    "channel": st.column_config.TextColumn("Channel", width="small"),
                    "status": st.column_config.TextColumn("Status", width="small"),
                }
            )
            
            # Alert actions
            st.markdown("### 🔧 Alert Actions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                alert_to_edit = st.selectbox(
                    "Select Alert",
                    options=[f"{a['id']} - {a['symbol']}" for a in st.session_state.alerts],
                    key="alert_select"
                )
            
            if alert_to_edit:
                alert_id = int(alert_to_edit.split(' - ')[0])
                with col2:
                    if st.button("⏸️ Pause Alert"):
                        for alert in st.session_state.alerts:
                            if alert['id'] == alert_id:
                                alert['status'] = 'Paused'
                                st.success("✅ Alert paused")
                                st.rerun()
                                break
                
                with col3:
                    if st.button("🗑️ Delete Alert"):
                        st.session_state.alerts = [
                            a for a in st.session_state.alerts if a['id'] != alert_id
                        ]
                        st.success("✅ Alert deleted")
                        st.rerun()
        else:
            st.info("ℹ️ No alerts found matching your filters")
    else:
        st.info("ℹ️ No alerts configured yet. Create your first alert above!")
    
    # Alert history
    st.markdown("---")
    st.markdown("### 📜 Alert History")
    
    # Sample historical alerts
    history_data = [
        {'symbol': 'AAPL', 'type': 'Price Above', 'triggered': 'Yesterday', 'status': 'Triggered'},
        {'symbol': 'GOOGL', 'type': 'RSI Oversold', 'triggered': '2 days ago', 'status': 'Triggered'},
        {'symbol': 'TSLA', 'type': 'Volume Spike', 'triggered': '3 days ago', 'status': 'Triggered'},
    ]
    
    if history_data:
        df_history = pd.DataFrame(history_data)
        st.dataframe(
            df_history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("ℹ️ No alert history")
