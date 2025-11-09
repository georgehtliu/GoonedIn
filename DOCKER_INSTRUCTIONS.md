# Docker Setup Instructions

This guide will help you run the GoonedIn application using Docker and Docker Compose.

## Prerequisites

1. **Docker** - Install Docker Desktop for Windows from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Docker Compose** - Usually included with Docker Desktop

## Quick Start

### 1. Create Environment File

Create a `.env` file in the project root with your API keys:

```env
# Backend API Keys
GEMINI_API_KEY=your_gemini_api_key_here
PHANTOMBUSTER_API_KEY=your_phantombuster_api_key_here
PHANTOMBUSTER_SEARCH_AGENT_ID=your_phantombuster_agent_id_here
PHANTOMBUSTER_SESSION_COOKIE=your_linkedin_session_cookie_here

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB=linkedin_baddie_finder
MONGODB_COLLECTION=search_results

# Frontend Configuration (optional - defaults to http://localhost:8000)
VITE_API_BASE_URL=http://localhost:8000
```

### 2. Build and Start Services

From the project root directory, run:

```powershell
docker-compose up --build
```

This will:
- Build the backend and frontend Docker images
- Start both services
- The backend will be available at `http://localhost:8000`
- The frontend will be available at `http://localhost:3000`

### 3. Access the Application

- **Frontend**: Open your browser to `http://localhost:3000`
- **Backend API**: Available at `http://localhost:8000`
- **API Health Check**: `http://localhost:8000/health`

## Common Commands

### Start services in detached mode (background)
```powershell
docker-compose up -d
```

### Stop services
```powershell
docker-compose down
```

### View logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild after code changes
```powershell
docker-compose up --build
```

### Stop and remove containers, networks, and volumes
```powershell
docker-compose down -v
```

## Troubleshooting

### Port Already in Use
If port 8000 or 3000 is already in use, modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### Environment Variables Not Loading
Make sure your `.env` file is in the project root (same directory as `docker-compose.yml`).

### Backend Not Starting
Check the logs:
```powershell
docker-compose logs backend
```

Common issues:
- Missing environment variables
- MongoDB connection issues
- API key authentication failures

### Frontend Can't Connect to Backend
Make sure:
1. Both services are running: `docker-compose ps`
2. The `VITE_API_BASE_URL` in `.env` is set to `http://localhost:8000`
3. Rebuild the frontend if you changed the API URL: `docker-compose up --build frontend`

## Architecture

- **Backend**: FastAPI application running on port 8000
- **Frontend**: React + Vite application served via nginx on port 3000
- **Communication**: Frontend communicates with backend via HTTP API

The services are connected via Docker's internal network, but the frontend (running in the browser) connects to the backend using `localhost:8000` since requests come from the user's browser, not from inside Docker.

