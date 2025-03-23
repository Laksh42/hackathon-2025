#!/bin/bash
# Startup script for Financial Assistant Application

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies for each service
echo "Installing dependencies for each service..."
cd news_analysis && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in news_analysis" && cd ..
cd backend && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in backend" && cd ..
cd news && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in news" && cd ..
cd understander && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in understander" && cd ..
cd recommender && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in recommender" && cd ..
cd ai_utils && pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt found in ai_utils" && cd ..

# Install common dependencies
pip install flask flask_cors requests numpy langchain sentence-transformers chromadb fastapi pydantic uvicorn

# Start the services in separate terminals
# Using gnome-terminal for Linux, Terminal.app for macOS, or cmd for Windows
echo "Starting services..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  gnome-terminal -- bash -c "cd news_analysis && python news_analysis_service.py; exec bash"
  sleep 2
  gnome-terminal -- bash -c "cd backend && python app.py; exec bash"
  sleep 2
  gnome-terminal -- bash -c "cd news && python app.py; exec bash"
  sleep 2
  gnome-terminal -- bash -c "cd understander && python app.py; exec bash"
  sleep 2
  gnome-terminal -- bash -c "cd recommender && python app.py; exec bash"
  sleep 2
elif [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e 'tell app "Terminal" to do script "cd '$PWD'/news_analysis && source ../.venv/bin/activate && python news_analysis_service.py"'
  sleep 2
  osascript -e 'tell app "Terminal" to do script "cd '$PWD'/backend && source ../.venv/bin/activate && python app.py"'
  sleep 2
  osascript -e 'tell app "Terminal" to do script "cd '$PWD'/news && source ../.venv/bin/activate && python app.py"'
  sleep 2
  osascript -e 'tell app "Terminal" to do script "cd '$PWD'/understander && source ../.venv/bin/activate && python app.py"'
  sleep 2
  osascript -e 'tell app "Terminal" to do script "cd '$PWD'/recommender && source ../.venv/bin/activate && python app.py"'
  sleep 2
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  # Windows
  start cmd /k "cd news_analysis && python news_analysis_service.py"
  sleep 2
  start cmd /k "cd backend && python app.py"
  sleep 2
  start cmd /k "cd news && python app.py"
  sleep 2
  start cmd /k "cd understander && python app.py"
  sleep 2
  start cmd /k "cd recommender && python app.py"
  sleep 2
fi

echo "All services started!"
echo "Backend API: http://localhost:5050"
echo "News API: http://localhost:5054"
echo "News Analysis API: http://localhost:5055"
echo "Understander API: http://localhost:5052"
echo "Recommender API: http://localhost:5051" 