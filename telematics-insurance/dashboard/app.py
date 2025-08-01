"""
Streamlit dashboard for telematics insurance platform
Calls backend endpoints and displays risk assessments, gamification, and claims analysis
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configure page
st.set_page_config(
    page_title="Telematics Insurance Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Backend API URL
API_BASE_URL = "http://localhost:8000"  # Update with your backend URL

def main():
    st.title("🚗 Telematics Insurance Dashboard")
    st.markdown("AI-powered telematics insurance platform with expert risk models")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Risk Assessment", "Driver Dashboard", "Claims Analysis", "Gamification", "Geographic Risk"]
    )
    
    if page == "Risk Assessment":
        risk_assessment_page()
    elif page == "Driver Dashboard":
        driver_dashboard_page()
    elif page == "Claims Analysis":
        claims_analysis_page()
    elif page == "Gamification":
        gamification_page()
    elif page == "Geographic Risk":
        geographic_risk_page()

def risk_assessment_page():
    st.header("🎯 Risk Assessment")
    
    # Input form for risk assessment
    with st.form("risk_assessment_form"):
        st.subheader("Driver Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            driver_id = st.text_input("Driver ID", value="driver_123")
            trip_duration = st.number_input("Trip Duration (minutes)", min_value=1, value=30)
            avg_speed = st.number_input("Average Speed (km/h)", min_value=0.0, value=50.0)
            max_speed = st.number_input("Max Speed (km/h)", min_value=0.0, value=80.0)
            harsh_accel = st.number_input("Harsh Acceleration Events", min_value=0, value=2)
        
        with col2:
            harsh_brake = st.number_input("Harsh Braking Events", min_value=0, value=1)
            phone_usage = st.number_input("Phone Usage (seconds)", min_value=0, value=0)
            latitude = st.number_input("Latitude", value=40.7128)
            longitude = st.number_input("Longitude", value=-74.0060)
            
        st.subheader("Context Information")
        col3, col4 = st.columns(2)
        
        with col3:
            weather_temp = st.number_input("Temperature (°C)", value=20)
            precipitation = st.number_input("Precipitation (mm)", min_value=0.0, value=0.0)
            visibility = st.number_input("Visibility (km)", min_value=0.0, value=10.0)
        
        with col4:
            traffic_density = st.selectbox("Traffic Density", ["light", "normal", "moderate", "heavy"])
            avg_traffic_speed = st.number_input("Average Traffic Speed (km/h)", value=50.0)
            speed_limit = st.number_input("Speed Limit (km/h)", value=60.0)
        
        submitted = st.form_submit_button("Assess Risk")
        
        if submitted:
            # Prepare data for API call
            assessment_data = {
                "driving_data": {
                    "avg_speed": avg_speed,
                    "max_speed": max_speed,
                    "harsh_acceleration_count": harsh_accel,
                    "harsh_braking_count": harsh_brake,
                    "phone_usage_duration": phone_usage
                },
                "location_data": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "weather_data": {
                    "temperature_c": weather_temp,
                    "precipitation_mm": precipitation,
                    "visibility_km": visibility
                },
                "traffic_data": {
                    "density": traffic_density,
                    "average_speed_kmh": avg_traffic_speed,
                    "speed_limit_kmh": speed_limit
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Display mock results (replace with actual API call)
            display_risk_results(assessment_data)

def display_risk_results(data):
    """Display risk assessment results"""
    
    # Mock results - replace with actual API call
    behavior_score = max(20, 100 - data["driving_data"]["harsh_acceleration_count"] * 10 - 
                        data["driving_data"]["harsh_braking_count"] * 10)
    geo_risk = 45 + (abs(data["location_data"]["latitude"] - 40) * 2)
    context_risk = 30 + (data["weather_data"]["precipitation_mm"] * 5)
    
    overall_risk = (behavior_score * 0.4 + (100 - geo_risk) * 0.3 + (100 - context_risk) * 0.3)
    
    st.subheader("📊 Risk Assessment Results")
    
    # Overall risk gauge
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = 100 - overall_risk,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Safety Score"},
        delta = {'reference': 80},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Expert model breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Behavior Score", f"{behavior_score:.1f}", delta=f"{behavior_score-75:.1f}")
    
    with col2:
        st.metric("Geographic Risk", f"{geo_risk:.1f}", delta=f"{50-geo_risk:.1f}")
    
    with col3:
        st.metric("Contextual Risk", f"{context_risk:.1f}", delta=f"{40-context_risk:.1f}")
    
    # Premium calculation
    risk_score = 100 - overall_risk
    if risk_score < 30:
        premium_factor = 0.8
        tier = "Preferred"
    elif risk_score < 60:
        premium_factor = 1.0
        tier = "Standard"
    else:
        premium_factor = 1.3
        tier = "High Risk"
    
    base_premium = 1000
    adjusted_premium = base_premium * premium_factor
    
    st.subheader("💰 Premium Information")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric("Base Premium", f"${base_premium:,.0f}")
    
    with col5:
        st.metric("Adjusted Premium", f"${adjusted_premium:,.0f}", 
                 delta=f"${adjusted_premium - base_premium:,.0f}")
    
    with col6:
        st.metric("Insurance Tier", tier)

def driver_dashboard_page():
    st.header("👤 Driver Dashboard")
    
    # Driver selection
    driver_id = st.selectbox("Select Driver", ["driver_123", "driver_456", "driver_789"])
    
    # Generate mock driver data
    dates = pd.date_range(start='2024-01-01', end='2024-07-31', freq='D')
    mock_data = pd.DataFrame({
        'date': dates,
        'trips': np.random.poisson(2, len(dates)),
        'total_distance': np.random.normal(50, 20, len(dates)).clip(0),
        'avg_speed': np.random.normal(45, 10, len(dates)).clip(0),
        'behavior_score': np.random.normal(80, 10, len(dates)).clip(0, 100),
        'risk_events': np.random.poisson(0.5, len(dates))
    })
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trips = mock_data['trips'].sum()
        st.metric("Total Trips", total_trips, delta=f"+{np.random.randint(1, 10)}")
    
    with col2:
        total_distance = mock_data['total_distance'].sum()
        st.metric("Total Distance (km)", f"{total_distance:,.0f}", delta=f"+{np.random.randint(100, 500)}")
    
    with col3:
        avg_behavior_score = mock_data['behavior_score'].mean()
        st.metric("Avg Behavior Score", f"{avg_behavior_score:.1f}", delta=f"{np.random.uniform(-2, 5):.1f}")
    
    with col4:
        total_risk_events = mock_data['risk_events'].sum()
        st.metric("Risk Events", total_risk_events, delta=f"{np.random.randint(-5, 2)}")
    
    # Behavior score trend
    st.subheader("📈 Behavior Score Trend")
    fig_trend = px.line(mock_data, x='date', y='behavior_score', 
                       title="Behavior Score Over Time")
    fig_trend.add_hline(y=80, line_dash="dash", line_color="red", 
                       annotation_text="Target Score")
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Weekly summary
    st.subheader("📅 Weekly Summary")
    weekly_data = mock_data.set_index('date').resample('W').agg({
        'trips': 'sum',
        'total_distance': 'sum',
        'behavior_score': 'mean',
        'risk_events': 'sum'
    }).reset_index()
    
    st.dataframe(weekly_data.tail(10), use_container_width=True)

def claims_analysis_page():
    st.header("📋 Claims Analysis")
    
    # Driver profile input
    with st.expander("Driver Profile", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=16, max_value=100, value=35)
            gender = st.selectbox("Gender", ["male", "female", "other"])
            area_type = st.selectbox("Area Type", ["urban", "suburban", "rural"])
            annual_mileage = st.number_input("Annual Mileage", min_value=0, value=12000)
        
        with col2:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=700)
            vehicle_type = st.selectbox("Vehicle Type", ["economy", "standard", "luxury"])
            safety_rating = st.number_input("Safety Rating (1-5)", min_value=1, max_value=5, value=4)
            telematics_score = st.number_input("Telematics Score", min_value=0.0, max_value=100.0, value=75.0)
    
    if st.button("Calculate Claims Prediction"):
        # Mock claims calculation
        base_frequency = 0.034  # 3.4% collision frequency
        
        # Age adjustment
        if age < 25:
            frequency_adj = 1.45
        elif age <= 35:
            frequency_adj = 1.15
        elif age <= 55:
            frequency_adj = 0.95
        else:
            frequency_adj = 1.05
        
        # Telematics adjustment
        if telematics_score > 80:
            telematics_adj = 0.82
        else:
            telematics_adj = 1.0
        
        adjusted_frequency = base_frequency * frequency_adj * telematics_adj
        
        # Severity calculation
        base_severity = 6800  # USD
        if vehicle_type == "luxury":
            severity_adj = 1.85
        elif vehicle_type == "economy":
            severity_adj = 0.75
        else:
            severity_adj = 1.0
        
        adjusted_severity = base_severity * severity_adj
        
        expected_annual_cost = adjusted_frequency * adjusted_severity
        
        # Display results
        st.subheader("📊 Claims Prediction Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Claim Frequency", f"{adjusted_frequency:.3f}", 
                     delta=f"{adjusted_frequency - base_frequency:.3f}")
        
        with col2:
            st.metric("Avg Claim Severity", f"${adjusted_severity:,.0f}", 
                     delta=f"${adjusted_severity - base_severity:,.0f}")
        
        with col3:
            st.metric("Expected Annual Cost", f"${expected_annual_cost:,.0f}")
        
        # Savings from telematics
        cost_without_telematics = base_frequency * frequency_adj * base_severity * severity_adj
        savings = cost_without_telematics - expected_annual_cost
        
        if savings > 0:
            st.success(f"💰 Telematics savings: ${savings:,.0f} annually ({savings/cost_without_telematics*100:.1f}%)")
        
        # Risk factors breakdown
        st.subheader("🎯 Risk Factors Analysis")
        
        risk_factors = {
            'Age Factor': frequency_adj,
            'Telematics Factor': telematics_adj,
            'Vehicle Type Factor': severity_adj,
            'Area Risk': 1.1 if area_type == "urban" else 0.9
        }
        
        df_factors = pd.DataFrame(list(risk_factors.items()), columns=['Factor', 'Multiplier'])
        fig_factors = px.bar(df_factors, x='Factor', y='Multiplier', 
                           title="Risk Factor Multipliers")
        fig_factors.add_hline(y=1.0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_factors, use_container_width=True)

def gamification_page():
    st.header("🎮 Gamification Dashboard")
    
    # Driver points and level
    total_points = 3250
    current_level = 3
    level_name = "Safe Driver"
    next_level_points = 5000
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Points", f"{total_points:,}", delta="+125")
    
    with col2:
        st.metric("Current Level", f"{current_level} - {level_name}")
    
    with col3:
        points_to_next = next_level_points - total_points
        st.metric("Points to Next Level", f"{points_to_next:,}")
    
    # Progress bar
    progress = total_points / next_level_points
    st.progress(progress)
    st.write(f"Level {current_level + 1} Progress: {progress*100:.1f}%")
    
    # Recent achievements
    st.subheader("🏆 Recent Achievements")
    
    achievements = [
        {"badge": "🚗", "name": "Safe Driver", "description": "Complete 10 safe trips", "points": 100, "date": "2024-07-30"},
        {"badge": "📱", "name": "Phone-Free Week", "description": "7 days without phone usage", "points": 150, "date": "2024-07-28"},
        {"badge": "🛣️", "name": "Highway Hero", "description": "Safe highway driving", "points": 75, "date": "2024-07-25"}
    ]
    
    for achievement in achievements:
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                st.write(achievement["badge"])
            with col2:
                st.write(f"**{achievement['name']}**")
                st.write(achievement["description"])
            with col3:
                st.write(f"+{achievement['points']} points")
            with col4:
                st.write(achievement["date"])
    
    # Leaderboard
    st.subheader("🏅 Weekly Leaderboard")
    
    leaderboard_data = {
        "Rank": [1, 2, 3, 4, 5],
        "Driver": ["You", "Driver B", "Driver C", "Driver D", "Driver E"],
        "Points": [3250, 3180, 3050, 2920, 2850],
        "Level": ["Safe Driver", "Safe Driver", "Careful Driver", "Careful Driver", "Careful Driver"]
    }
    
    df_leaderboard = pd.DataFrame(leaderboard_data)
    st.dataframe(df_leaderboard, use_container_width=True)
    
    # Points breakdown
    st.subheader("📊 Points Breakdown")
    
    points_sources = {
        "Safe Trips": 1500,
        "Smooth Driving": 800,
        "Speed Compliance": 600,
        "Phone-Free Driving": 350
    }
    
    fig_points = px.pie(values=list(points_sources.values()), 
                       names=list(points_sources.keys()),
                       title="Points by Category")
    st.plotly_chart(fig_points, use_container_width=True)

def geographic_risk_page():
    st.header("🗺️ Geographic Risk Analysis")
    
    # Mock geographic data
    import numpy as np
    
    # Generate sample location data
    np.random.seed(42)
    n_points = 100
    
    # Create sample data around major cities
    cities = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060, "risk": 65},
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "risk": 55},
        {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "risk": 60},
        {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "risk": 50},
        {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740, "risk": 45}
    ]
    
    map_data = []
    for city in cities:
        for _ in range(20):
            lat = city["lat"] + np.random.normal(0, 0.1)
            lon = city["lon"] + np.random.normal(0, 0.1)
            risk = max(0, min(100, city["risk"] + np.random.normal(0, 10)))
            map_data.append({
                "latitude": lat,
                "longitude": lon,
                "risk_score": risk,
                "city": city["name"]
            })
    
    df_map = pd.DataFrame(map_data)
    
    # Risk map
    st.subheader("🎯 Risk Heat Map")
    
    fig_map = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        color="risk_score",
        size="risk_score",
        hover_name="city",
        hover_data={"risk_score": True},
        color_continuous_scale="RdYlGn_r",
        size_max=15,
        zoom=3,
        height=600
    )
    
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Risk statistics by city
    st.subheader("📊 Risk Statistics by City")
    
    city_stats = df_map.groupby('city').agg({
        'risk_score': ['mean', 'std', 'count']
    }).round(1)
    city_stats.columns = ['Average Risk', 'Risk Std Dev', 'Data Points']
    city_stats = city_stats.sort_values('Average Risk', ascending=False)
    
    st.dataframe(city_stats, use_container_width=True)
    
    # Risk distribution
    st.subheader("📈 Risk Score Distribution")
    
    fig_hist = px.histogram(df_map, x="risk_score", nbins=20, 
                           title="Geographic Risk Score Distribution")
    fig_hist.add_vline(x=df_map['risk_score'].mean(), line_dash="dash", 
                      line_color="red", annotation_text="Average")
    st.plotly_chart(fig_hist, use_container_width=True)

if __name__ == "__main__":
    # Import required libraries
    import numpy as np
    main()
