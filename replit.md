# Overview

This is a Streamlit-based web application for discovering and searching sports venues in Taipei City. The application provides a comprehensive search engine with personalized recommendations, interactive map visualization, and user preference management. Users can find suitable sports facilities through various filtering options including sport type, district, price range, and facilities.

# User Preferences

Preferred communication style: Simple, everyday language.

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

The application uses a flexible data storage approach without a fixed database:
- Supports JSON and CSV file formats for venue data
- Environment variable-based configuration for data sources
- Pandas DataFrame structures for in-memory data manipulation
- Session state for user preference persistence during app usage

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