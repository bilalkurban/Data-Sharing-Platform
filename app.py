#!/usr/bin/env python
# coding: utf-8

# In[7]:


#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from io import BytesIO
import base64
import uuid
import datetime

# --- Session State for API Keys and Configuration ---
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}

# --- Default configuration ---
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "https://yourdomain.com/api/data"

# --- Load and clean data ---
@st.cache_data
def load_data():
    df = pd.read_excel("your_data_file.xlsx", 2)  # Replace with your Excel file
    df['OBS_DATE'] = pd.to_datetime(df['OBS_DATE'], errors='coerce')
    df['ITEM'] = df['ITEM'].astype(str)
    df['CURRENCY'] = df['CURRENCY'].astype(str)
    df['RESIDUAL_MATURITY'] = df['RESIDUAL_MATURITY'].astype(str)
    df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
    return df.dropna(subset=['OBS_DATE', 'ITEM', 'CURRENCY', 'RESIDUAL_MATURITY', 'AMOUNT'])

df = load_data()
date_options = sorted(df['OBS_DATE'].dt.date.unique())  # Needed for both modes

st.title("📊 Data Dissemination Platform")

# --- API Key Management ---
def generate_api_key():
    """Generate a unique API key"""
    new_key = str(uuid.uuid4())
    st.session_state.api_keys[new_key] = {
        "created_at": datetime.datetime.now(),
        "last_used": None,
        "call_count": 0
    }
    return new_key

# --- Sidebar: Main Navigation ---
app_mode = st.sidebar.radio("Mode", ["Data Explorer", "API Management"])

if app_mode == "Data Explorer":
    # --- Original data filtering and visualization functionality ---
    st.sidebar.header("Filter Options")

    # Time-series mode toggle
    time_series_mode = st.sidebar.checkbox("Enable Time-Series Mode (multiple dates)", value=False)

    if time_series_mode:
        selected_dates = st.sidebar.multiselect("Select Dates", options=date_options)
    else:
        # Clean and convert date options
        date_options = sorted([
            d.to_pydatetime().date() if hasattr(d, 'to_pydatetime') else d
            for d in df['OBS_DATE'].dropna().unique()
            if isinstance(d, (datetime.date, datetime.datetime, pd.Timestamp))
        ])
        # Guard clause
        if not date_options:
            st.sidebar.warning("No valid dates found in the dataset.")
            st.stop()
        # Use None as the placeholder instead of ""
        selected_date = st.sidebar.selectbox(
            "Select Observation Date",
            options=[None] + date_options,
            format_func=lambda x: x.strftime("%Y-%m-%d") if isinstance(x, datetime.date) else "Select a date"
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

        # --- Download & API Section ---
        if not filtered_df.empty:
            st.markdown("### ⬇️ Download or Access Data")
            
            tab1, tab2 = st.tabs(["Download Data", "API Access"])
            
            with tab1:
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
            
            with tab2:
                st.subheader("Access this data via API")
                
                # Create query parameters from current filters
                params = {}
                
                if time_series_mode and selected_dates:
                    params['dates'] = ",".join([d.strftime("%Y-%m-%d") for d in selected_dates])
                elif not time_series_mode and selected_date != "":
                    params['date'] = selected_date.strftime("%Y-%m-%d") if selected_date else ""
                
                if selected_item:
                    params['items'] = ",".join(selected_item)
                if selected_currency:
                    params['currencies'] = ",".join(selected_currency)
                if selected_maturity:
                    params['maturities'] = ",".join(selected_maturity)
                
                # Build example API URL using the configured base URL
                base_url = st.session_state.api_base_url
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                example_url = f"{base_url}?{param_str}"
                
                st.code(example_url, language="text")
                
                st.markdown("""
                #### API Documentation
                
                To access this data programmatically, you'll need an API key. Go to the API Management tab to generate one.
                
                **Example Request:**
                ```python
                import requests
                
                url = "EXAMPLE_URL_ABOVE"
                headers = {
                    "x-api-key": "YOUR_API_KEY"
                }
                
                response = requests.get(url, headers=headers)
                data = response.json()
                ```
                """)
    else:
        st.info("Please select a date to begin filtering.")

elif app_mode == "API Management":
    st.header("API Management")
    
    # API Configuration
    st.subheader("API Configuration")
    
    api_base_url = st.text_input(
        "API Base URL", 
        value=st.session_state.api_base_url,
        help="The base URL where your API will be hosted"
    )
    
    if st.button("Save Configuration"):
        st.session_state.api_base_url = api_base_url
        st.success("Configuration saved!")
    
    # API Key Generation Section
    st.subheader("Generate API Key")
    
    if st.button("Generate New API Key"):
        new_key = generate_api_key()
        st.success("New API key generated!")
        st.code(new_key)
        st.warning("Save this key securely. It won't be shown again!")
    
    # View existing API keys
    st.subheader("Your API Keys")
    
    if not st.session_state.api_keys:
        st.info("No API keys have been generated yet.")
    else:
        key_data = []
        for key, data in st.session_state.api_keys.items():
            masked_key = f"{key[:8]}...{key[-4:]}"
            created_time = data['created_at']
            last_used = data['last_used'] if data['last_used'] else "Never"
            
            # Format timestamps properly
            if isinstance(created_time, pd.Timestamp):
                created_str = created_time.strftime("%Y-%m-%d %H:%M")
            else:
                created_str = created_time.strftime("%Y-%m-%d %H:%M") if hasattr(created_time, 'strftime') else str(created_time)
                
            if isinstance(last_used, str):
                last_used_str = last_used
            else:
                last_used_str = last_used.strftime("%Y-%m-%d %H:%M") if hasattr(last_used, 'strftime') else str(last_used)
                
            key_data.append({
                "Key": masked_key,
                "Created": created_str,
                "Last Used": last_used_str,
                "Usage Count": data['call_count']
            })
        
        st.table(pd.DataFrame(key_data))
    
    # API Documentation
    st.subheader("API Documentation")
    
    st.markdown("""
    ### Endpoints
    
    #### `GET /api/data`
    
    Returns data based on your filter criteria.
    
    **Query Parameters:**
    
    - `date` - Single date in YYYY-MM-DD format
    - `dates` - Multiple dates, comma-separated (YYYY-MM-DD,YYYY-MM-DD)
    - `items` - Filter by items, comma-separated
    - `currencies` - Filter by currencies, comma-separated
    - `maturities` - Filter by residual maturities, comma-separated
    - `format` - Response format: json (default), csv, or excel
    
    **Headers:**
    
    - `x-api-key` - Your API key (required)
    
    **Example Request:**
    ```
    GET /api/data?date=2023-01-15&currencies=USD,EUR&format=json
    ```
    
    **Response:**
    ```json
    {
      "data": [
        {
          "CURRENCY": "USD",
          "ITEM": "Example Item",
          "OBS_DATE": "2023-01-15T00:00:00Z",
          "RESIDUAL_MATURITY": "1Y",
          "AMOUNT": 12345.67
        },
        ...
      ],
      "count": 42,
      "timestamp": "2023-06-10T12:34:56Z"
    }
    ```
    """)
    
    # Server implementation instructions 
    with st.expander("Server Implementation Guide"):
        st.markdown("""
        ### Implementing the API Server
        
        To expose this data through an API, you'll need to implement a server component. Here's how to implement this with FastAPI in Python:
        
        ```python
        from fastapi import FastAPI, Header, HTTPException, Query
        from fastapi.responses import JSONResponse, StreamingResponse
        import pandas as pd
        from typing import List, Optional
        import io
        
        app = FastAPI()
        
        # This would be stored in a database in production
        API_KEYS = {
            # Keys generated from the Streamlit app
        }
        
        @app.get("/api/data")
        async def get_data(
            x_api_key: str = Header(None),
            date: Optional[str] = None,
            dates: Optional[str] = None,
            items: Optional[str] = None,
            currencies: Optional[str] = None,
            maturities: Optional[str] = None,
            format: str = "json"
        ):
            # Validate API key
            if x_api_key not in API_KEYS:
                raise HTTPException(status_code=401, detail="Invalid API key")
                
            # Update API key usage statistics
            # In production, this would update a database
            
            # Load the same data source as your Streamlit app
            df = pd.read_excel("your_data_file.xlsx", 2)
            
            # Apply the same cleaning
            df['OBS_DATE'] = pd.to_datetime(df['OBS_DATE'], errors='coerce')
            df['ITEM'] = df['ITEM'].astype(str)
            df['CURRENCY'] = df['CURRENCY'].astype(str)
            df['RESIDUAL_MATURITY'] = df['RESIDUAL_MATURITY'].astype(str)
            df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce')
            df = df.dropna(subset=['OBS_DATE', 'ITEM', 'CURRENCY', 'RESIDUAL_MATURITY', 'AMOUNT'])
            
            # Apply filters
            if date:
                df = df[df['OBS_DATE'].dt.date == pd.to_datetime(date).date()]
            
            if dates:
                date_list = [pd.to_datetime(d).date() for d in dates.split(",")]
                df = df[df['OBS_DATE'].dt.date.isin(date_list)]
                
            if items:
                item_list = items.split(",")
                df = df[df['ITEM'].isin(item_list)]
                
            if currencies:
                currency_list = currencies.split(",")
                df = df[df['CURRENCY'].isin(currency_list)]
                
            if maturities:
                maturity_list = maturities.split(",")
                df = df[df['RESIDUAL_MATURITY'].isin(maturity_list)]
            
            # Return requested format
            if format.lower() == "csv":
                output = io.StringIO()
                df.to_csv(output, index=False)
                return StreamingResponse(
                    io.BytesIO(output.getvalue().encode()),
                    media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=data.csv"}
                )
            elif format.lower() == "excel":
                output = io.BytesIO()
                df.to_excel(output, index=False)
                return StreamingResponse(
                    output,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=data.xlsx"}
                )
            else:  # json is default
                return {
                    "data": df.to_dict(orient="records"),
                    "count": len(df),
                    "timestamp": pd.Timestamp.now().isoformat()
                }
        
        # Run with: uvicorn api_server:app --reload
        ```
        """)

# If you want to handle API requests directly in this Streamlit app (simulated API endpoint)
# Note: This is not a real API but can demonstrate the functionality
if "api_request" in st.query_params:
    # This section simulates an API response based on URL parameters
    # In a real implementation, this would be handled by a separate API server
    
    # Don't show the UI for API requests
    st.set_page_config(initial_sidebar_state="collapsed")
    
    # Parse API key from headers (this doesn't actually work in Streamlit)
    # In a real API implementation, you would validate the API key
    
    # Parse parameters
    params = st.query_params
    format_param = params.get("format", "json")
    
    # Apply filters similar to the main app
    filtered_api_df = df.copy()
    
    # Apply date filter
    if "date" in params:
        try:
            date_param = pd.to_datetime(params["date"]).date()
            filtered_api_df = filtered_api_df[filtered_api_df['OBS_DATE'].dt.date == date_param]
        except:
            pass
    
    if "dates" in params:
        try:
            date_list = [pd.to_datetime(d).date() for d in params["dates"].split(",")]
            filtered_api_df = filtered_api_df[filtered_api_df['OBS_DATE'].dt.date.isin(date_list)]
        except:
            pass
    
    # Apply other filters
    if "items" in params:
        item_list = params["items"].split(",")
        filtered_api_df = filtered_api_df[filtered_api_df['ITEM'].isin(item_list)]
    
    if "currencies" in params:
        currency_list = params["currencies"].split(",")
        filtered_api_df = filtered_api_df[filtered_api_df['CURRENCY'].isin(currency_list)]
    
    if "maturities" in params:
        maturity_list = params["maturities"].split(",")
        filtered_api_df = filtered_api_df[filtered_api_df['RESIDUAL_MATURITY'].isin(maturity_list)]
    
    # Return data in requested format
    if format_param == "csv":
        csv = filtered_api_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "data.csv", "text/csv")
    elif format_param == "excel":
        excel_buffer = BytesIO()
        filtered_api_df.to_excel(excel_buffer, index=False)
        excel_data = excel_buffer.getvalue()
        st.download_button("Download Excel", excel_data, "data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:  # json is default
        st.json({
            "data": filtered_api_df.to_dict(orient="records"),
            "count": len(filtered_api_df),
            "timestamp": pd.Timestamp.now().isoformat()
        })


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




