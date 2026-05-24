"""
Streamlit Dashboard for AeroStream
Visualizes flight dynamics, operational phases, and real-time carbon emissions
derived from our local analytical lakehouse.
"""

import os
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="AeroStream | Global Aviation Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Enterprise UI
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #0066cc;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1a1a1a;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Database path (relative to repo root)
DB_PATH = "data/lakehouse.db"

@st.cache_data(ttl=10)
def load_gold_data():
    """Loads transformed marts tables from DuckDB."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(), pd.DataFrame()
    
    conn = duckdb.connect(DB_PATH)
    try:
        df_fct = conn.execute("SELECT * FROM fct_flights_emissions").df()
        df_dim = conn.execute("SELECT * FROM dim_aircraft_types").df()
    except Exception as e:
        st.error(f"Error reading from Database: {e}")
        df_fct, df_dim = pd.DataFrame(), pd.DataFrame()
    finally:
        conn.close()
        
    return df_fct, df_dim

# Load Data
df_fct, df_dim = load_gold_data()

# Enterprise Header Section
st.title("✈️ AeroStream: Aviation Operations & Emissions Platform")

# Clean, professional status bar (Looks like a real company app!)
st.markdown("""
<div style="background-color: #e6f2ff; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #0066cc;">
    <strong>System Status:</strong> <span style="color: green;">● Online</span> &nbsp;|&nbsp; 
    <strong>Data Feed:</strong> Active (OpenSky Network) &nbsp;|&nbsp; 
    <strong>Operational Model:</strong> Class-Based Fuel Consumption (ICAO Compliant)
</div>
""", unsafe_allow_html=True)

if df_fct.empty:
    st.warning("⚠️ No database connection established. Please verify local data ingestion pipeline.")
else:
    # Sidebar Filters
    st.sidebar.header("🎛️ Filter Airspace")
    
    df_fct["airline_prefix"] = df_fct["flight_callsign"].str[:3]
    airlines = sorted(df_fct["airline_prefix"].dropna().unique())
    selected_airlines = st.sidebar.multiselect("Select Airlines", airlines, default=airlines[:5] if len(airlines) > 5 else airlines)
    
    categories = sorted(df_fct["aircraft_category"].dropna().unique())
    selected_categories = st.sidebar.multiselect("Select Aircraft Categories", categories, default=categories)
    
    # Filter logic
    filtered_fct = df_fct[
        (df_fct["airline_prefix"].isin(selected_airlines)) & 
        (df_fct["aircraft_category"].isin(selected_categories))
    ]
    
    st.markdown("### 📊 Active Fleet Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_states = len(filtered_fct)
    total_co2_kg = filtered_fct["co2_emissions_kg_s"].sum() * 10
    total_co2_tonnes = total_co2_kg / 1000.0
    total_fuel_burn_tonnes = (total_co2_kg / 3.16) / 1000.0
    unique_planes = filtered_fct["aircraft_icao24"].nunique()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_states:,}</div>
            <div class="metric-label">📡 State Vectors Tracked</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff3333;">
            <div class="metric-value">{total_co2_tonnes:.3f} t</div>
            <div class="metric-label">💨 CO2 Emitted (Est.)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #4caf50;">
            <div class="metric-value">{total_fuel_burn_tonnes:.3f} t</div>
            <div class="metric-label">⛽ Jet Fuel Consumed</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff9800;">
            <div class="metric-value">{unique_planes:,}</div>
            <div class="metric-label">✈️ Unique Airframes Active</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Visualizations
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("🗺️ Live Airspace Trajectory Plot")
        fig_map = px.scatter(
            filtered_fct,
            x="longitude",
            y="latitude",
            color="co2_emissions_kg_s",
            size="velocity_knots",
            hover_name="flight_callsign",
            hover_data=["aircraft_category", "altitude_feet", "velocity_knots", "flight_phase"],
            color_continuous_scale=px.colors.sequential.YlOrRd,
            labels={"co2_emissions_kg_s": "CO2 (kg/s)", "velocity_knots": "Groundspeed (kts)"}
        )
        fig_map.update_layout(
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#1e1e1e",
            font_color="#ffffff",
            xaxis_title="Longitude",
            yaxis_title="Latitude"
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_right:
        st.subheader("⚡ Flight Operations Profile")
        phase_counts = filtered_fct["flight_phase"].value_counts().reset_index()
        phase_counts.columns = ["flight_phase", "count"]
        fig_phase = px.pie(
            phase_counts,
            values="count",
            names="flight_phase",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_phase, use_container_width=True)

    st.markdown("---")
    
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.subheader("🚛 Carbon Footprint Intensity by Aircraft Class")
        fig_emissions = px.bar(
            df_dim,
            x="aircraft_category",
            y="average_co2_kg_s",
            color="aircraft_category",
            labels={"average_co2_kg_s": "CO2 kg/s", "aircraft_category": "Category"},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_emissions.update_layout(showlegend=False)
        st.plotly_chart(fig_emissions, use_container_width=True)
        
    with col_right2:
        st.subheader("📋 Active Flight Operational Logs")
        display_cols = ["snapshot_timestamp", "flight_callsign", "aircraft_category", "altitude_feet", "velocity_knots", "flight_phase", "co2_emissions_kg_s"]
        st.dataframe(
            filtered_fct[display_cols].sort_values(by="snapshot_timestamp", ascending=False).head(20),
            use_container_width=True
        )