def render_current_week_detail_view(df: pd.DataFrame) -> None:
    """
    Render a detailed table view of current week's NCs showing ALL columns.
    """
    from datetime import datetime, timedelta
    
    st.markdown("## 📅 Current Week - Full Detail View")
    st.markdown("Complete data table with **all columns** from the source data")
    
    if df.empty:
        st.warning("No data available.")
        return
    
    # Ensure Date Submitted is datetime
    df = df.copy()
    df['Date Submitted'] = pd.to_datetime(df['Date Submitted'], errors='coerce')
    
    # Calculate current week boundaries
    today = datetime.now()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_start = current_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Week selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        week_options = ["Current Week", "Last Week", "Last 2 Weeks", "Last 4 Weeks", "All Data"]
        selected_period = st.selectbox("📆 Select Time Period", options=week_options, index=0, key="week_detail_period")
    
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
    else:  # All Data
        start_date = df['Date Submitted'].min()
        end_date = today
    
    with col2:
        st.markdown(f"**From:** {start_date.strftime('%b %d, %Y') if pd.notna(start_date) else 'N/A'}")
    with col3:
        st.markdown(f"**To:** {end_date.strftime('%b %d, %Y') if pd.notna(end_date) else 'N/A'}")
    
    # Filter data for selected period
    df_valid = df.dropna(subset=['Date Submitted'])
    
    if selected_period != "All Data":
        mask = (df_valid['Date Submitted'] >= start_date) & (df_valid['Date Submitted'] <= end_date)
        filtered_df = df_valid[mask].copy()
    else:
        filtered_df = df_valid.copy()
    
    if filtered_df.empty:
        st.info(f"No NCs found for {selected_period.lower()}.")
        return
    
    # Quick summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Records", len(filtered_df))
    with col2:
        open_count = len(filtered_df[filtered_df['Status'].isin(['Open', 'In Progress', 'Pending Review', 'On Hold'])])
        st.metric("🔴 Open NCs", open_count)
    with col3:
        if 'Cost of Rework' in filtered_df.columns:
            st.metric("💰 Rework Cost", f"${filtered_df['Cost of Rework'].sum():,.2f}")
    with col4:
        if 'Cost Avoided' in filtered_df.columns:
            st.metric("✅ Cost Avoided", f"${filtered_df['Cost Avoided'].sum():,.2f}")
    
    st.markdown("---")
    
    # Show ALL columns in table
    st.markdown("### 📋 Complete Data Table (All Columns)")
    st.markdown(f"**{len(filtered_df.columns)} columns available** | Scroll horizontally to see all data")
    
    # List all columns
    with st.expander("📑 View Column List"):
        col_list = ", ".join(filtered_df.columns.tolist())
        st.markdown(f"**Columns:** {col_list}")
    
    # Prepare display dataframe with ALL columns
    display_df = filtered_df.copy()
    
    # Format date columns
    for col in display_df.columns:
        if display_df[col].dtype == 'datetime64[ns]':
            display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
    
    # Display FULL dataframe with ALL columns
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )
    
    # Export
    st.markdown("---")
    st.markdown("### 📥 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Full Data (CSV)",
            data=csv_data,
            file_name=f"nc_full_data_{selected_period.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        st.markdown(f"**{len(filtered_df)} records** with **{len(filtered_df.columns)} columns**")
