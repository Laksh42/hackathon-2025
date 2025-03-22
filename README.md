# Financial Assistant Application - Hackathon 2025

A comprehensive financial assistant application that provides personalized recommendations based on user interactions and financial profile.

## System Architecture

The application is built with a microservices architecture:

1. **Frontend**: React application with Material UI
2. **Backend**: Flask API that coordinates between services
3. **Understander**: Service for processing user conversations
4. **Recommender**: Service for generating financial recommendations
5. **Auth**: Service for user authentication and profile management
6. **Database**: PostgreSQL for data persistence

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
                                        │  PostgreSQL │
                                        │  Database   │
                                        └─────────────┘
```

## Features

- **User Authentication**: Secure login and registration system
- **Conversational Onboarding**: Interactive dialogue to understand user's financial situation
- **Personalized Recommendations**: AI-driven financial product recommendations
- **Financial News**: Latest relevant financial news
- **User Dashboard**: Central view of all recommendations and financial information
- **Profile Management**: User profile and persona management

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 16+ and npm (for local development)
- Python 3.9+ (for local development)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Laksh42/hackathon-2025.git
   cd hackathon-2025
   ```

2. Start the application with Docker Compose:
   ```
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5050
   - Database Admin: http://localhost:8080

### Local Development

#### Frontend

```bash
cd frontend
npm install
npm start
```

#### Backend Services

For each service (backend, recommender, understander, auth):

```bash
cd [service_directory]
pip install -r requirements.txt
python app.py
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
- `GET /api/v1/news` - Get financial news articles
- `POST /api/v1/chat` - Send a message to the chat interface

### Understander Service (port 5052)

- `POST /api/v1/understand` - Process a user message
- `GET /api/v1/dialogue/state` - Get dialogue state
- `POST /api/v1/dialogue/reset` - Reset dialogue
- `POST /api/v1/user/profile` - Generate user profile
- `POST /api/v1/user/vector` - Get user vector

### Recommender Service (port 5051)

- `POST /api/v1/generate` - Generate recommendations based on user profile

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