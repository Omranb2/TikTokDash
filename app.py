import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from urllib.parse import urlparse
import os
from tiktok_scraper import TikTokScraper

# Page configuration
st.set_page_config(
    page_title="TikTok Analytics Dashboard",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize the scraper
@st.cache_resource
def init_scraper():
    return TikTokScraper()

def validate_tiktok_url(url):
    """Validate if the provided URL is a valid TikTok profile URL"""
    if not url:
        return False, "Please enter a TikTok URL"
    
    # Basic URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)
        
        if "tiktok.com" not in parsed.netloc.lower():
            return False, "Please enter a valid TikTok URL"
        
        # Check if it's a profile URL (contains @username)
        if "@" not in url and "/user/" not in url:
            return False, "Please enter a valid TikTok profile URL (should contain @username)"
        
        return True, url
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"

def extract_username_from_url(url):
    """Extract username from TikTok URL"""
    try:
        if "@" in url:
            # Extract @username from URL
            username = url.split("@")[1].split("/")[0].split("?")[0]
            return username
        elif "/user/" in url:
            # Extract from /user/ format
            username = url.split("/user/")[1].split("/")[0].split("?")[0]
            return username
        return None
    except:
        return None

def display_analytics_dashboard(profile_data):
    """Enhanced analytics dashboard matching the provided design"""
    
    # Header with title and branding
    st.markdown("## 📊 TikTok Analytics Dashboard")
    
    # Main layout - Left sidebar and right content
    left_col, right_col = st.columns([1, 3])
    
    with left_col:
        # Profile picture and basic info
        avatar_url = profile_data.get('avatar_url')
        if avatar_url and avatar_url != 'No profile_pic found':
            st.image(avatar_url, width=200, caption="")
        else:
            st.markdown("📸 **Profile Picture**<br>Not available", unsafe_allow_html=True)
        
        # Profile name and username
        st.markdown(f"### {profile_data.get('display_name', 'N/A')}")
        st.markdown(f"**@{profile_data.get('username', 'N/A')}**")
        
        # Biography section
        if profile_data.get('bio'):
            st.markdown("**📝 Biography**")
            st.write(profile_data['bio'])
        
        # Account Status
        st.markdown("**👤 Account Status**")
        st.write(f"✅ Verified: {profile_data.get('verified_verdict', 'No')}")
    
    with right_col:
        # Profile Overview Section
        st.markdown("### ✅ Profile Overview")
        
        # Metrics in horizontal layout
        overview_html = f"""
        <div style="display: flex; justify-content: space-between; background: rgba(255, 255, 255, 0.1); 
                    border-radius: 12px; padding: 20px; margin: 15px 0; backdrop-filter: blur(10px);">
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">👥 Followers</div>
                <div style="font-size: 18px; font-weight: bold;">{format_number(profile_data.get('follower_count', 0))}</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">🔗 Following</div>
                <div style="font-size: 18px; font-weight: bold;">{format_number(profile_data.get('following_count', 0))}</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">📊 Avg Likes/Video</div>
                <div style="font-size: 18px; font-weight: bold;">{format_number(int(profile_data.get('avg_likes_per_video', 0)))}</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">🎥 Videos</div>
                <div style="font-size: 18px; font-weight: bold;">{format_number(profile_data.get('video_count', 0))}</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">❤️ Total Likes</div>
                <div style="font-size: 18px; font-weight: bold;">{format_number(profile_data.get('heart_count', 0))}</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 12px; opacity: 0.8; margin-bottom: 5px;">📈 Engagement Rate</div>
                <div style="font-size: 18px; font-weight: bold;">{profile_data.get('engagement_rate', 0):.2f}%</div>
            </div>
        </div>
        """
        st.markdown(overview_html, unsafe_allow_html=True)
        
        # Performance Section
        st.markdown("### 🎯 Performance")
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            # Influencer Score Bar
            influencer_score = profile_data.get('influencer_score', 0)
            influencer_bar = create_performance_bar("Influence", influencer_score, "influencer")
            st.markdown(influencer_bar, unsafe_allow_html=True)
        
        with perf_col2:
            # Credibility Bar (now uses new combined credibility score)
            credibility_score = profile_data.get('credibility_score', 0)
            credibility_bar = create_performance_bar("Credibility", credibility_score, "credibility")
            st.markdown(credibility_bar, unsafe_allow_html=True)
    
    # Social Links Section
    if profile_data.get('social_links'):
        st.markdown("### 🔗 Social Media Links")
        social_links = profile_data['social_links']
        if social_links:
            for link in social_links:
                st.write(f"• {link}")
        else:
            st.write("No social media links found in bio")
    
    # Recent Videos (if available)
    if 'recent_videos' in profile_data and profile_data['recent_videos']:
        st.markdown("### 🎬 Recent Videos")
        for i, video in enumerate(profile_data['recent_videos'][:5]):  # Show top 5
            with st.expander(f"Video {i+1}: {video.get('description', 'No description')[:50]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Views:** {format_number(video.get('view_count', 0))}")
                    st.write(f"**Likes:** {format_number(video.get('like_count', 0))}")
                with col2:
                    st.write(f"**Comments:** {format_number(video.get('comment_count', 0))}")
                    st.write(f"**Shares:** {format_number(video.get('share_count', 0))}")

def create_performance_bar(title, score, score_type="influencer"):
    """Create horizontal performance bar visualization"""
    
    # Determine score level and color based on new classification system
    if score_type == "influencer":
        if score < 30:
            level = "Low Influence"
            color = "#ef4444"
            width = "25%"
        elif score < 60:
            level = "Average Influence" 
            color = "#f59e0b"
            width = "50%"
        elif score < 80:
            level = "Strong Influence"
            color = "#10b981"
            width = "75%"
        else:
            level = "Top-Tier Influence"
            color = "#059669"
            width = "100%"
    else:  # credibility
        if score < 60:
            level = "Poor Credibility"
            color = "#ef4444"
            width = "30%"
        elif score < 80:
            level = "Medium Credibility"
            color = "#f59e0b"
            width = "65%"
        else:
            level = "High Credibility"
            color = "#10b981"
            width = "100%"
    
    # Set labels based on score type
    if score_type == "influencer":
        labels = ["Low", "Average", "Strong", "Top-Tier"]
    else:
        labels = ["Poor", "Medium", "High", "High"]
    
    bar_html = f"""
    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin: 10px 0; backdrop-filter: blur(10px);">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="width: 12px; height: 12px; background: {color}; border-radius: 50%; margin-right: 10px;"></div>
            <span style="color: white; font-weight: 600; font-size: 16px;">{title}: {score}</span>
        </div>
        <div style="background: rgba(255, 255, 255, 0.2); border-radius: 8px; height: 24px; position: relative; overflow: hidden;">
            <div style="display: flex; height: 100%; position: absolute; width: 100%; z-index: 1;">
                <div style="flex: 1; border-right: 1px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: 500;">{labels[0]}</div>
                <div style="flex: 1; border-right: 1px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: 500;">{labels[1]}</div>
                <div style="flex: 1; border-right: 1px solid rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: 500;">{labels[2]}</div>
                <div style="flex: 1; display: flex; align-items: center; justify-content: center; font-size: 9px; color: white; font-weight: 500;">{labels[3]}</div>
            </div>
            <div style="background: linear-gradient(90deg, {color}, {color}); height: 100%; width: {width}; border-radius: 8px; position: relative; z-index: 2; transition: width 0.8s ease;"></div>
        </div>
        <div style="text-align: center; margin-top: 10px; color: white; font-weight: 600; font-size: 14px;">{level}</div>
    </div>
    """
    return bar_html


def format_number(num):
    """Format large numbers with K, M, B suffixes"""
    try:
        num = int(num)
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return str(num)
    except:
        return "0"

def show_login_page():
    """Display the login/input page"""
    # Main container with custom styling
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Title and description
    st.markdown('<h1 class="main-title">Get TikTok Profile Info</h1>', unsafe_allow_html=True)
    
    # Create the form
    with st.form("tiktok_form", clear_on_submit=False):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # Full Name input
        full_name = st.text_input(
            "Full Name",
            placeholder="e.g. Cristiano Ronaldo",
            help="Enter the full name of the TikTok user"
        )
        
        # TikTok URL input
        tiktok_url = st.text_input(
            "TikTok URL",
            placeholder="https://www.tiktok.com/@c.ronaldoxd7",
            help="Enter the complete TikTok profile URL"
        )
        
        # Submit button
        submitted = st.form_submit_button("Submit", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process form submission
    if submitted:
        if not full_name:
            st.error("⚠️ Please enter a full name")
            return
        
        # Validate TikTok URL
        is_valid, result = validate_tiktok_url(tiktok_url)
        if not is_valid:
            st.error(f"⚠️ {result}")
            return
        
        # Store data in session state and redirect to dashboard
        st.session_state.full_name = full_name
        st.session_state.tiktok_url = result
        st.session_state.page = "dashboard"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem;'>"
        "TikTok Analytics Dashboard | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

def show_dashboard_page():
    """Display the analytics dashboard page"""
    # Initialize scraper
    scraper = init_scraper()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Back to login button
    if st.button("← Back to Search", type="secondary"):
        st.session_state.page = "login"
        st.rerun()
    
    # Show loading spinner and process data
    full_name = st.session_state.get('full_name', '')
    tiktok_url = st.session_state.get('tiktok_url', '')
    
    with st.spinner(f"🔍 Analyzing TikTok profile for {full_name}..."):
        try:
            # Extract username
            username = extract_username_from_url(tiktok_url)
            if not username:
                st.error("❌ Could not extract username from URL")
                return
            
            # Scrape profile data
            profile_data = scraper.get_profile_data(username)
            
            if profile_data:
                # Add full name to profile data
                profile_data['full_name'] = full_name
                
                # Display success message
                st.success(f"✅ Successfully retrieved data for {full_name}")
                
                # Display analytics dashboard
                display_analytics_dashboard(profile_data)
            else:
                st.error("❌ Failed to retrieve profile data. Please check the URL and try again.")
                st.info("💡 Make sure the profile is public and the URL is correct.")
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please try again with a different URL or check your internet connection.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Load custom CSS
    load_css()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    # Display appropriate page based on session state
    if st.session_state.page == "login":
        show_login_page()
    elif st.session_state.page == "dashboard":
        show_dashboard_page()

if __name__ == "__main__":
    main()
