import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="NEO Monitor",
    page_icon="☄️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

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

def create_metric_card(title, value, delta=None):
    with st.container():
        st.markdown(f"""
            <div class="metric-card">
                <p>{title}</p>
                <h2>{value}</h2>
                {f"<p>Δ {delta}</p>" if delta else ""}
            </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.title("Near-Earth Objects Monitor 🌍☄️")
    st.markdown("Real-time monitoring of Near-Earth Objects and potential hazards")
    
    # Add a refresh button
    if st.button("🔄 Refresh Data"):
        st.experimental_rerun()
    
    # Load data
    stats, objects, hazardous = load_data()
    
    if not all([stats, objects, hazardous]):
        st.warning("Unable to load data. Please check if the backend server is running.")
        return
    
    # Dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total Objects", stats['total_objects'])
    with col2:
        create_metric_card("Hazardous Objects", stats['hazardous_count'])
    with col3:
        create_metric_card("Avg Diameter (km)", f"{stats['avg_diameter']:.2f}")
    with col4:
        create_metric_card("Closest Approach (km)", 
                          f"{stats['closest_object']['distance']:,.2f}")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Overview", "Hazardous Objects", "Data Table"])
    
    with tab1:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Object Distribution")
            df_objects = pd.DataFrame(objects)
            fig = px.scatter(df_objects, 
                           x='miss_distance', 
                           y='est_diameter_min',
                           color='hazardous',
                           hover_data=['name'],
                           title="NEO Distribution by Distance and Size")
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("Velocity Distribution")
            fig = px.histogram(df_objects, 
                             x='relative_velocity',
                             color='hazardous',
                             title="Velocity Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Hazardous Objects Analysis")
        df_hazardous = pd.DataFrame(hazardous)
        if not df_hazardous.empty:
            fig = px.scatter(df_hazardous,
                           x='miss_distance',
                           y='relative_velocity',
                           size='est_diameter_min',
                           hover_data=['name'],
                           title="Hazardous Objects Analysis")
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed hazardous objects table
            st.dataframe(df_hazardous)
        else:
            st.info("No hazardous objects found in the current dataset.")
    
    with tab3:
        st.subheader("Raw Data")
        df_all = pd.DataFrame(objects)
        st.dataframe(df_all)
        
        # Add download button
        csv = df_all.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'neo_data_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main() 