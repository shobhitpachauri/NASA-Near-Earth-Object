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
    page_title="NEO Hazard Monitor",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_radar_plot(hazardous_df, current_time):
    """Create scientific radar plot for hazardous objects"""
    if hazardous_df.empty:
        return None
        
    def normalize(x, min_val, max_val):
        return (x - min_val) / (max_val - min_val)
    
    fig = go.Figure()
    
    # Only plot the 5 most recent objects
    for _, neo in hazardous_df.tail(5).iterrows():
        velocity_norm = normalize(neo['relative_velocity'], 20000, 100000)
        distance_norm = 1 - normalize(neo['miss_distance'], 10000, 500000)
        diameter_norm = normalize(neo['est_diameter_min'], 0.1, 2.0)
        risk_score = (velocity_norm + distance_norm + diameter_norm) / 3
        
        fig.add_trace(go.Scatterpolar(
            r=[velocity_norm, distance_norm, diameter_norm, risk_score, velocity_norm],
            theta=['Velocity', 'Proximity', 'Size', 'Risk Score', 'Velocity'],
            name=f"{neo['name']} ({risk_score:.2f})",
            fill='toself',
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title=f"NEO Hazard Analysis - {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=700
    )
    
    return fig

def main():
    st.title("Near-Earth Objects Hazard Monitor 🌍☄️")
    
    # Sidebar
    st.sidebar.title("Analysis Settings")
    update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 2)
    
    # Initialize session state
    if 'last_data' not in st.session_state:
        st.session_state.last_data = None
    if 'hazardous_history' not in st.session_state:
        st.session_state.hazardous_history = pd.DataFrame()
    
    # Create fixed containers
    header = st.empty()
    metrics = st.empty()
    radar = st.empty()
    table = st.empty()
    details_expander = st.expander("View Historical Data", expanded=False)
    
    while True:
        try:
            current_time = datetime.now()
            
            # Update header with current time
            header.markdown(f"""
            ### Real-time Analysis of Potentially Hazardous Objects
            Last updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            # Fetch new data
            response = requests.get('http://localhost:5000/api/objects')
            data = response.json()
            df = pd.DataFrame(data)
            
            # Get hazardous objects
            hazardous_df = df[df['hazardous']].copy()
            hazardous_df['detected_time'] = current_time.strftime('%H:%M:%S')
            
            # Update hazardous history
            st.session_state.hazardous_history = pd.concat([
                st.session_state.hazardous_history,
                hazardous_df
            ]).drop_duplicates(subset=['name']).tail(10)
            
            # Update metrics in a single container
            with metrics.container():
                col1, col2, col3, col4 = st.columns(4)
                
                if st.session_state.last_data is not None:
                    last_df = pd.DataFrame(st.session_state.last_data)
                    hazard_delta = len(hazardous_df) - len(last_df[last_df['hazardous']])
                    dist_delta = df['miss_distance'].min() - last_df['miss_distance'].min()
                    vel_delta = df['relative_velocity'].max() - last_df['relative_velocity'].max()
                else:
                    hazard_delta = dist_delta = vel_delta = None
                
                col1.metric(
                    "Active Hazards", 
                    len(hazardous_df),
                    delta=hazard_delta,
                    delta_color="inverse"
                )
                col2.metric(
                    "Closest (km)",
                    f"{df['miss_distance'].min():,.0f}",
                    delta=f"{dist_delta:,.0f}" if dist_delta is not None else None
                )
                col3.metric(
                    "Max Velocity (km/h)",
                    f"{df['relative_velocity'].max():,.0f}",
                    delta=f"{vel_delta:,.0f}" if vel_delta is not None else None
                )
                col4.metric(
                    "Max Size (km)",
                    f"{df['est_diameter_min'].max():.2f}",
                    None
                )
            
            # Update radar plot in fixed container
            if not hazardous_df.empty:
                radar_fig = create_radar_plot(hazardous_df, current_time)
                if radar_fig:
                    radar.plotly_chart(radar_fig, use_container_width=True)
            else:
                radar.info("No hazardous objects currently detected.")
            
            # Update recent hazards table
            if not hazardous_df.empty:
                display_cols = [
                    'name', 'detected_time', 'miss_distance', 
                    'relative_velocity', 'est_diameter_min'
                ]
                
                recent_df = hazardous_df[display_cols].tail(5).copy()
                recent_df = recent_df.reset_index(drop=True)
                
                recent_df.columns = [
                    'Object Name', 'Detected At', 'Miss Distance (km)', 
                    'Velocity (km/h)', 'Estimated Diameter (km)'
                ]
                
                styled_df = recent_df.style.format({
                    'Miss Distance (km)': '{:,.0f}',
                    'Velocity (km/h)': '{:,.0f}',
                    'Estimated Diameter (km)': '{:.2f}'
                })
                
                table.dataframe(styled_df, hide_index=True)
            else:
                table.info("No hazardous objects in current scan.")
            
            # Update historical data in expander
            with details_expander:
                if not st.session_state.hazardous_history.empty:
                    st.markdown("### Historical Hazard Detections")
                    st.dataframe(
                        st.session_state.hazardous_history.style.format({
                            'miss_distance': '{:,.0f}',
                            'relative_velocity': '{:,.0f}',
                            'est_diameter_min': '{:.2f}'
                        }),
                        hide_index=True
                    )
                else:
                    st.info("No historical data available yet.")
            
            # Store current data
            st.session_state.last_data = data
            
            time.sleep(update_interval)
            
        except Exception as e:
            st.error(f"Error updating data: {str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    main() 