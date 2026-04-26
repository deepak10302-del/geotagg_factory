import streamlit as st
import pandas as pd
import folium
from datetime import datetime
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.title("Factory & Dispensary Geo Dashboard")

# Upload Excel
file = st.file_uploader("Upload Excel file", type=["xlsx"])



if file:

    df = pd.read_excel(file)
    st.write(df.columns)
    st.write(df['Number_of_IPs'].dtype)

    # Convert date
    df['Last_Camp'] = pd.to_datetime(df['Last_Camp'], errors='coerce')

    # Sidebar filters
    st.sidebar.header("Filters")

    type_filter = st.sidebar.multiselect(
        "Select Type",
        df['Type'].unique(),
        default=df['Type'].unique()
    )

    df = df[df['Type'].isin(type_filter)]

    # 🎚️ IP Slider
    min_ips = int(df['Number_of_IPs'].min())
    max_ips = int(df['Number_of_IPs'].max())

    ip_range = st.sidebar.slider(
        "Select IP Range",
        min_value=min_ips,
        max_value=max_ips,
        value=(min_ips, max_ips)
    )

    df = df[
        (df['Number_of_IPs'] >= ip_range[0]) &
        (df['Number_of_IPs'] <= ip_range[1])
    ]

    # 📅 Date filter
    min_date = df['Last_Camp'].min()
    max_date = df['Last_Camp'].max()

    date_range = st.sidebar.date_input(
        "Last Camp Date Range",
        [min_date, max_date],
	key="date_range"
    )

    df = df[
        (df['Last_Camp'] >= pd.to_datetime(date_range[0])) &
        (df['Last_Camp'] <= pd.to_datetime(date_range[1]))
    ]

    # -----------------------------
    # BUSINESS LOGIC
    
    # Overdue logic (e.g., > 6 months)
    today = datetime.today()
    df['Overdue'] = (today - df['Last_Camp']).dt.days > 180

    # Map
    m = folium.Map(
        location=[df['Latitude'].mean(), df['Longitude'].mean()],
        zoom_start=5
    )

    for _, row in df.iterrows():

        color = 'red' if row['Overdue'] else 'green'

        popup = f"""
        <b>Name:</b> {row['Name']}<br>
        <b>Type:</b> {row['Type']}<br>
        <b>IPs:</b> {row['Number_of_IPs']}<br>
        <b>Last Camp:</b> {row['Last_Camp'].date()}<br>
        <b>Status:</b> {'Overdue' if row['Overdue'] else 'OK'}
        """

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=7,
            color=color,
            fill=True,
            popup=popup
        ).add_to(m)

    html(m._repr_html_(), height=600)

    # Summary metrics
    st.subheader("Summary")
    col1, col2 = st.columns(2)

    col1.metric("Total Locations", len(df))
    col2.metric("Overdue Locations", df['Overdue'].sum())
