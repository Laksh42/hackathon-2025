# Financial Assistant Application - Hackathon 2025

A comprehensive financial assistant application that provides personalized recommendations based on user interactions and financial profile.

## System Architecture

The application is built with a microservices architecture:

1. **Frontend**: React application with Material UI
2. **Backend**: Flask API that coordinates between services
3. **Understander**: Service for processing user conversations
4. **Recommender**: Service for generating financial recommendations
5. **Auth**: Service for user authentication and profile management
6. **News Analysis**: Service for processing financial news and generating personalized news recommendations using vector embeddings
7. **Database**: SQLite for development, PostgreSQL for production

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│ Understander│
│    (React)  │◀────│   (Flask)   │◀────│   (Flask)   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ Recommender │     │    Auth     │
                    │   (Flask)   │     │   (Flask)   │
                    └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Database   │
                                        │  (SQLite)   │
                                        └─────────────┘
```

## Features

- **User Authentication**: Secure login and registration system
- **Conversational Onboarding**: Interactive dialogue to understand user's financial situation
- **Personalized Recommendations**: AI-driven financial product recommendations
- **Financial News**: Latest relevant financial news
- **User Dashboard**: Central view of all recommendations and financial information
- **Profile Management**: User profile and persona management
- **Vector-based News Analysis**: Personalized news recommendations based on user profile
- **Interactive Financial Chatbot**: AI-powered assistant in the dashboard
- **Understander Service** - Uses AI to understand user messages and identify intents, entities, and sentiment
- **Recommender Service** - Generates personalized financial product recommendations based on user profile
- **News Analysis Service** - Processes and indexes financial news articles, providing topic classification and sentiment analysis
- **News Summarization** - Generates concise summaries of financial news articles with customizable options for length, focus, and style
  - Single article summarization
  - Multi-article collection summarization
  - Customizable focus areas and style options
  - Keyword extraction from articles
- **Backend Service** - Central API gateway that coordinates between all services
- **Frontend** - React application for user interaction

## Getting Started

### Quick Start

The application now offers simplified deployment options:

1. **Local deployment with automatic setup**:
   ```bash
   ./startup.sh
   ```

2. **Docker Compose deployment**:
   ```bash
   docker-compose up --build
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- Docker and Docker Compose (for containerized deployment)

### Quick Start Guide for Cursor AI

To automatically set up and run the application with Cursor AI, you can use the following commands:

```bash
# 1. Setup Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies for each service
cd auth && pip install -r requirements.txt && cd ..
cd backend && pip install -r requirements.txt && cd ..
cd understander && pip install -r requirements.txt && cd ..
cd recommender && pip install -r requirements.txt && cd ..

# 3. Initialize the auth database
cd auth
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
cd ..

# 4. Install frontend dependencies
cd frontend && npm install && cd ..

# 5. Start all services in separate terminals
# Service 1: Auth (Port 5053)
cd auth && python app.py
# Service 2: Recommender (Port 5051)
cd recommender && python app.py
# Service 3: Understander (Port 5052)
cd understander && python app.py
# Service 4: Backend (Port 5050)
cd backend && python app.py
# Service 5: Frontend (Port 3000)
cd frontend && npm start
```

Once all services are running, visit http://localhost:3000 in your browser. Create an account and begin the onboarding chat process.

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Laksh42/hackathon-2025.git
   cd hackathon-2025
   ```

2. Start the application with Docker Compose (optional):
   ```
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5050

### Local Development

#### Database Setup

The application uses SQLite by default for development, which requires no additional setup.

If you prefer PostgreSQL:

1. Install PostgreSQL using Homebrew (macOS):
   ```bash
   brew install postgresql@14
   brew services start postgresql@14
   ```

2. Create a database and user:
   ```bash
   createdb financial_assistant
   psql -d financial_assistant -c "CREATE USER postgres WITH PASSWORD 'postgres';"
   psql -d financial_assistant -c "GRANT ALL PRIVILEGES ON DATABASE financial_assistant TO postgres;"
   ```

3. Configure your environment variables in auth/.env:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/financial_assistant
   JWT_SECRET_KEY=VnbRyn2dIcom20/8Y0o9fQrg00Ew2RRPxA9Gj0CoGK0=
   PORT=5053
   ```

#### Starting Services Manually

Start each service in a separate terminal:

1. Auth Service:
```bash
cd auth
pip install -r requirements.txt
python app.py
```

2. Recommender Service:
```bash
cd recommender
pip install -r requirements.txt
python app.py
```

3. Understander Service:
```bash
cd understander
pip install -r requirements.txt
python app.py
```

4. Backend Service:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

5. Frontend:
```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Auth Service (port 5053)

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/check-auth` - Validate JWT token
- `GET /api/v1/auth/persona` - Get user persona
- `POST /api/v1/auth/persona` - Save user persona

### Backend Service (port 5050)

- `GET /api/v1/recommendations` - Get personalized recommendations
- `GET /api/v1/products` - Get all available financial products
- `GET /api/v1/news` - Get general financial news
- `GET /api/v1/personalized-news` - Get personalized financial news based on user profile
- `POST /api/v1/news/summarize` - Generate a summary of one or more news articles
- `POST /api/v1/news/summarize-collection` - Generate a summary of a collection of news articles by their IDs
- `POST /api/v1/chat` - Process chat messages

### Understander Service (port 5052)

- `POST /api/v1/understand` - Process a user message
- `POST /api/v1/user/profile` - Generate user profile

### Recommender Service (port 5051)

- `POST /api/v1/generate` - Generate recommendations based on user profile
- `GET /api/v1/news` - Get financial news

### News Analysis API

- `POST /api/v1/news/personalized` - Get news articles personalized to a user vector
- `POST /api/v1/news/process` - Process and index news articles
- `POST /api/v1/news/summarize` - Generate summaries for news articles with customizable options

## Troubleshooting

### Common Issues

1. **Port already in use**: 
   - Check for running services: `lsof -i :<port_number>`
   - Kill the process: `kill -9 <PID>`

2. **Authentication errors**:
   - Make sure JWT_SECRET_KEY is the same in both auth and backend services
   - Clear browser cookies and localStorage, then login again

3. **No recommendations showing**:
   - Check browser console for errors
   - Verify the auth token is properly passed in API calls
   - Complete the onboarding chat process

4. **Chat not working**:
   - Ensure the understander service is running
   - Check browser console for API errors

- If services fail to connect, check that all services are running and that the `config.json` URLs are correct.
- For authentication issues, verify that the `auth_service_url` is correct and that the Auth Service is running.
- If Docker containers fail to build, ensure Docker is running and that you have sufficient permissions.

## API Examples

### News Summarization

#### Summarize Articles
```
POST /api/v1/news/summarize
Content-Type: application/json
Authorization: Bearer <user_token>

{
  "articles": [
    {
      "id": "news123",
      "title": "Market Rally Continues for Third Day",
      "content": "The stock market continued its upward trend for the third consecutive day, with tech stocks leading the gains..."
    }
  ],
  "options": {
    "max_length": 150,
    "focus": "market_impact",
    "style": "concise"
  }
}
```

#### Summarize Collection by IDs
```
POST /api/v1/news/summarize-collection
Content-Type: application/json
Authorization: Bearer <user_token>

{
  "news_ids": ["news123", "news456", "news789"],
  "options": {
    "max_length": 300,
    "focus": "investment_opportunities",
    "style": "detailed"
  }
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Wells Fargo for the challenge
- The hackathon organizing team
- All contributors to the project