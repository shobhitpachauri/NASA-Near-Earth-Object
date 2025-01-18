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

# Custom CSS
st.markdown("""
    <style>
    .big-font { font-size:24px !important; }
    .stMetric:hover { background-color: #f0f2f6; transition: 0.3s; }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def format_number(num):
    return f"{num:,}"

def main():
    st.title("Near-Earth Objects Monitor 🌍☄️")
    st.markdown("Real-time monitoring and analysis of Near-Earth Objects (NEOs)")
    
    # Sidebar
    st.sidebar.title("Settings")
    update_interval = st.sidebar.slider("Update Interval (seconds)", 5, 60, 10)
    show_hazardous_only = st.sidebar.checkbox("Show Hazardous Objects Only")
    
    # Initialize session state
    if 'update_counter' not in st.session_state:
        st.session_state.update_counter = 0
    
    # Global Statistics
    try:
        stats_response = requests.get('http://localhost:5000/api/stats')
        global_stats = stats_response.json()
        
        st.header("Global NEO Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Known NEOs", 
                     format_number(global_stats['total_known_neos']))
        with col2:
            st.metric("Potentially Hazardous", 
                     format_number(global_stats['potentially_hazardous_total']))
        with col3:
            st.metric("Discovery Rate", 
                     global_stats['discovery_rate'])
        with col4:
            st.metric("Largest Known", 
                     global_stats['largest_known'])
        
        # Information boxes
        st.subheader("Current NEO Monitoring")
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("""
            <div class="info-box">
            <h3>Observation Programs</h3>
            </div>
            """, unsafe_allow_html=True)
            for program in global_stats['observation_programs']:
                st.markdown(f"- {program}")
                
        with info_col2:
            st.markdown("""
            <div class="info-box">
            <h3>Recent Activity</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Closest Approach 2024:** {global_stats['closest_approach_2024']}")
            st.markdown(f"**Last Updated:** {global_stats['last_update']}")
    
    except Exception as e:
        st.error(f"Error fetching global stats: {str(e)}")
    
    # Live Monitoring Section
    st.header("Live Monitoring")
    
    # Create placeholders for charts
    charts_col1, charts_col2 = st.columns(2)
    distance_chart = charts_col1.empty()
    velocity_chart = charts_col2.empty()
    
    # Data table section
    table_section = st.expander("Detailed Data", expanded=False)
    
    while True:
        try:
            st.session_state.update_counter += 1
            
            # Fetch new data
            response = requests.get('http://localhost:5000/api/objects')
            data = response.json()
            df = pd.DataFrame(data['objects'])
            
            # Add timestamp display
            st.sidebar.markdown(f"Last Update: {data['timestamp']}")
            
            if show_hazardous_only:
                df = df[df['hazardous']]
            
            # Update charts
            fig_distance = px.histogram(
                df, 
                x='miss_distance',
                title="Distance Distribution",
                labels={'miss_distance': 'Distance from Earth (km)'},
                color='hazardous',
                color_discrete_map={True: 'red', False: 'green'}
            )
            distance_chart.plotly_chart(
                fig_distance, 
                use_container_width=True,
                key=f"distance_plot_{st.session_state.update_counter}"
            )
            
            fig_velocity = px.scatter(
                df,
                x='miss_distance',
                y='relative_velocity',
                color='hazardous',
                size='est_diameter_min',
                hover_data=['name', 'orbit_type', 'discovery_date'],
                title="Velocity vs Distance",
                color_discrete_map={True: 'red', False: 'green'}
            )
            velocity_chart.plotly_chart(
                fig_velocity, 
                use_container_width=True,
                key=f"velocity_plot_{st.session_state.update_counter}"
            )
            
            # Update data table
            with table_section:
                st.markdown("### Detailed NEO Data")
                styled_df = df.style.highlight_max(axis=0, subset=['miss_distance', 'relative_velocity'])
                st.dataframe(
                    styled_df,
                    key=f"table_{st.session_state.update_counter}"
                )
            
            time.sleep(update_interval)
            
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    main() 