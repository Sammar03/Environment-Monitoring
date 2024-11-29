import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

# Initialize or load the live data DataFrame
try:
    live_data = pd.read_csv('live_sensor_readings.csv')
except FileNotFoundError:
    live_data = pd.DataFrame(columns=['Timestamp', 'Temperature', 'Pressure', 'Gas', 'Humidity', 'DewPoint'])

# Function to fetch live readings from ESP32
def fetch_live_readings():
    try:
        response = requests.get('https://glad-scorpion-naturally.ngrok-free.app/')  # Update with your ESP32's IP
        if response.status_code == 200:
            data = response.json()
            # Format timestamp to Hours:Minutes:Seconds
            data['Timestamp'] = pd.to_datetime('now').strftime('%H:%M:%S')
            return data
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching live readings: {e}")
        return None

# Function to update the dashboard
def update_dashboard():
    global live_data

    # Fetch new live readings and add to DataFrame
    new_row = fetch_live_readings()
    if new_row:
        new_df = pd.DataFrame([new_row])
        live_data = pd.concat([live_data, new_df], ignore_index=True)

        # Save live data to CSV for downloading
        live_data.to_csv('live_sensor_readings.csv', index=False)

        # Update graph with live data
        fig = px.line(live_data, x='Timestamp', y=selected_quantity, title=f'Live {selected_quantity} Readings')
        fig.update_layout(
            plot_bgcolor='#2d2d2d',
            paper_bgcolor='#2d2d2d',
            font_color='white',
            xaxis_title='Time',
            yaxis_title=units[selected_quantity],
            xaxis_tickformat="%H:%M:%S"
        )
        fig.update_traces(line_color='orange')
        st.plotly_chart(fig, use_container_width=True)
        
        # Update live readings markdown
        update_live_readings(new_row)
    else:
        st.warning("Waiting for live data...")

# Function to update the live readings markdown display with a styled box
def update_live_readings(data):
    live_readings_html = f"""
    <style>
        .bordered-box {{
            border: 1px solid orange;
            padding: 10px;
            border-radius: 5px;
            background-color: #333333; /* Dark background */
            color: white; /* White text */
        }}
    </style>
    <div class="bordered-box">
        <h3>Live Readings</h3>
        <p><strong>Temperature:</strong> {data['Temperature']:.2f} °C</p>
        <p><strong>Pressure:</strong> {data['Pressure']:.2f} hPa</p>
        <p><strong>Gas:</strong> {data['Gas']:.2f} ppm</p>
        <p><strong>Humidity:</strong> {data['Humidity']:.2f} %</p>
        <p><strong>DewPoint:</strong> {data['DewPoint']:.2f} °C</p>
    </div>
    """
    live_readings_placeholder.markdown(live_readings_html, unsafe_allow_html=True)

# Set up the Streamlit layout
st.set_page_config(layout="wide")
st.title("Live BME 680 Sensor Dashboard")

# Sidebar options for quantity selection
selected_quantity = st.sidebar.selectbox("Select Quantity", options=['Temperature', 'Pressure', 'Gas', 'Humidity'], index=0)
units = {'Temperature': '°C', 'Pressure': 'hPa', 'Gas': 'ppm', 'Humidity': '%'}
st.sidebar.button("Refresh Data", on_click=update_dashboard)

# Placeholder for live readings markdown
live_readings_placeholder = st.empty()

# Download button for the CSV file
st.sidebar.download_button(
    label="Download CSV",
    data=live_data.to_csv(index=False),
    file_name="live_sensor_readings.csv",
    mime="text/csv"
)

# Continuously update the live readings panel every 10 seconds
while True:
    update_dashboard()
    time.sleep(10)
    st.rerun()
