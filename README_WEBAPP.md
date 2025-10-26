# MTG Madness Carlo - Web Application

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- Git

### Start the Application

```bash
# 1. Start all services
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Stop the Application

```bash
docker-compose down

# Or with data cleanup:
docker-compose down -v
```

## 📦 What's Running

When you start Docker Compose, these services will be available:

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 5173 | React + TypeScript app |
| **Backend** | 8000 | FastAPI Python backend |
| **Celery Worker** | - | Background job processor |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache & job queue |

## 🛠 Development Workflow

### Backend Development

```bash
# Shell into backend container
docker-compose exec backend bash

# Run tests
pytest

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check logs
docker-compose logs -f backend
```

### Frontend Development

```bash
# Shell into frontend container
docker-compose exec frontend sh

# Install new package
npm install package-name

# Check logs
docker-compose logs -f frontend
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U madness_user -d madnesscarlo

# Or use a GUI tool:
# Host: localhost
# Port: 5432
# User: madness_user
# Password: madness_pass_dev
# Database: madnesscarlo
```

### Redis Access

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR
```

## 📝 Project Structure

```
madnesscarlo/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── tasks/          # Celery tasks
│   │   ├── simulation/     # Simulation code
│   │   ├── utils/          # Utilities
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── hooks/         # Custom hooks
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utilities
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml      # Docker orchestration
├── README_WEBAPP.md        # This file
└── WEB_APP_PROJECT_PLAN.md # Full project plan
```

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `CORS_ORIGINS` - Allowed frontend origins

**Frontend** (`frontend/.env`):
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

See `.env.example` files for complete configuration options.

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_api.py
```

### Frontend Tests

```bash
# Run tests (when implemented)
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm run test:coverage
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild container
docker-compose build backend
docker-compose up -d backend
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Clear node_modules and reinstall
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
```

### Database connection issues
```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check if database exists
docker-compose exec postgres psql -U madness_user -l
```

### Port already in use
```bash
# Check what's using the port
lsof -i :5173  # or :8000, :5432, :6379

# Kill the process or change ports in docker-compose.yml
```

## 📚 Next Steps

1. **Authentication** - Add user registration and login
2. **Deck Management** - Build deck CRUD API and UI
3. **Simulations** - Integrate existing simulation code
4. **Real-time Progress** - WebSocket implementation
5. **Results Dashboard** - Interactive charts and tables

See `WEB_APP_PROJECT_PLAN.md` for the complete roadmap.

## 🤝 Development Tips

### Hot Reload
- Backend: Automatically reloads on code changes (uvicorn --reload)
- Frontend: Automatically reloads on code changes (Vite HMR)

### Debugging
- Backend: Add `import pdb; pdb.set_trace()` for breakpoints
- Frontend: Use browser DevTools and React DevTools extension

### Code Quality
```bash
# Backend formatting
docker-compose exec backend black app/
docker-compose exec backend isort app/

# Frontend linting
docker-compose exec frontend npm run lint
```

## 📖 Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Project Plan**: `WEB_APP_PROJECT_PLAN.md`
- **Migration Guide**: `WEB_APP_MIGRATION_PLAN.md`
- **UI Wireframes**: `WEBAPP_UI_WIREFRAMES.md`
- **Quick Start**: `WEBAPP_QUICK_START.md`

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f [service]`
3. Restart services: `docker-compose restart`
4. Rebuild containers: `docker-compose build --no-cache`
5. Check documentation files in the project root

---

**Happy coding! 🎉**

