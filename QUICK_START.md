# Quick Start Guide

## 🚀 Running the Web Application

### Start Everything
```bash
cd /Users/brian/madnesscarlo
docker-compose up -d
```

### Access the Application
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

### Stop Everything
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Check Status
```bash
docker-compose ps
```

---

## 🎯 Testing the API

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "username": "yourname",
    "password": "yourpassword",
    "full_name": "Your Name"
  }'
```

Save the `access_token` from the response!

### 2. Create a Deck
```bash
TOKEN="<your-access-token>"

curl -X POST http://localhost:8000/api/decks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "My Deck",
    "description": "A test deck",
    "cards": [
      {"name": "Lightning Bolt", "quantity": 4},
      {"name": "Mountain", "quantity": 20}
    ]
  }'
```

### 3. List Your Decks
```bash
curl http://localhost:8000/api/decks/ \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Create a Simulation Config
```bash
curl -X POST http://localhost:8000/api/configs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "My Config",
    "description": "Test configuration",
    "config_data": {
      "simulations": 10000,
      "max_turns": 4,
      "key_cards": ["Lightning Bolt"]
    }
  }'
```

---

## 🛠️ Development Tasks

### Backend: Apply Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Backend: Create New Migration
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Backend: Access PostgreSQL
```bash
docker-compose exec postgres psql -U madness -d madness
```

### Backend: Run Python Shell
```bash
docker-compose exec backend python
```

### Frontend: Install New Package
```bash
docker-compose exec frontend npm install <package-name>
```

### Frontend: Access Shell
```bash
docker-compose exec frontend sh
```

### Rebuild After Dependency Changes
```bash
# Backend
docker-compose build backend
docker-compose up -d backend

# Frontend
docker-compose build frontend
docker-compose up -d frontend

# Everything
docker-compose build
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check what's running
docker ps -a

# Remove all containers and start fresh
docker-compose down
docker-compose up -d

# Check logs for errors
docker-compose logs
```

### Database Connection Errors
```bash
# Make sure Postgres is healthy
docker-compose ps postgres

# Restart Postgres
docker-compose restart postgres

# Check if migrations need to be applied
docker-compose exec backend alembic current
docker-compose exec backend alembic upgrade head
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # Postgres

# Kill the process or change ports in docker-compose.yml
```

### Frontend Won't Load
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

### Clear Everything and Start Over
```bash
# WARNING: This deletes ALL data!
docker-compose down -v  # -v removes volumes (database data)
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

---

## 📚 Additional Resources

- **Full Phase 1 Documentation:** [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md)
- **Getting Started Guide:** [GETTING_STARTED.md](GETTING_STARTED.md)
- **Project Plan:** [WEB_APP_PROJECT_PLAN.md](WEB_APP_PROJECT_PLAN.md)
- **CLI Tool Documentation:** [README.md](README.md)

---

## 🎓 Common Workflows

### Making Backend Code Changes
1. Edit Python files in `backend/app/`
2. Save the file
3. Restart backend: `docker-compose restart backend`
4. Check logs: `docker-compose logs -f backend`

### Making Frontend Code Changes
1. Edit TypeScript/React files in `frontend/src/`
2. Save the file
3. Vite automatically reloads (check browser)
4. If it doesn't reload, restart: `docker-compose restart frontend`

### Adding New API Endpoint
1. Add endpoint in `backend/app/api/`
2. Add schema in `backend/app/schemas/`
3. Add model if needed in `backend/app/models/`
4. Restart backend: `docker-compose restart backend`
5. Visit http://localhost:8000/docs to see it

### Database Schema Changes
1. Edit models in `backend/app/models/`
2. Create migration: `docker-compose exec backend alembic revision --autogenerate -m "description"`
3. Review migration in `backend/alembic/versions/`
4. Apply migration: `docker-compose exec backend alembic upgrade head`
5. Restart backend: `docker-compose restart backend`

---

## 🎉 You're Ready!

The web application is now running and ready for development. Visit http://localhost:5173 to see it in action!

**Next Steps:**
- Test the API endpoints in the Swagger UI: http://localhost:8000/docs
- Start building the frontend UI components
- Integrate the simulation engine in Phase 2

