import streamlit as st
import pandas as pd
import numpy as np
import requests
import cohere
import folium
from streamlit_folium import st_folium

# ================= CONFIG =================
st.set_page_config(
    page_title="Aquix",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= API KEYS =================
COHERE_API_KEY = "d9ea3N70agpIs4DqoT9Xc61WU8rojtHVocqInAnq"
WEATHER_API_KEY = "f70c404179540d94a627483bb8997793"

co = cohere.Client(COHERE_API_KEY)

# ================= STYLING =================
st.markdown("""
    <style>
        .main {background-color: #f5f7fa;}
        .stMetric {text-align: center;}
        .css-1d391kg {background-color: #ffffff;}
    </style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("Aquix💧")
page = st.sidebar.radio("Navigation", [
    "🏠 Overview",
    "📊 Demand Prediction",
    "🚨 Leak Detection",
    "🌧️ Weather & Crisis",
    "🗺️ Smart Map",
    "🧑‍🌾 Farmer Insights",
    "🔧 Services",
    "💬 AI Chatbot"
])

# ================= OVERVIEW =================
if page == "🏠 Overview":
    st.title("Aquix 💧")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💧 Water Usage", "1200 L", "+5%")
    col2.metric("🚨 Active Leaks", "3", "-1")
    col3.metric("🌧️ Rainfall", "45 mm", "+10%")
    col4.metric("⚠️ Risk Level", "Medium")

    st.markdown("---")
    st.subheader("📊 System Summary")

    st.line_chart(np.random.randn(50, 3))

# ================= DEMAND =================
elif page == "📊 Demand Prediction":
    st.title("📊 Water Demand Prediction")

    st.write("Predict water usage based on inputs")

    temp = st.slider("Temperature", 20, 45)
    humidity = st.slider("Humidity", 10, 100)

    if st.button("Predict Demand"):
        prediction = temp * 10 + humidity * 2  # Replace with your model
        st.success(f"Predicted Demand: {prediction:.2f} liters")

# ================= LEAK =================
elif page == "🚨 Leak Detection":
    st.title("🚨 Leak Detection")

    value = st.slider("Sensor Reading", 0, 100)

    if value > 70:
        st.error("🚨 Leak Detected!")
    else:
        st.success("✅ Normal Flow")

# ================= WEATHER =================
elif page == "🌧️ Weather & Crisis":
    st.title("🌧️ Weather Insights")

    city = st.text_input("Enter City", "Bangalore")

    if st.button("Get Weather"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("main"):
            st.metric("Temperature", f"{data['main']['temp']} °C")
            st.metric("Humidity", f"{data['main']['humidity']} %")

            if data['main']['temp'] > 35:
                st.warning("⚠️ High water demand expected")

# ================= MAP =================
elif page == "🗺️ Smart Map":
    st.title("🗺️ Water Intelligence Map")

    m = folium.Map(location=[12.97, 77.59], zoom_start=10)

    folium.Marker([12.97, 77.59], tooltip="Normal Zone").add_to(m)
    folium.Marker([12.95, 77.60], tooltip="High Demand Zone", icon=folium.Icon(color="red")).add_to(m)

    st_folium(m, width=1000)

# ================= FARMER =================
elif page == "🧑‍🌾 Farmer Insights":
    st.title("🧑‍🌾 Smart Irrigation")

    crop = st.selectbox("Select Crop", ["Rice", "Wheat", "Maize"])

    if st.button("Get Recommendation"):
        st.success(f"💧 Recommended irrigation for {crop}: 500L/day")

# ================= SERVICES =================
elif page == "🔧 Services":
    st.title("🔧 Water Services")

    service = st.selectbox("Select Service", ["Plumber", "Water Tanker"])

    if st.button("Book Service"):
        st.success(f"{service} booked successfully!")

# ================= CHATBOT =================
elif page == "💬 AI Chatbot":
    st.title("💬 AquaSphere Assistant")

    user_input = st.text_input("Ask your question")

    if st.button("Ask"):
        if not user_input.strip():
            st.warning("Please enter a question.")
        else:
            try:
                response = co.chat(
                    model="command-a-03-2025",
                    message=user_input,
                    max_tokens=100
                )
                st.write(response.text)
            except Exception as error:
                st.error(f"Chatbot error: {error}")
