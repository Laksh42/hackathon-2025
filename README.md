# Wells Fargo Financial Recommendation System

A hyper-personalized financial product recommendation system built for Wells Fargo customers, featuring an interactive chat interface, an "understander" module for user profiling, and a "recommender" engine for personalized product suggestions.

## Project Overview

This system provides a seamless experience for Wells Fargo customers to receive tailored financial product recommendations based on their financial situation, goals, and risk tolerance. The application is built with:

- **Frontend**: React with Material UI
- **Backend API**: Flask
- **Understander Service**: Python service for analyzing user profiles
- **Recommender Service**: Python service for generating personalized recommendations

## Features

- Interactive chat-based onboarding flow
- Financial profile analysis
- Personalized product recommendations
- Relevant financial news integration
- Responsive and modern UI

## Project Structure

```
hackathon-2025/
├── frontend/          # React application
├── backend/           # Flask API server
├── understander/      # User profile analysis service
├── recommender/       # Recommendation generation service
└── docker-compose.yml # Service orchestration
```

## Getting Started

### Prerequisites

- Node.js (v14+)
- Python 3.8+
- Docker and Docker Compose (optional, for containerized deployment)

### Local Development Setup

1. **Backend API**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Understander Service**:
   ```bash
   cd understander
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python understander.py
   ```

3. **Recommender Service**:
   ```bash
   cd recommender
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python recommender.py
   ```

4. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

The application will be accessible at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5050
- Understander Service: http://localhost:5051
- Recommender Service: http://localhost:5052

## Usage

1. Navigate to the main page
2. Complete the financial profile questionnaire
3. View your personalized product recommendations
4. Explore related financial news and product details

## Demo Mode

If you don't want to run all services, you can use the "Use sample data" checkbox in the UI to run in demo mode with mock data.