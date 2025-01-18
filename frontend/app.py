import streamlit as st
import pandas as pd
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

def create_threshold_plot(hazardous_df, current_time):
    """Create a simplified threshold plot for hazardous objects"""
    if hazardous_df.empty:
        return None

    # Define thresholds
    velocity_threshold = 50000  # Example threshold for velocity (in km/h)
    distance_threshold = 200000  # Example threshold for miss distance (in km)

    # Create figure
    fig = go.Figure()

    # Add threshold lines
    fig.add_hline(y=velocity_threshold, line_dash="dash", line_color="red", 
                  annotation_text="Velocity Threshold", annotation_position="top right")
    fig.add_vline(x=distance_threshold, line_dash="dash", line_color="blue", 
                   annotation_text="Distance Threshold", annotation_position="top right")

    # Plot each hazardous object
    for _, neo in hazardous_df.iterrows():
        color = 'red' if neo['relative_velocity'] > velocity_threshold else 'green'
        fig.add_trace(go.Scatter(
            x=[neo['miss_distance']], 
            y=[neo['relative_velocity']],
            mode='markers+text',
            marker=dict(size=10, color=color),
            text=[f"{neo['name']} ({neo['relative_velocity']:.0f} km/h)"],
            textposition="top center"
        ))

    # Update layout
    fig.update_layout(
        title=f"NEO Hazard Analysis - {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
        xaxis_title="Miss Distance (km)",
        yaxis_title="Relative Velocity (km/h)",
        showlegend=False,
        height=700,
        xaxis=dict(range=[0, max(hazardous_df['miss_distance']) * 1.1]),
        yaxis=dict(range=[0, max(hazardous_df['relative_velocity']) * 1.1])
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
    
    # Create placeholders for dynamic content
    header_placeholder = st.empty()
    metrics_placeholder = st.empty()
    threshold_plot_placeholder = st.empty()
    table_placeholder = st.empty()
    details_expander = st.expander("View Historical Data", expanded=False)
    
    while True:
        try:
            current_time = datetime.now()
            
            # Update header with current time
            header_placeholder.markdown(f"""
            ### Real-time Analysis of Potentially Hazardous Objects
            Last updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
            """)
            
            # Fetch NEO data
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
            with metrics_placeholder.container():
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
            
            # Update threshold plot in fixed container
            if not hazardous_df.empty:
                threshold_fig = create_threshold_plot(hazardous_df, current_time)
                if threshold_fig:
                    threshold_plot_placeholder.plotly_chart(threshold_fig, use_container_width=True)
            else:
                threshold_plot_placeholder.info("No hazardous objects currently detected.")
            
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
                
                table_placeholder.dataframe(styled_df, hide_index=True)
            else:
                table_placeholder.info("No hazardous objects in current scan.")
            
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