#!/usr/bin/env python
# coding: utf-8

# In[26]:


import streamlit as st
import pandas as pd
import plotly.express as px

# Load and clean the data
@st.cache_data
def load_data():
    df = pd.read_excel("your_data_file.xlsx",2)  # Replace with your Excel file path

    # Ensure correct types
    df['OBS_DATE'] = pd.to_datetime(df['OBS_DATE'], errors='coerce')
    df['ITEM'] = df['ITEM'].astype(str)
    df['CURRENCY'] = df['CURRENCY'].astype(str)
    df['RESIDUAL_MATURITY'] = df['RESIDUAL_MATURITY'].astype(str)
    df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')

    # Drop rows with missing required values
    df = df.dropna(subset=['OBS_DATE', 'ITEM', 'CURRENCY', 'RESIDUAL_MATURITY', 'AMOUNT'])

    return df

# Load data
df = load_data()

st.title("📊 Data Dissemination Platform")

# Sidebar filters
st.sidebar.header("Filter Options")

date_options = sorted(df['OBS_DATE'].dt.date.unique())
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

# Filtering logic
if selected_date != "":
    filtered_df = df[df['OBS_DATE'].dt.date == selected_date]

    if selected_item:
        filtered_df = filtered_df[filtered_df['ITEM'].isin(selected_item)]

    if selected_currency:
        filtered_df = filtered_df[filtered_df['CURRENCY'].isin(selected_currency)]

    if selected_maturity:
        filtered_df = filtered_df[filtered_df['RESIDUAL_MATURITY'].isin(selected_maturity)]

    if not filtered_df.empty:
        st.subheader("📄 Filtered Results")
        st.dataframe(
            filtered_df[['CURRENCY', 'ITEM', 'OBS_DATE', 'RESIDUAL_MATURITY', 'AMOUNT']].reset_index(drop=True),
            use_container_width=True
        )
        st.markdown(f"### ✅ Total Records: {len(filtered_df)}")

        # Show chart only if type is selected
        if selected_chart_type != "":
            st.subheader("📈 Amount Visualization")

            # Create LABEL
            filtered_df['LABEL'] = (
                filtered_df['ITEM'] + " | " +
                filtered_df['CURRENCY'] + " | " +
                filtered_df['RESIDUAL_MATURITY']
            )

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
        st.warning("No data available for the selected filters.")
else:
    st.info("Please select an observation date to begin.")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




