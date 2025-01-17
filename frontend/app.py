import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="NEO Monitor",
    page_icon="☄️",
    layout="wide"
)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"

def load_data():
    try:
        stats = requests.get(f"{API_BASE_URL}/stats").json()
        objects = requests.get(f"{API_BASE_URL}/objects").json()
        hazardous = requests.get(f"{API_BASE_URL}/hazardous").json()
        return stats, objects, hazardous
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data: {str(e)}")
        return None, None, None

def main():
    st.title("Near-Earth Objects Monitor 🌍☄️")
    st.markdown("Real-time monitoring of Near-Earth Objects and potential hazards")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    stats, objects, hazardous = load_data()
    
    if not all([stats, objects, hazardous]):
        st.warning("Unable to load data. Please check if the backend server is running.")
        return
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Objects", stats['total_objects'])
    with col2:
        st.metric("Hazardous Objects", stats['hazardous_count'])
    with col3:
        st.metric("Avg Diameter (km)", f"{stats['avg_diameter']:.2f}")
    with col4:
        st.metric("Closest Approach (km)", 
                 f"{stats['closest_object']['distance']:,.2f}")
    
    # Data visualization
    tab1, tab2 = st.tabs(["All Objects", "Hazardous Objects"])
    
    with tab1:
        df_objects = pd.DataFrame(objects)
        fig = px.scatter(df_objects, 
                        x='miss_distance', 
                        y='est_diameter_min',
                        color='hazardous',
                        hover_data=['name'],
                        title="NEO Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        df_hazardous = pd.DataFrame(hazardous)
        if not df_hazardous.empty:
            fig = px.scatter(df_hazardous,
                           x='miss_distance',
                           y='relative_velocity',
                           size='est_diameter_min',
                           hover_data=['name'],
                           title="Hazardous Objects")
            st.plotly_chart(fig, use_container_width=True)
        
    # Data table
    st.subheader("Raw Data")
    st.dataframe(pd.DataFrame(objects))

if __name__ == "__main__":
    main() 