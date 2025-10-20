# TikTok Analytics Dashboard

## Overview

This is a Streamlit-based web application that provides analytics for TikTok profiles. The application allows users to input TikTok profile URLs and retrieve analytics data using web scraping techniques. It features a modern, glassmorphism-styled user interface with a gradient background and focuses on delivering TikTok profile insights through data extraction and visualization.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for rapid web application development
- **Styling**: Custom CSS with glassmorphism design using backdrop filters and gradient backgrounds
- **Layout**: Centered layout with collapsed sidebar for clean user experience
- **Fonts**: Google Fonts (Inter) for modern typography

### Backend Architecture
- **Core Logic**: Python-based application with modular scraper component
- **Data Processing**: BeautifulSoup for HTML parsing and requests for HTTP operations
- **Caching**: Streamlit's `@st.cache_resource` decorator for scraper instance optimization
- **URL Validation**: Built-in validation system for TikTok profile URLs

### Data Extraction Strategy
- **Primary Method**: Custom TikTokScraper class with multiple fallback approaches
- **Mobile API Approach**: Attempts to use mobile endpoints for less restricted access
- **Web Scraping Fallback**: HTML parsing as secondary data extraction method
- **Session Management**: Persistent session with realistic browser headers for anti-detection

### Application Structure
- **Main Application**: `app.py` - Streamlit interface and user interaction logic
- **Scraper Module**: `tiktok_scraper.py` - Data extraction and API interaction
- **Styling**: `style.css` - Custom UI styling with modern design elements

### Data Flow
1. User inputs TikTok profile URL
2. URL validation and normalization
3. Username extraction from URL
4. Multi-approach data scraping (mobile API → web scraping)
5. Data processing and presentation

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **requests**: HTTP library for making API calls and web requests
- **beautifulsoup4**: HTML/XML parsing for web scraping
- **pandas**: Data manipulation and analysis (imported but usage not shown in provided code)
- **re**: Regular expressions for text processing
- **urllib.parse**: URL parsing and validation

### Web Services
- **TikTok Mobile API**: Primary data source through mobile endpoints
- **TikTok Web Platform**: Fallback scraping target for profile data
- **Google Fonts**: External font loading for Inter font family

### Browser Simulation
- **User-Agent Spoofing**: Chrome browser simulation for anti-detection
- **Header Management**: Realistic browser headers to mimic legitimate requests
- **Session Persistence**: Maintained session state for consistent scraping