#!/usr/bin/env python
# coding: utf-8

# In[11]:


import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Load and clean data ---
@st.cache_data
def load_data():
    df = pd.read_excel("your_data_file.xlsx",2)  # Replace with your Excel file
    df['OBS_DATE'] = pd.to_datetime(df['OBS_DATE'], errors='coerce')
    df['ITEM'] = df['ITEM'].astype(str)
    df['CURRENCY'] = df['CURRENCY'].astype(str)
    df['RESIDUAL_MATURITY'] = df['RESIDUAL_MATURITY'].astype(str)
    df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
    return df.dropna(subset=['OBS_DATE', 'ITEM', 'CURRENCY', 'RESIDUAL_MATURITY', 'AMOUNT'])

df = load_data()
date_options = sorted(df['OBS_DATE'].dt.date.unique())  # Needed for both modes

st.title("📊 Data Dissemination Platform")

# --- Sidebar: Filtering ---
st.sidebar.header("Filter Options")

# Time-series mode toggle
time_series_mode = st.sidebar.checkbox("Enable Time-Series Mode (multiple dates)", value=False)

if time_series_mode:
    selected_dates = st.sidebar.multiselect("Select Dates", options=date_options)
else:
    selected_date = st.sidebar.selectbox(
        "Select Observation Date", 
        options=[""] + date_options, 
        format_func=lambda x: x if x != "" else "Select a date"
    )

selected_item = st.sidebar.multiselect("Select Item", options=sorted(df['ITEM'].unique()))
selected_currency = st.sidebar.multiselect("Select Currency", options=sorted(df['CURRENCY'].unique()))
selected_maturity = st.sidebar.multiselect("Select Residual Maturity", options=sorted(df['RESIDUAL_MATURITY'].unique()))

chart_options = ["", "Bar", "Column", "Line", "Pie"]
selected_chart_type = st.sidebar.selectbox("Select Chart Type", options=chart_options)

# --- Apply filters ---
filtered_df = df.copy()

if time_series_mode and selected_dates:
    filtered_df = filtered_df[filtered_df['OBS_DATE'].dt.date.isin(selected_dates)]
elif not time_series_mode and selected_date != "":
    filtered_df = filtered_df[filtered_df['OBS_DATE'].dt.date == selected_date]
else:
    filtered_df = pd.DataFrame()  # Empty until selection

# Apply other filters
if not filtered_df.empty:
    if selected_item:
        filtered_df = filtered_df[filtered_df['ITEM'].isin(selected_item)]
    if selected_currency:
        filtered_df = filtered_df[filtered_df['CURRENCY'].isin(selected_currency)]
    if selected_maturity:
        filtered_df = filtered_df[filtered_df['RESIDUAL_MATURITY'].isin(selected_maturity)]

# --- Display Data Table ---
if not filtered_df.empty:
    st.subheader("📄 Filtered Results")
    st.dataframe(filtered_df[['CURRENCY', 'ITEM', 'OBS_DATE', 'RESIDUAL_MATURITY', 'AMOUNT']].reset_index(drop=True))
    st.markdown(f"### ✅ Total Records: {len(filtered_df)}")

    # Add label column for grouping
    filtered_df['LABEL'] = (
        filtered_df['ITEM'] + " | " +
        filtered_df['CURRENCY'] + " | " +
        filtered_df['RESIDUAL_MATURITY']
    )

    # --- Chart Display ---
    if selected_chart_type != "":
        st.subheader("📈 Amount Visualization")

        if time_series_mode and selected_chart_type == "Line":
            ts_data = filtered_df.groupby(['OBS_DATE', 'LABEL'])['AMOUNT'].sum().reset_index()
            fig = px.line(ts_data, x='OBS_DATE', y='AMOUNT', color='LABEL', markers=True, title="Time Series")
        else:
            chart_data = filtered_df.groupby('LABEL')['AMOUNT'].sum().reset_index()
            if selected_chart_type == "Bar":
                fig = px.bar(chart_data, x='LABEL', y='AMOUNT', text_auto='.2s', title="Bar Chart")
                fig.update_layout(xaxis_tickangle=-45)
            elif selected_chart_type == "Column":
                fig = px.bar(chart_data, x='AMOUNT', y='LABEL', orientation='h', text_auto='.2s', title="Column Chart")
            elif selected_chart_type == "Line":
                fig = px.line(chart_data, x='LABEL', y='AMOUNT', markers=True, title="Line Chart")
                fig.update_layout(xaxis_tickangle=-45)
            elif selected_chart_type == "Pie":
                fig = px.pie(chart_data, names='LABEL', values='AMOUNT', title="Pie Chart")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select a chart type to visualize the data.")
else:
    st.info("Please select a date to begin filtering.")

# --- Download Section ---
if not filtered_df.empty:
    st.markdown("### ⬇️ Download Filtered Data")

    col1, col2 = st.columns(2)

    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv'
        )

    with col2:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            filtered_df.to_excel(tmp.name, index=False)
            tmp.seek(0)
            st.download_button(
                label="Download as Excel",
                data=tmp.read(),
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




