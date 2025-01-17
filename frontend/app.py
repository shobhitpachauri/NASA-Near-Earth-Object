import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import numpy as np
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="NEO Monitor (Live)",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font { font-size:24px !important; }
    .stMetric:hover { background-color: #f0f2f6; transition: 0.3s; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("Near-Earth Objects Monitor 🌍☄️")
    
    # Sidebar for filters and settings
    st.sidebar.title("Settings")
    update_interval = st.sidebar.slider("Update Interval (seconds)", 5, 60, 10)
    show_hazardous_only = st.sidebar.checkbox("Show Hazardous Objects Only")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    metric_placeholders = {
        'total': col1.empty(),
        'hazardous': col2.empty(),
        'closest': col3.empty(),
        'fastest': col4.empty()
    }
    
    # Create placeholders for charts
    charts_col1, charts_col2 = st.columns(2)
    distance_chart = charts_col1.empty()
    velocity_chart = charts_col2.empty()
    
    # Data table section
    table_section = st.expander("Detailed Data", expanded=False)
    
    while True:
        try:
            # Fetch new data
            response = requests.get('http://localhost:5000/api/objects')
            data = response.json()
            df = pd.DataFrame(data)
            
            if show_hazardous_only:
                df = df[df['hazardous']]
            
            # Update metrics
            metric_placeholders['total'].metric(
                "Total Objects", 
                len(df),
                delta=None
            )
            metric_placeholders['hazardous'].metric(
                "Hazardous Objects",
                len(df[df['hazardous']]),
                delta=None
            )
            metric_placeholders['closest'].metric(
                "Closest Approach (km)",
                f"{df['miss_distance'].min():,.0f}",
                delta=None
            )
            metric_placeholders['fastest'].metric(
                "Fastest Object (km/h)",
                f"{df['relative_velocity'].max():,.0f}",
                delta=None
            )
            
            # Update distance distribution
            fig_distance = px.histogram(
                df, 
                x='miss_distance',
                title="Distance Distribution",
                labels={'miss_distance': 'Distance from Earth (km)'},
                color='hazardous'
            )
            distance_chart.plotly_chart(
                fig_distance, 
                use_container_width=True,
                key="distance_plot"
            )
            
            # Update velocity distribution
            fig_velocity = px.scatter(
                df,
                x='miss_distance',
                y='relative_velocity',
                color='hazardous',
                size='est_diameter_min',
                hover_data=['name'],
                title="Velocity vs Distance"
            )
            velocity_chart.plotly_chart(
                fig_velocity, 
                use_container_width=True,
                key="velocity_plot"
            )
            
            # Update data table
            with table_section:
                st.dataframe(
                    df.style.highlight_max(axis=0, subset=['miss_distance', 'relative_velocity'])
                )
            
            # Wait for next update
            time.sleep(update_interval)
            
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main() 