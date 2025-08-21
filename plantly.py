import streamlit as st
import numpy as np
from PIL import Image
import requests
import base64
import google.generativeai as genai

# 🔐 Google Gemini API setup (HARDCODED for testing only)
GOOGLE_API_KEY = "AIzaSyB7FnTT7mkSoxe-yqqMjZQ1QVNLkamfMOE"         # 👈 Replace with your Gemini API key
UNSPLASH_ACCESS_KEY = "sedpZQEtU0fdAPlHZqIjucHGjFj4JDbaLgYajhPWNqY"  # 👈 Replace with your Unsplash key

genai.configure(api_key=GOOGLE_API_KEY)

# ✅ Use the latest Gemini 2.0 Flash model
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Unsplash API setup
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# ----------------- Utility Functions -----------------

# Fetch plant image from Unsplash
def fetch_plant_image(plant_name):
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {"query": f"{plant_name} plant", "per_page": 1}
    response = requests.get(UNSPLASH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    return None

# Generate plant care guide using Gemini
def generate_plant_guide(plant_name):
    msg = (
        f"Generate a concise, practical care guide for the plant '{plant_name}'. "
        f"Include:\n"
        f"1. Watering needs\n"
        f"2. Fertilizer type (if required)\n"
        f"3. Soil type & pH\n"
        f"4. Optimal temperature range\n"
        f"5. Pruning requirements\n"
        f"6. Useful plant parts\n"
        f"7. Any extra care tips"
    )
    response = chat.send_message(msg)
    return response.text.strip()

# Recommend plants based on preferences
def recommend_plants(plant_type, growth_habit, growth_place, maintenance_level, sunlight):
    msg = (
        f"Recommend 3 home gardening plants based on these preferences. "
        f"Return ONLY the names separated by line breaks, no numbering or descriptions. "
        f"Focus on common and known plants in India.\n\n"
        f"Plant Type: {plant_type}\n"
        f"Growth Habit: {growth_habit}\n"
        f"Growth Place: {growth_place}\n"
        f"Maintenance Level: {maintenance_level}\n"
        f"Sunlight Requirement: {sunlight}"
    )
    response = chat.send_message(msg)
    plant_names = [p.strip() for p in response.text.split("\n") if p.strip()]
    return plant_names[:3]

# Set background image
def set_background_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ----------------- Streamlit UI -----------------

# Session state
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_plant' not in st.session_state:
    st.session_state.selected_plant = None
if 'query_response' not in st.session_state:
    st.session_state.query_response = None

# Background
set_background_image("342a4a4b-d389-4862-907c-44d1f1de5239.jpg")

# Title
st.markdown(
    "<h1 style='text-align: center; color: Black; font-weight: bold;'>🌿 Home Gardening AI Assistant 🌼</h1>",
    unsafe_allow_html=True
)

# Sidebar: Chatbot
with st.sidebar:
    st.markdown("<h2 style='font-weight: bold;'>Ask Me Anything About Plants 🌻</h2>", unsafe_allow_html=True)
    user_query = st.text_input("Enter your query here:")
    if st.button("Ask"):
        try:
            st.session_state.query_response = chat.send_message(user_query).text
        except Exception as e:
            st.session_state.query_response = f"⚠️ Error: {e}"
    if st.session_state.query_response:
        st.markdown("<b>🤖 Chatbot Response:</b>", unsafe_allow_html=True)
        st.markdown(f"<b>{st.session_state.query_response}</b>", unsafe_allow_html=True)

# Main: Plant Recommendation Tool
st.markdown("<h2 style='font-weight: bold;'>Discover Your Perfect Plant 🌱</h2>", unsafe_allow_html=True)
plant_type = st.selectbox("Select Plant Type", ["Ornamental", "Vegetable", "Fruit", "Flower", "Medicinal"])
growth_habit = st.selectbox("Select Growth Habit", ["Bushy", "Herb", "Upright", "Climber"])
growth_place = st.selectbox("Select Growth Place", ["Pot", "Ground"])
maintenance_level = st.selectbox("Select Maintenance Level", ["Low", "Moderate", "High"])
sunlight = st.selectbox("Select Sunlight Requirement", ["Low", "Moderate", "High"])

if st.button("Find Your Green Companions 🌳"):
    st.session_state.recommendations = recommend_plants(
        plant_type, growth_habit, growth_place, maintenance_level, sunlight
    )
    st.session_state.selected_plant = None

# Show recommendations
if st.session_state.recommendations:
    st.markdown("<b>🌟 Here are some green gems for you! 🌟</b>", unsafe_allow_html=True)
    for plant in st.session_state.recommendations:
        st.markdown(f"<b>{plant}</b>", unsafe_allow_html=True)
    
    selected_plant = st.selectbox("Select a Plant for Care Guide", st.session_state.recommendations)
    
    if st.button("Generate Care Guide 🌿"):
        st.session_state.selected_plant = selected_plant

# Show care guide & image
if st.session_state.selected_plant:
    image_url = fetch_plant_image(st.session_state.selected_plant)
    if image_url:
        st.image(image_url, caption=st.session_state.selected_plant)

    try:
        care_guide = generate_plant_guide(st.session_state.selected_plant)
        st.markdown(
            f"<h3 style='font-weight: bold;'>🌱 Care Guide for {st.session_state.selected_plant}:</h3>",
            unsafe_allow_html=True
        )
        st.markdown(f"<b>{care_guide}</b>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error generating guide: {e}")
