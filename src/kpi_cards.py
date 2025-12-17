"""
KPI Cards Module for NC Dashboard
Renders the Open NC Status Tracker with various visualizations

Author: Xander @ Calyx Containers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def render_open_nc_status_tracker(df: pd.DataFrame) -> None:
    """
    Render the Open NCs Status Tracker dashboard section.
    
    Displays:
    - KPI metric cards for each status
    - Status distribution bar chart
    - Status gauge charts
    - Priority breakdown within open NCs
    
    Args:
        df: Filtered NC DataFrame
    """
    st.markdown("## 📋 Current Open NCs Status Tracker")
    st.markdown("Real-time view of all non-conformance tickets by status")
    
    if df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Get status counts
    status_counts = df['Status'].value_counts()
    total_ncs = len(df)
    
    # Define status colors
    status_colors = {
        'Open': '#FF6B6B',
        'In Progress': '#4ECDC4',
        'Pending Review': '#FFE66D',
        'Closed': '#95E1D3',
        'On Hold': '#DDA0DD'
    }
    
    # Row 1: KPI Metric Cards
    st.markdown("### Status Overview")
    
    # Create columns for metrics
    cols = st.columns(len(status_counts) if len(status_counts) <= 5 else 5)
    
    for idx, (status, count) in enumerate(status_counts.items()):
        if idx < 5:  # Show top 5 statuses
            with cols[idx]:
                percentage = (count / total_ncs) * 100
                color = status_colors.get(status, '#888888')
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {color}22, {color}44);
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #333;">{count}</h3>
                    <p style="margin: 0; color: #666; font-size: 0.9rem;">{status}</p>
                    <p style="margin: 0; color: {color}; font-weight: bold;">{percentage:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Row 2: Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Status Distribution")
        
        # Bar chart
        fig_bar = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            color=status_counts.index,
            color_discrete_map=status_colors,
            labels={'x': 'Status', 'y': 'Count'},
            title=""
        )
        fig_bar.update_layout(
            showlegend=False,
            xaxis_title="Status",
            yaxis_title="Number of NCs",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_bar.update_traces(
            texttemplate='%{y}',
            textposition='outside'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.markdown("### Status Breakdown")
        
        # Pie/Donut chart
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4,
            color=status_counts.index,
            color_discrete_map=status_colors
        )
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Open NCs Deep Dive
    st.markdown("### 🔍 Open NCs Deep Dive")
    
    # Filter for open (non-closed) NCs
    open_statuses = ['Open', 'In Progress', 'Pending Review', 'On Hold']
    open_ncs = df[df['Status'].isin(open_statuses)]
    
    if not open_ncs.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Priority breakdown for open NCs
            priority_counts = open_ncs['Priority'].value_counts()
            
            priority_colors = {
                'High': '#FF4444',
                'Medium': '#FFAA00',
                'Low': '#44AA44'
            }
            
            fig_priority = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                color=priority_counts.index,
                color_discrete_map=priority_colors,
                title="Open NCs by Priority"
            )
            fig_priority.update_layout(
                showlegend=False,
                height=300,
                xaxis_title="Priority",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_priority, use_container_width=True)
        
        with col2:
            # External vs Internal breakdown
            ext_int_counts = open_ncs['External Or Internal'].value_counts()
            
            fig_ext_int = px.pie(
                values=ext_int_counts.values,
                names=ext_int_counts.index,
                title="External vs Internal",
                color_discrete_sequence=['#667eea', '#f093fb']
            )
            fig_ext_int.update_layout(height=300)
            st.plotly_chart(fig_ext_int, use_container_width=True)
        
        with col3:
            # Gauge for open NC percentage
            open_percentage = (len(open_ncs) / total_ncs) * 100
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=open_percentage,
                title={'text': "Open NC Rate"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#FF6B6B"},
                    'steps': [
                        {'range': [0, 30], 'color': '#95E1D3'},
                        {'range': [30, 60], 'color': '#FFE66D'},
                        {'range': [60, 100], 'color': '#FF6B6B'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Open NCs summary table
        st.markdown("### 📊 Open NCs Summary Table")
        
        summary_df = open_ncs.groupby(['Status', 'Priority']).agg({
            'NC Number': 'count',
            'Cost of Rework': 'sum',
            'Total Quantity Affected': 'sum'
        }).reset_index()
        summary_df.columns = ['Status', 'Priority', 'Count', 'Total Rework Cost', 'Total Qty Affected']
        summary_df['Total Rework Cost'] = summary_df['Total Rework Cost'].apply(lambda x: f"${x:,.2f}")
        summary_df['Total Qty Affected'] = summary_df['Total Qty Affected'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("🎉 No open NCs! All non-conformances have been resolved.")
    
    # Export option
    st.markdown("---")
    with st.expander("📥 Export Status Data"):
        export_df = df[['NC Number', 'Status', 'Priority', 'Customer', 
                       'Issue Type', 'Date Submitted', 'Cost of Rework']].copy()
        
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download Status Report (CSV)",
            data=csv,
            file_name="nc_status_report.csv",
            mime="text/csv"
        )
    
    # Row 5: Current Week Detailed View
    st.markdown("---")
    render_current_week_detail_view(df)


def render_current_week_detail_view(df: pd.DataFrame) -> None:
    """
    Render a detailed view of current week's NCs with all columns.
    
    Args:
        df: NC DataFrame
    """
    from datetime import datetime, timedelta
    
    st.markdown("## 📅 Current Week Detailed View")
    st.markdown("Full details of non-conformances from the current and recent weeks")
    
    if df.empty:
        st.warning("No data available.")
        return
    
    # Ensure Date Submitted is datetime
    df = df.copy()
    df['Date Submitted'] = pd.to_datetime(df['Date Submitted'], errors='coerce')
    
    # Calculate current week boundaries
    today = datetime.now()
    current_week_start = today - timedelta(days=today.weekday())  # Monday of current week
    current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Week selection
    st.markdown("### 🗓️ Week Selection")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        week_options = [
            "Current Week",
            "Last Week", 
            "Last 2 Weeks",
            "Last 4 Weeks",
            "Custom Range"
        ]
        selected_period = st.selectbox(
            "Select Time Period",
            options=week_options,
            index=0,
            key="week_detail_period"
        )
    
    # Calculate date range based on selection
    if selected_period == "Current Week":
        start_date = current_week_start
        end_date = today
    elif selected_period == "Last Week":
        start_date = current_week_start - timedelta(days=7)
        end_date = current_week_start - timedelta(seconds=1)
    elif selected_period == "Last 2 Weeks":
        start_date = current_week_start - timedelta(days=14)
        end_date = today
    elif selected_period == "Last 4 Weeks":
        start_date = current_week_start - timedelta(days=28)
        end_date = today
    else:  # Custom Range
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=current_week_start.date(),
                key="week_detail_start"
            )
            start_date = datetime.combine(start_date, datetime.min.time())
        with col3:
            end_date = st.date_input(
                "End Date",
                value=today.date(),
                key="week_detail_end"
            )
            end_date = datetime.combine(end_date, datetime.max.time())
    
    # Filter data for selected period
    df_valid = df.dropna(subset=['Date Submitted'])
    mask = (df_valid['Date Submitted'] >= start_date) & (df_valid['Date Submitted'] <= end_date)
    week_df = df_valid[mask].copy()
    
    # Display period info
    if selected_period != "Custom Range":
        col2.markdown(f"**From:** {start_date.strftime('%b %d, %Y')}")
        col3.markdown(f"**To:** {end_date.strftime('%b %d, %Y')}")
    
    st.markdown("---")
    
    if week_df.empty:
        st.info(f"No NCs found for {selected_period.lower()}.")
        return
    
    # Summary metrics for selected period
    st.markdown("### 📊 Period Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total NCs", len(week_df))
    
    with col2:
        open_count = len(week_df[week_df['Status'].isin(['Open', 'In Progress', 'Pending Review', 'On Hold'])])
        st.metric("Open NCs", open_count)
    
    with col3:
        if 'Cost of Rework' in week_df.columns:
            total_rework = week_df['Cost of Rework'].sum()
            st.metric("Total Rework Cost", f"${total_rework:,.2f}")
        else:
            st.metric("Total Rework Cost", "N/A")
    
    with col4:
        if 'Cost Avoided' in week_df.columns:
            total_avoided = week_df['Cost Avoided'].sum()
            st.metric("Total Cost Avoided", f"${total_avoided:,.2f}")
        else:
            st.metric("Total Cost Avoided", "N/A")
    
    with col5:
        if 'Total Quantity Affected' in week_df.columns:
            total_qty = week_df['Total Quantity Affected'].sum()
            st.metric("Total Qty Affected", f"{total_qty:,.0f}")
        else:
            st.metric("Total Qty Affected", "N/A")
    
    st.markdown("---")
    
    # Filters for the detailed view
    st.markdown("### 🔍 Filter Data")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        # Status filter
        status_options = ["All"] + sorted(week_df['Status'].dropna().unique().tolist())
        status_filter = st.selectbox(
            "Status",
            options=status_options,
            index=0,
            key="week_detail_status"
        )
    
    with filter_col2:
        # Priority filter
        priority_options = ["All"] + sorted(week_df['Priority'].dropna().unique().tolist())
        priority_filter = st.selectbox(
            "Priority",
            options=priority_options,
            index=0,
            key="week_detail_priority"
        )
    
    with filter_col3:
        # External/Internal filter
        ext_int_options = ["All"] + sorted(week_df['External Or Internal'].dropna().unique().tolist())
        ext_int_filter = st.selectbox(
            "External/Internal",
            options=ext_int_options,
            index=0,
            key="week_detail_ext_int"
        )
    
    with filter_col4:
        # Customer filter
        customer_options = ["All"] + sorted(week_df['Customer'].dropna().unique().tolist())
        customer_filter = st.selectbox(
            "Customer",
            options=customer_options,
            index=0,
            key="week_detail_customer"
        )
    
    # Apply filters
    filtered_df = week_df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    
    if ext_int_filter != "All":
        filtered_df = filtered_df[filtered_df['External Or Internal'] == ext_int_filter]
    
    if customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Customer'] == customer_filter]
    
    # Search box
    search_term = st.text_input(
        "🔎 Search (NC Number, Customer, Defect Summary, etc.)",
        "",
        key="week_detail_search"
    )
    
    if search_term:
        search_mask = filtered_df.astype(str).apply(
            lambda row: row.str.contains(search_term, case=False, na=False).any(), 
            axis=1
        )
        filtered_df = filtered_df[search_mask]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(week_df)} records**")
    
    st.markdown("---")
    
    # Column selection
    st.markdown("### 📋 Detailed Data View")
    
    all_columns = filtered_df.columns.tolist()
    
    # Default columns to show
    default_columns = [
        'NC Number', 'Date Submitted', 'Status', 'Priority', 'External Or Internal',
        'Customer', 'Issue Type', 'Defect Summary', 'Employee Responsible',
        'Cost of Rework', 'Cost Avoided', 'Total Quantity Affected'
    ]
    default_columns = [col for col in default_columns if col in all_columns]
    
    with st.expander("⚙️ Configure Columns", expanded=False):
        selected_columns = st.multiselect(
            "Select columns to display",
            options=all_columns,
            default=default_columns,
            key="week_detail_columns"
        )
        
        # Quick selection buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Select All Columns", key="select_all_cols"):
                selected_columns = all_columns
        with col2:
            if st.button("Reset to Default", key="reset_cols"):
                selected_columns = default_columns
        with col3:
            if st.button("Clear All", key="clear_cols"):
                selected_columns = ['NC Number']
    
    if not selected_columns:
        selected_columns = ['NC Number']
    
    # Prepare display dataframe
    display_df = filtered_df[selected_columns].copy()
    
    # Format date columns for display
    for col in display_df.columns:
        if 'date' in col.lower() or 'submitted' in col.lower():
            if display_df[col].dtype == 'datetime64[ns]':
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M')
    
    # Display the dataframe with full interactivity
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    
    # Export filtered data
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export visible columns
        csv_visible = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Visible Columns (CSV)",
            data=csv_visible,
            file_name=f"nc_detail_{selected_period.lower().replace(' ', '_')}_visible.csv",
            mime="text/csv",
            key="download_visible"
        )
    
    with col2:
        # Export all columns
        csv_all = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Columns (CSV)",
            data=csv_all,
            file_name=f"nc_detail_{selected_period.lower().replace(' ', '_')}_all.csv",
            mime="text/csv",
            key="download_all"
        )


def render_status_kpi_card(
    status: str, 
    count: int, 
    total: int, 
    color: str
) -> None:
    """
    Render a single status KPI card.
    
    Args:
        status: Status name
        count: Number of NCs with this status
        total: Total number of NCs
        color: Color for the card
    """
    percentage = (count / total) * 100 if total > 0 else 0
    
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid {color};">
        <h2 style="margin: 0; color: {color};">{count}</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem;">{status}</p>
        <p style="margin: 0; color: #888; font-size: 0.8rem;">{percentage:.1f}% of total</p>
    </div>
    """, unsafe_allow_html=True)
