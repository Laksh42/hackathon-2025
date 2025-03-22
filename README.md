# Wells Fargo Financial Assistant

A hyper-personalized recommendation system for Wells Fargo bank customers. This project consists of a chat interface that engages users, an "understander" module that processes user input, and a "recommender" module that generates personalized financial product recommendations.

## Project Structure

The application is divided into three main components:

1. **Frontend**: React-based user interface with chat functionality and recommendation display
2. **Backend API**: Flask-based service that coordinates between the frontend and other microservices
3. **Understander Service**: Processes user conversations to extract relevant financial information
4. **Recommender Service**: Generates personalized product recommendations based on user profiles

## Features

- Interactive chat interface for gathering user financial information
- Personalized financial product recommendations
- Relevant news articles related to financial markets
- Error handling with fallback to mock data
- Modern, responsive UI using Material-UI components

## Tech Stack

- **Frontend**: React, Material-UI, React Router
- **Backend**: Flask/FastAPI
- **AI Recommendation Engine**: Custom vector-based matching algorithm
- **Containerization**: Docker & Docker Compose

## Local Development Setup

### Prerequisites

- Node.js (v16+)
- Python 3.8+
- Docker and Docker Compose (optional)

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend API will run on `http://localhost:5050`

### Understander Service

```bash
cd understander
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python understander.py
```

The understander service will run on `http://localhost:5051`

### Recommender Service

```bash
cd recommender
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python recommender.py
```

The recommender service will run on `http://localhost:5052`

## Docker Setup

To run all services with Docker Compose:

```bash
docker-compose up
```

## Project Structure

```
├── backend/            # Flask backend API
├── frontend/           # React frontend
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── ChatInterface.js
│       ├── RecommendationDisplay.js
│       ├── RecommendationsPage.js
│       └── mockData.js
├── understander/       # Understander service
└── recommender/        # Recommender service
```

## Troubleshooting

- If you encounter connection errors, make sure all services are running and accessible on their respective ports
- For local development, ensure services are using localhost URLs instead of container names
- If API requests fail, try using mock data by typing "mock" in the final chat question

## Future Enhancements

- Authentication and user account integration
- Session persistence for chat history
- Product detail pages with application process
- More sophisticated AI reasoning for personalized insights
- Expanded product database and recommendation algorithm