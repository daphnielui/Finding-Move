# Overview

This is a Streamlit-based web application for discovering and searching sports venues in Taipei City. The application provides a comprehensive search engine with personalized recommendations, interactive map visualization, and user preference management. Users can find suitable sports facilities through various filtering options including sport type, district, price range, and facilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

**September 15, 2025**: Successfully implemented top-right location selector with auto-positioning:
- Added fixed position location selector in top-right corner with gray theme design
- Integrated all 12 Taipei districts dropdown using Streamlit native selectbox component
- Implemented HTML5 geolocation API with distance calculation to nearest district
- Added real-time weather data updates based on selected district
- Fixed pandas compatibility issues (na_last → na_position in sort_values)
- Resolved accessibility warnings by adding proper selectbox labels
- Enhanced URL parameter management for state persistence across page reloads
- Complete end-to-end testing validation with Playwright

**September 13, 2025**: Completed comprehensive sports venue search engine with following features:
- PostgreSQL database integration with venues, bookings, reviews, and user tables
- Real-time booking system with availability checking and conflict detection
- User review and rating system with administrative moderation dashboard
- Advanced machine learning recommendation algorithms (ML-based, clustering, content-based similarity)
- Comprehensive venue comparison feature with charts, statistics, and analysis
- Venue detail pages with complete information, booking forms, and review sections
- Security improvements: removed hardcoded passwords, using environment variables
- Enhanced error handling and data validation throughout the application

# System Architecture

## Frontend Architecture
The application uses Streamlit as the primary web framework with a multi-page architecture:
- **Main App (app.py)**: Entry point with user preference settings and overall configuration
- **Search Page**: Advanced filtering and search functionality for venues
- **Map View Page**: Interactive map visualization using Folium integration

The frontend follows a session state management pattern to maintain user preferences and application state across different pages. The layout uses a sidebar for filters and controls with a wide main content area.

## Backend Architecture
The system is built with a modular utility-based architecture:

### Core Components
- **DataManager**: Handles all data operations including loading, filtering, and venue retrieval
- **RecommendationEngine**: Implements multiple recommendation algorithms using content-based filtering and TF-IDF vectorization
- **MapUtils**: Provides geographical utilities and coordinate calculations for map functionality

### Data Processing Layer
The DataManager supports flexible data loading from multiple sources:
- JSON files for structured venue data
- CSV files for tabular data
- REST API endpoints for dynamic data fetching
- Environment variable configuration for data source specification

### Recommendation System
The RecommendationEngine implements sophisticated recommendation algorithms:
- Content-based filtering using venue features
- User preference matching with weighted scoring
- Diversity and novelty factors to avoid filter bubbles
- Feedback integration for continuous learning

## Data Storage

**PostgreSQL Database Integration (Updated September 2025)**

The application now uses a comprehensive PostgreSQL database with the following tables:
- **venues**: Stores all venue information including name, location, facilities, pricing
- **reviews**: User-generated reviews and ratings with moderation status
- **bookings**: Real-time booking records with availability tracking
- **user_preferences**: User preference data for personalized recommendations

Key features:
- Real-time availability checking with conflict detection
- ACID-compliant booking transactions
- Review moderation workflow with admin dashboard
- Secure environment-based database configuration

## Geographic Features

Map functionality is built around Taipei City's district system:
- Predefined district center coordinates for all Taipei districts
- Color-coded markers for different sport types
- Boundary calculations for map viewport management
- Integration with Folium for interactive map rendering

# External Dependencies

## Core Web Framework
- **Streamlit**: Main web application framework for UI and user interaction
- **streamlit-folium**: Integration package for embedding Folium maps in Streamlit

## Data Processing
- **Pandas**: Primary data manipulation and analysis library
- **NumPy**: Numerical computing support for calculations and array operations

## Machine Learning & Recommendations
- **scikit-learn**: Machine learning utilities including TfidfVectorizer and cosine similarity calculations for content-based recommendations

## Visualization & Mapping
- **Folium**: Interactive map generation and visualization library for geographic data display

## Data Sources
- **Configurable data sources**: Support for JSON files, CSV files, or REST API endpoints
- **Environment variables**: VENUES_DATA_SOURCE for flexible data source configuration
- **HTTP requests**: Optional integration for API-based data fetching

The architecture is designed to be flexible and extensible, allowing for easy integration of additional data sources, recommendation algorithms, and visualization features.