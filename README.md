# Marvel Rivals Analytics

A data analytics platform for Marvel Rivals game data, providing hero statistics, team composition analysis, and match outcome predictions.

## Features

- **Hero Analytics**: View detailed statistics for each hero including win rates, KDA, and average damage
- **Team Builder**: Create team compositions and get win probability predictions
- **Interactive Dashboard**: Overview of key game metrics and trends

## Tech Stack

**Backend**
- Python 3.10, FastAPI
- Pandas & NumPy for data processing
- PostgreSQL and Redis

**Frontend**
- React 18 with React Router
- Chart.js for data visualization

## Quick Start

1. Make sure you have Docker and Docker Compose installed
2. Run: docker-compose up --build
3. Visit http://localhost:3000 for the frontend
4. Visit http://localhost:8000/docs for the API documentation

## Development Setup

**Backend**
1. Navigate to backend directory
2. Install requirements from requirements.txt
3. Run uvicorn app.main:app --reload

**Frontend**
1. Navigate to frontend directory
2. Run npm install
3. Run npm start

## Project Structure

- `backend/`: Python FastAPI backend
  - `app/`: Main application code
  - `etl/`: Data processing pipeline
  - `tests/`: Backend tests
- `frontend/`: React frontend application
  - `src/components/`: React components
  - `public/`: Static assets

## License

This project is licensed under the MIT License.
