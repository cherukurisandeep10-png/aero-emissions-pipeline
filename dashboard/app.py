"""
Streamlit Dashboard for AeroStream
Visualizes flight dynamics, operational phases, and real-time carbon emissions
derived from our local analytical lakehouse.
Features a clean, modern corporate light theme, compact visuals, multi-phase filters, and chronological date selectors.
"""

import os
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# Set page config with a clean light theme behavior
st.set_page_config(
    page_title="AeroStream | Global Flight Operations",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful, modern, bright corporate look (SaaS style like Snowflake/Datadog)
st.markdown("""
<style>
    /* Main Background & Text Color - Modern Light Slate */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    /* Sidebar styling - Clean Dark Slate */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Main Header Container */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 32px;
        color: #0f172a;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .subtitle {
        font-size: 14px;
        color: #64748b;
        margin-top: 5px;
    }
    
    /* Compact Flight Picture Box styling */
    .compact-img-box {
        width: 180px;
        height: 100px;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Operational Status Banner - Professional Ice Blue */
    .status-banner {
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        border-left: 5px solid #0284c7;
        border-radius: 8px;
        padding: 12px 20px;
        margin-bottom: 25px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .status-text {
        font-size: 14px;
        color: #0369a1;
        font-weight: 500;
    }
    .status-active {
        color: #0284c7;
        font-weight: 700;
    }
    .radar-pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #0284c7;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.7);
        animation: pulse 1.8s infinite;
        vertical-align: middle;
        margin-right: 6px;
    }
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(2, 132, 199, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(2, 132, 199, 0);
        }
    }
    
    /* Clean Cards with Subtle Shadow Lift */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-top: 4px solid #0284c7;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 2px;
        font-family: 'Inter', sans-serif;
    }
    .kpi-label {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Section headers */
    .section-header {
        color: #0f172a;
        font-weight: 700;
        font-size: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
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

# 📰 Compact, Unified Header (Title on left, small box-sized aircraft photo on right)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px 25px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
    <div style="flex-grow: 1;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 5px;">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 16V14L13 9V3.5C13 2.67 12.33 2 11.5 2C10.67 2 10 2.67 10 3.5V9L2 14V16L10 13.5V19L8 20.5V22L11.5 21L15 22V20.5L13 19V13.5L21 16Z" fill="#0284c7"/>
            </svg>
            <span style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 30px; color: #0f172a;">AeroStream: Dispatch & Emissions Control</span>
        </div>
        <div style="font-size: 14px; color: #64748b; margin-left: 42px;">Global Operations Telemetry Engine & ICAO Environmental Analytics</div>
    </div>
    <div style="width: 180px; height: 100px; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.06); flex-shrink: 0; margin-left: 20px;">
        <img src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=250&h=130&q=80" style="width: 100%; height: 100%; object-fit: cover;" />
    </div>
</div>
""", unsafe_allow_html=True)

# Operational Status Banner (Bright Ice-Blue Theme)
st.markdown("""
<div class="status-banner">
    <div class="status-text">
        <span class="radar-pulse"></span>
        SYSTEM CONNECTION: <span class="status-active">ONLINE</span> &nbsp;|&nbsp; 
        DATA STREAM: <span class="status-active">LIVE ADS-B RADAR</span> &nbsp;|&nbsp; 
        COMPLIANCE: <span class="status-active">ICAO EMISSIONS ENGINE</span>
    </div>
    <div class="status-text" style="font-size: 11px; font-weight: 700; color: #0284c7;">
        FLEET METRICS CONTROL
    </div>
</div>
""", unsafe_allow_html=True)

if df_fct.empty:
    st.warning("⚠️ No database connection established. Please verify local data ingestion pipeline.")
else:
    # Sidebar Filters (Dark Slate Sidebar with bright controls)
    st.sidebar.markdown("<h2 style='color: #f8fafc; font-size: 18px; font-weight: 700; margin-bottom: 15px;'>🛰️ Airspace Control</h2>", unsafe_allow_html=True)
    
    # 📅 Chronological Date Selector (Filters yesterday vs. today dynamically!)
    df_fct["snapshot_date"] = pd.to_datetime(df_fct["snapshot_timestamp"]).dt.date
    available_dates = sorted(df_fct["snapshot_date"].dropna().unique(), reverse=True)
    
    st.sidebar.markdown("<h3 style='color: #f1f5f9; font-size: 15px; font-weight: 700; margin-bottom: 5px;'>📅 Select Date</h3>", unsafe_allow_html=True)
    selected_date = st.sidebar.selectbox(
        "Choose Date to Track", 
        ["All Dates"] + [str(d) for d in available_dates], 
        index=1 if len(available_dates) > 0 else 0
    )
    
    # Carriers filter
    df_fct["airline_prefix"] = df_fct["flight_callsign"].str[:3]
    airlines = sorted(df_fct["airline_prefix"].dropna().unique())
    selected_airlines = st.sidebar.multiselect("Select Active Carriers", airlines, default=airlines[:5] if len(airlines) > 5 else airlines)
    
    # Aircraft class filter
    categories = sorted(df_fct["aircraft_category"].dropna().unique())
    selected_categories = st.sidebar.multiselect("Select Aircraft Classes", categories, default=categories)
    
    # Flight Phase Filter (Takeoff, Cruise, Descent, Ground)
    phases = sorted(df_fct["flight_phase"].dropna().unique())
    selected_phases = st.sidebar.multiselect("Filter by Operational Phase", phases, default=phases)
    
    # 🔍 Search Feature
    st.sidebar.markdown("<hr style='border-color: #1e293b;' />", unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style='color: #f1f5f9; font-size: 15px; font-weight: 700; margin-bottom: 5px;'>🔍 Target Active Flight</h3>", unsafe_allow_html=True)
    search_callsign = st.sidebar.text_input("Enter Callsign (e.g. DAL7174, UPS120)", value="").strip().upper()
    
    # Apply baseline filters (including the new flight phase filter!)
    filtered_fct = df_fct[
        (df_fct["airline_prefix"].isin(selected_airlines)) & 
        (df_fct["aircraft_category"].isin(selected_categories)) &
        (df_fct["flight_phase"].isin(selected_phases))
    ]
    
    # Apply Date Selector Filter
    if selected_date != "All Dates":
        filtered_fct = filtered_fct[filtered_fct["snapshot_date"].astype(str) == selected_date]
    
    # Apply search filter if user typed anything
    if search_callsign:
        filtered_fct = filtered_fct[filtered_fct["flight_callsign"].str.upper().str.contains(search_callsign)]
        
    # Compute metrics
    total_states = len(filtered_fct)
    total_co2_kg = filtered_fct["co2_emissions_kg_s"].sum() * 10
    total_co2_tonnes = total_co2_kg / 1000.0
    total_fuel_burn_tonnes = (total_co2_kg / 3.16) / 1000.0
    unique_planes = filtered_fct["aircraft_icao24"].nunique()
    
    # Render customized KPI Cards via HTML grid (Clean Light SaaS look)
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card" style="border-top-color: #0284c7;">
            <div class="kpi-value">{total_states:,}</div>
            <div class="kpi-label">🛰️ Active Vectors Tracked</div>
        </div>
        <div class="kpi-card" style="border-top-color: #ef4444;">
            <div class="kpi-value">{total_co2_tonnes:.3f} t</div>
            <div class="kpi-label">💨 CO2 Mass Emitted</div>
        </div>
        <div class="kpi-card" style="border-top-color: #22c55e;">
            <div class="kpi-value">{total_fuel_burn_tonnes:.3f} t</div>
            <div class="kpi-label">⛽ Jet-A1 Fuel Burned</div>
        </div>
        <div class="kpi-card" style="border-top-color: #f59e0b;">
            <div class="kpi-value">{unique_planes:,}</div>
            <div class="kpi-label">✈️ Airframes Active</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if filtered_fct.empty:
        st.info("ℹ️ No active aircraft found matching that query. Clear the text search or adjust your airspace filters!")
    else:
        # Grid Columns
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("<h3 class='section-header'>🗺️ Spatial Flight Trajectory Radar</h3>", unsafe_allow_html=True)
            fig_map = px.scatter(
                filtered_fct,
                x="longitude",
                y="latitude",
                color="co2_emissions_kg_s",
                size="velocity_knots" if total_states > 1 else None, # avoid single point size error
                hover_name="flight_callsign",
                hover_data=["aircraft_category", "altitude_feet", "velocity_knots", "flight_phase"],
                color_continuous_scale=px.colors.sequential.Bluered,
                labels={"co2_emissions_kg_s": "CO2 (kg/s)", "velocity_knots": "Groundspeed (kts)"}
            )
            # Add sizing backup for single flight search targeting
            if total_states == 1:
                fig_map.update_traces(marker=dict(size=18, symbol="triangle-up"))
                
            fig_map.update_layout(
                plot_bgcolor="#f8fafc",
                paper_bgcolor="#f8fafc",
                font_color="#1e293b",
                xaxis_title="Longitude Coordinate",
                yaxis_title="Latitude Coordinate",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_map, use_container_width=True)
            
        with col_right:
            st.markdown("<h3 class='section-header'>⚡ Airspace Operational Phase Mix</h3>", unsafe_allow_html=True)
            phase_counts = filtered_fct["flight_phase"].value_counts().reset_index()
            phase_counts.columns = ["flight_phase", "count"]
            fig_phase = px.pie(
                phase_counts,
                values="count",
                names="flight_phase",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_phase.update_layout(
                plot_bgcolor="#f8fafc",
                paper_bgcolor="#f8fafc",
                font_color="#1e293b",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_phase, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            st.markdown("<h3 class='section-header'>🚛 Carbon Footprint Intensity by Class</h3>", unsafe_allow_html=True)
            fig_emissions = px.bar(
                df_dim,
                x="aircraft_category",
                y="average_co2_kg_s",
                color="aircraft_category",
                labels={"average_co2_kg_s": "CO2 kg/s", "aircraft_category": "Class"},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_emissions.update_layout(
                plot_bgcolor="#f8fafc",
                paper_bgcolor="#f8fafc",
                font_color="#1e293b",
                showlegend=False,
                xaxis_title="Aircraft Class",
                yaxis_title="Average CO2 (kg/sec)",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_emissions, use_container_width=True)
            
        with col_right2:
            st.markdown("<h3 class='section-header'>📋 Tactical Operational Logs</h3>", unsafe_allow_html=True)
            display_cols = ["snapshot_timestamp", "flight_callsign", "aircraft_category", "altitude_feet", "velocity_knots", "flight_phase", "co2_emissions_kg_s"]
            st.dataframe(
                filtered_fct[display_cols].sort_values(by="snapshot_timestamp", ascending=False).head(20),
                use_container_width=True
            )
