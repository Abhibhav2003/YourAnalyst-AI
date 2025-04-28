import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as plt
import requests
from streamlit_lottie import st_lottie
from datetime import datetime

# Set the page configuration
st.set_page_config(
    page_title="YourAnalyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Main Styles */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Title Styles */
    .hero-title {
        font-size: 3.5em;
        font-weight: 700;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #2c3e50, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.5em;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Card Styles */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #3498db;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .feature-card h3 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.2em;
    }
    
    .feature-card p {
        color: #666;
        line-height: 1.6;
    }
    
    /* Stats Card */
    .stats-card {
        background: white;
        color: #2c3e50;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 4px solid #3498db;
    }
    
    .stats-card h2 {
        font-size: 2.5em;
        color: #3498db;
        margin: 10px 0;
    }
    
    .stats-card h3 {
        font-size: 1.2em;
        color: #2c3e50;
    }
    
    /* Section Titles */
    .section-title {
        font-size: 2.5em;
        color: #2c3e50;
        text-align: center;
        margin: 60px 0 40px 0;
        padding-bottom: 20px;
        position: relative;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .section-title:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #3498db, #2c3e50);
        border-radius: 4px;
        margin-top: 25px;
    }
    
    /* CTA Button */
    .cta-button {
        background: linear-gradient(45deg, #3498db, #2c3e50);
        color: white;
        padding: 12px 30px;
        border-radius: 25px;
        border: none;
        font-size: 1.2em;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        display: block;
        margin: 20px auto;
        width: fit-content;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Benefits List */
    .benefits-list {
        list-style: none;
        padding: 0;
        margin: 20px 0;
    }
    
    .benefits-list li {
        padding: 10px 0;
        color: #2c3e50;
        display: flex;
        align-items: center;
    }
    
    .benefits-list li:before {
        content: '✓';
        color: #3498db;
        margin-right: 10px;
        font-weight: bold;
    }

    .feature-title {
        color: #2c3e50;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 15px;
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 15px;
        color: #3498db;
    }

    .feature-card {
        background: #ffffff;
        border-radius: 15px;
        padding: 30px;
        height: 350px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: start;
        border: 1px solid #e1e8ed;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(52, 152, 219, 0.2);
    }

    .feature-description {
        color: #596275;
        font-size: 16px;
        line-height: 1.6;
    }

    .features-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        padding: 20px 0;
    }

    .section-title {
        color: #2c3e50;
        font-size: 2.5em;
        font-weight: 700;
        text-align: center;
        margin: 60px 0 40px 0;
        padding-bottom: 20px;
        position: relative;
        letter-spacing: 0.5px;
    }

    .section-title:after {
        content: "";
        display: block;
        width: 80px;
        height: 4px;
        background: #3498db;
        margin: 25px auto 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load animations
analyzing_animation = load_lottie_url("https://lottie.host/46d346ba-c57b-452c-ac6f-2b4a34d4d87d/YUWkpeSAFk.json")

# Hero Section
st.markdown('<h1 class="hero-title">Welcome to YourAnalyst</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Transform Your Data into Actionable Insights</p>', unsafe_allow_html=True)

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st_lottie(analyzing_animation, height=300, key="analyzing")

with col2:
    st.markdown("""
    <div>
        <h4>Your Data Analysis Partner</h4>
        <ul class="benefits-list">
            <li style = "color: #ffff;">Advanced Analytics Tools</li>
            <li style = "color: #ffff;">Interactive Visualizations</li>
            <li style = "color: #ffff;">Real-time Insights</li>
            <li style = "color: #ffff;">User-friendly Interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown('<h2 class="section-title">Key Features</h2>', unsafe_allow_html=True)
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📤 Data Import</h3>
        <p>Seamlessly upload and process data from multiple sources including CSV, Excel, and databases. Automatic data validation and cleaning ensure quality analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>🔍 Smart Analysis</h3>
        <p>Leverage advanced statistical methods and machine learning algorithms for deep insights. Automated pattern recognition and trend analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Dynamic Visualizations</h3>
        <p>Create stunning interactive charts and dashboards. Customizable plots and real-time updates make your data come alive.</p>
    </div>
    """, unsafe_allow_html=True)

# Why Choose Us Section
st.markdown('<h2 class="section-title">Why Choose YourAnalyst?</h2>', unsafe_allow_html=True)
col9, col10 = st.columns(2)

with col9:
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Powerful Yet Simple</h3>
        <ul class="benefits-list">
            <li>Intuitive user interface</li>
            <li>No coding required</li>
            <li>Quick learning curve</li>
            <li>Real-time results</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col10:
    st.markdown("""
    <div class="feature-card">
        <h3>💡 Smart Features</h3>
        <ul class="benefits-list">
            <li>Automated insights</li>
            <li>Predictive analytics</li>
            <li>Custom reporting</li>
            <li>Data security</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Call to Action
st.markdown("""
<div style='text-align: center; margin: 50px 0;'>
    <h2 style='color: #2c3e50; margin-bottom: 20px;'>Ready to Transform Your Data?</h2>
    <p style='color: #666; margin-bottom: 30px;'>Start your analysis journey today!</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <p style='color: #666; margin-bottom: 10px;'>© 2024 YourAnalyst. All rights reserved.</p>
    <p style='color: #666;'>Made with ❤️ for data enthusiasts</p>
</div>
""", unsafe_allow_html=True)
