# Deployment Guide for Financial Assistant Application

This guide covers deployment options for the Financial Assistant Application.

## Local Deployment

### Prerequisites
- Python 3.9+ 
- pip (Python package manager)
- Bash-compatible shell

### Option 1: Automated Setup (Recommended)

1. Run the startup script:
   ```bash
   ./startup.sh
   ```

   This script will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Start all services in separate terminal windows

2. Access the services:
   - Backend API: http://localhost:5050
   - News API: http://localhost:5054
   - News Analysis API: http://localhost:5055
   - Understander API: http://localhost:5052
   - Recommender API: http://localhost:5051

### Option 2: Manual Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies for each service:
   ```bash
   cd news_analysis && pip install -r requirements.txt && cd ..
   cd backend && pip install -r requirements.txt && cd ..
   cd news && pip install -r requirements.txt && cd ..
   cd understander && pip install -r requirements.txt && cd ..
   cd recommender && pip install -r requirements.txt && cd ..
   cd ai_utils && pip install -r requirements.txt && cd ..
   
   # Install common dependencies
   pip install flask flask_cors requests numpy langchain sentence-transformers chromadb fastapi pydantic uvicorn
   ```

3. Start each service in a separate terminal window:
   ```bash
   # Terminal 1
   cd news_analysis && python news_analysis_service.py
   
   # Terminal 2
   cd backend && python app.py
   
   # Terminal 3
   cd news && python app.py
   
   # Terminal 4
   cd understander && python app.py
   
   # Terminal 5
   cd recommender && python app.py
   ```

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Build and start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the services:
   - Backend API: http://localhost:5050
   - News API: http://localhost:5054
   - News Analysis API: http://localhost:5055
   - Understander API: http://localhost:5052
   - Recommender API: http://localhost:5051

3. To stop the services:
   ```bash
   docker-compose down
   ```

### Individual Services

You can also build and run individual services:

```bash
# Build a specific service
docker-compose build news_analysis

# Run a specific service
docker-compose up news_analysis

# Run in detached mode
docker-compose up -d
```

## Debugging

### Logs

#### Docker Deployment
```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs news_analysis

# Follow logs in real-time
docker-compose logs -f
```

#### Local Deployment
Logs are displayed in each terminal window.

### Accessing Containers

```bash
# Get container IDs
docker ps

# Access a container's shell
docker exec -it <container_id> bash
```

## Configuration

The application configuration is in `config.json`. This file is mounted as a volume in Docker, so changes to it will be reflected in the containers. 