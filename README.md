# LinkedIn Baddie Finder

This repository contains a full-stack application:

- `client/` – React 18 + Vite frontend
- `server/` – FastAPI backend

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
   - On Windows (Git Bash):
   ```bash
   source .venv/Scripts/activate
   ```
   - On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
   - Copy `env.example` to `.env`
   - Add your `PERPLEXITY_API_KEY` if using Perplexity features
   - Optionally set `DEBUG=True` for development

6. Run the server:
```bash
# From the server directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### API Documentation

Once the backend is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Project Structure

```
.
├── client/           # React frontend
│   ├── src/         # Source files
│   └── package.json # Frontend dependencies
├── server/          # FastAPI backend
│   └── app/         # Application code
│       ├── main.py  # FastAPI application and endpoints
│       ├── models.py # Data models
│       ├── schemas.py # Pydantic schemas
│       ├── matcher.py # Matching engine
│       └── perplexity_service.py # AI service
└── README.md
```
