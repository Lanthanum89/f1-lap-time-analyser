import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import os
from lap_analyser import (
    setup_cache, load_session, best_laps_dataframe, 
    plot_lap_comparison, plot_sector_comparison, 
    plot_telemetry_comparison, plot_lap_time_distribution
)

# Page config
st.set_page_config(
    page_title="F1 Lap Time Analyser",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🏎️ F1 Lap Time Analyser")
st.markdown("Interactive analysis of Formula 1 session data using FastF1")

# Sidebar for session selection
st.sidebar.header("Session Selection")

# Cache setup
cache_dir = st.sidebar.text_input("Cache Directory", value=os.path.expanduser("~/.fastf1-cache"))
if st.sidebar.button("Setup Cache"):
    setup_cache(cache_dir)
    st.sidebar.success("Cache setup complete!")

# Session parameters
year = st.sidebar.selectbox("Season", options=range(2018, 2025), index=5)  # Default to 2023
gp_options = [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami", "Monaco",
    "Spain", "Canada", "Austria", "Great Britain", "Hungary", "Belgium", 
    "Netherlands", "Italy", "Singapore", "Japan", "Qatar", "United States",
    "Mexico", "Brazil", "Las Vegas", "Abu Dhabi"
]
gp = st.sidebar.selectbox("Grand Prix", options=gp_options, index=8)  # Default to Italy
session_type = st.sidebar.selectbox("Session", options=["FP1", "FP2", "FP3", "Q", "R"], index=3)

# Load session button
if st.sidebar.button("Load Session", type="primary"):
    with st.spinner(f"Loading {year} {gp} {session_type}..."):
        try:
            setup_cache(cache_dir)
            session = load_session(year, gp, session_type)
            st.session_state.session = session
            st.session_state.session_info = f"{year} {gp} {session_type}"
            st.sidebar.success("Session loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error loading session: {str(e)}")

# Main content
if 'session' in st.session_state:
    session = st.session_state.session
    
    # Session info
    st.header(f"📊 Analysis: {st.session_state.session_info}")
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Best Laps", "Lap Comparison", "Sector Analysis", "Telemetry", "Distribution"])
    
    with tab1:
        st.subheader("🏆 Best Lap Times")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            top_n = st.slider("Show top N drivers", min_value=5, max_value=20, value=10)
        
        with col1:
            try:
                best_laps = best_laps_dataframe(session)
                st.dataframe(
                    best_laps.head(top_n)[['Driver', 'Team', 'LapNumber', 'Compound', 'LapTime_s']], 
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error computing best laps: {str(e)}")
    
    with tab2:
        st.subheader("📈 Lap Time Comparison")
        
        # Get available drivers
        available_drivers = sorted(session.laps['Driver'].unique())
        selected_drivers = st.multiselect(
            "Select drivers to compare",
            options=available_drivers,
            default=available_drivers[:3] if len(available_drivers) >= 3 else available_drivers
        )
        
        if selected_drivers:
            try:
                fig = plot_lap_comparison(session, selected_drivers, interactive=True)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating lap comparison: {str(e)}")
    
    with tab3:
        st.subheader("🎯 Sector Time Analysis")
        
        available_drivers = sorted(session.laps['Driver'].unique())
        selected_drivers_sector = st.multiselect(
            "Select drivers for sector analysis",
            options=available_drivers,
            default=available_drivers[:5] if len(available_drivers) >= 5 else available_drivers,
            key="sector_drivers"
        )
        
        if selected_drivers_sector and st.button("Generate Sector Analysis"):
            try:
                sector_df = plot_sector_comparison(session, selected_drivers_sector)
                if sector_df is not None:
                    st.pyplot(plt.gcf())
                    st.subheader("Sector Time Data")
                    st.dataframe(sector_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error in sector analysis: {str(e)}")
    
    with tab4:
        st.subheader("🔧 Telemetry Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            available_drivers = sorted(session.laps['Driver'].unique())
            selected_drivers_tel = st.multiselect(
                "Select drivers for telemetry",
                options=available_drivers,
                default=available_drivers[:3] if len(available_drivers) >= 3 else available_drivers,
                key="telemetry_drivers"
            )
        
        with col2:
            telemetry_type = st.selectbox(
                "Telemetry Type",
                options=["Speed", "Throttle", "Brake", "nGear", "RPM"]
            )
        
        if selected_drivers_tel:
            try:
                fig = plot_telemetry_comparison(session, selected_drivers_tel, telemetry_type)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating telemetry plot: {str(e)}")
    
    with tab5:
        st.subheader("📊 Lap Time Distribution")
        
        try:
            fig = plot_lap_time_distribution(session)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating distribution plot: {str(e)}")
    
    # Additional info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Session Info")
    if hasattr(session, 'session_info'):
        st.sidebar.write(f"**Date:** {session.session_info.get('Date', 'N/A')}")
        st.sidebar.write(f"**Weather:** {session.session_info.get('Weather', 'N/A')}")
    
    # Driver standings for the session
    if hasattr(session, 'results') and session.results is not None:
        st.sidebar.markdown("### Session Results")
        results_df = session.results[['Abbreviation', 'Position', 'Time']]
        st.sidebar.dataframe(results_df.head(10), use_container_width=True)

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to the F1 Lap Time Analyser! 🏁
    
    This interactive dashboard allows you to:
    - 🏆 View best lap times for any F1 session
    - 📈 Compare lap times between drivers
    - 🎯 Analyze sector performance
    - 🔧 Examine detailed telemetry data
    - 📊 Visualize lap time distributions
    
    ### Getting Started:
    1. Select a season, Grand Prix, and session type in the sidebar
    2. Click "Load Session" to download the data
    3. Explore the different analysis tabs
    
    ### Features:
    - **Interactive plots** powered by Plotly
    - **Real-time data** from FastF1 API
    - **Caching** for faster subsequent loads
    - **Multiple visualization types** for comprehensive analysis
    
    👈 **Start by selecting a session in the sidebar!**
    """)
    
    # Sample data showcase
    st.markdown("### Example Analysis")
    st.image("https://via.placeholder.com/800x400/FF6B6B/FFFFFF?text=F1+Data+Visualization", 
             caption="Interactive lap time analysis with multiple drivers")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using FastF1, Streamlit, and Plotly | Data from Formula 1")