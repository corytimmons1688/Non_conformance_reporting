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
