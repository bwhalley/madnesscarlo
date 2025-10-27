# 🚀 Getting Started with Web App Development

## What We Just Built

Your Docker development environment is ready! Here's what's included:

### ✅ Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL 14
- **Cache/Queue**: Redis 7
- **Background Jobs**: Celery workers
- **Location**: `backend/` directory

### ✅ Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite (fast!)
- **Styling**: TailwindCSS
- **State**: Zustand + TanStack Query
- **Location**: `frontend/` directory

### ✅ Docker Configuration
- **All services** orchestrated with Docker Compose
- **Hot reload** enabled for both frontend and backend
- **Database** with persistent storage
- **One command** to start everything

---

## 🏃 Quick Start (3 Steps)

### Option 1: Using the startup script (easiest)
```bash
./start-webapp.sh
```

### Option 2: Using docker-compose directly
```bash
docker-compose up -d --build
```

### Step 2: Wait ~30 seconds for services to start

### Step 3: Open your browser
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📂 What Got Created

```
madnesscarlo/
├── docker-compose.yml          ⭐ Orchestrates all services
├── start-webapp.sh             ⭐ Easy startup script
│
├── backend/                    🐍 Python Backend
│   ├── Dockerfile
│   ├── requirements.txt        📦 Python dependencies
│   ├── app/
│   │   ├── main.py            🚀 FastAPI application
│   │   ├── config.py          ⚙️  Configuration
│   │   ├── utils/
│   │   │   └── database.py    💾 Database setup
│   │   ├── api/               📡 API endpoints (to be built)
│   │   ├── models/            🗄️  Database models (to be built)
│   │   ├── schemas/           📋 Pydantic schemas (to be built)
│   │   ├── services/          🛠️  Business logic (to be built)
│   │   ├── tasks/             ⚙️  Celery tasks (to be built)
│   │   └── simulation/        🎲 Your existing code (to be moved)
│   └── tests/                 🧪 Backend tests
│
└── frontend/                   ⚛️  React Frontend
    ├── Dockerfile
    ├── package.json            📦 Node dependencies
    ├── index.html             
    ├── vite.config.ts         ⚡ Vite configuration
    ├── tailwind.config.js     🎨 Tailwind setup
    └── src/
        ├── main.tsx           🚀 React entry point
        ├── App.tsx            📱 Main app component
        ├── services/
        │   └── api.ts         📡 Axios API client
        ├── components/        🧩 React components (to be built)
        ├── pages/             📄 Page components (to be built)
        ├── hooks/             🪝 Custom hooks (to be built)
        └── types/             📝 TypeScript types (to be built)
```

---

## 🎯 What's Working Right Now

### ✅ Backend
- [x] FastAPI server running on port 8000
- [x] Health check endpoint: `/health`
- [x] API info endpoint: `/api/info`
- [x] Auto-generated docs: `/docs`
- [x] PostgreSQL database connected
- [x] Redis cache connected
- [x] Celery worker running

### ✅ Frontend
- [x] React app running on port 5173
- [x] TypeScript configured
- [x] TailwindCSS working
- [x] Axios API client setup
- [x] Welcome page with system status

### ✅ Infrastructure
- [x] Docker Compose orchestration
- [x] Hot reload for backend
- [x] Hot reload for frontend
- [x] PostgreSQL with persistent storage
- [x] Redis for caching

---

## 🔧 Common Commands

### Start Everything
```bash
./start-webapp.sh
# or
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery-worker
```

### Stop Everything
```bash
docker-compose down

# With data cleanup
docker-compose down -v
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild After Changes
```bash
docker-compose build backend
docker-compose up -d backend
```

### Shell into Containers
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# PostgreSQL
docker-compose exec postgres psql -U madness_user -d madnesscarlo

# Redis
docker-compose exec redis redis-cli
```

---

## 🐛 Troubleshooting

### "Port already in use"
```bash
# Check what's using the port
lsof -i :5173  # or :8000, :5432, :6379

# Stop the conflicting service or change port in docker-compose.yml
```

### "Docker daemon not running"
```bash
# Start Docker Desktop application
open -a Docker  # on macOS
```

### Services won't start
```bash
# Check logs for errors
docker-compose logs

# Rebuild with no cache
docker-compose build --no-cache
docker-compose up -d
```

### Frontend shows connection error
```bash
# Make sure backend is running
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend
```

---

## 📚 Next Steps - Development Roadmap

### Phase 1: Backend Foundation (Week 1)
- [ ] Create database models (User, Deck, Simulation)
- [ ] Setup Alembic migrations
- [ ] Implement JWT authentication
- [ ] Create Deck CRUD endpoints
- [ ] Write tests for API endpoints

**Start with**: `backend/app/models/` directory

### Phase 2: Frontend Auth (Week 1-2)
- [ ] Create login/register pages
- [ ] Implement JWT token storage
- [ ] Create protected routes
- [ ] Add authentication context

**Start with**: `frontend/src/pages/auth/` directory

### Phase 3: Deck Management (Week 2)
- [ ] Build deck list view
- [ ] Create deck editor component
- [ ] Implement CSV import/export
- [ ] Add card search functionality

**Start with**: `frontend/src/pages/decks/` directory

### Phase 4: Simulation Integration (Week 3)
- [ ] Move existing simulation code to backend
- [ ] Create simulation API endpoints
- [ ] Setup Celery tasks for background processing
- [ ] Implement WebSocket for progress updates

**Start with**: Copy `madness.py` to `backend/app/simulation/`

### Phase 5: Results Dashboard (Week 3-4)
- [ ] Create results view components
- [ ] Add interactive charts (Recharts)
- [ ] Implement Excel export
- [ ] Build comparison view

**Start with**: `frontend/src/components/results/` directory

---

## 💡 Development Tips

### Hot Reload is Enabled
- Edit backend Python files → Auto-reloads
- Edit frontend React files → Instant update (HMR)

### Debugging
**Backend**:
```python
import pdb; pdb.set_trace()  # Breakpoint
```

**Frontend**:
- Use browser DevTools (F12)
- Install React DevTools extension

### Code Quality
```bash
# Format backend code
docker-compose exec backend black app/

# Lint frontend code
docker-compose exec frontend npm run lint
```

### Testing
```bash
# Backend tests (when written)
docker-compose exec backend pytest

# Frontend tests (when written)
docker-compose exec frontend npm test
```

---

## 📖 Documentation

All documentation is in the project root:

- **README_WEBAPP.md** - Complete web app guide
- **WEB_APP_PROJECT_PLAN.md** - Full 12-week plan
- **WEB_APP_MIGRATION_PLAN.md** - Technical architecture
- **WEBAPP_QUICK_START.md** - Setup instructions
- **WEBAPP_UI_WIREFRAMES.md** - UI mockups
- **WEBAPP_COMPARISON_SUMMARY.md** - CLI vs Web comparison

---

## ✨ Your First Task

Want to see it all working? Here's your first task:

1. **Start the services**:
   ```bash
   ./start-webapp.sh
   ```

2. **Check the backend**:
   - Open: http://localhost:8000/docs
   - Try the `/health` endpoint
   - Try the `/api/info` endpoint

3. **Check the frontend**:
   - Open: http://localhost:5173
   - You should see a welcome page

4. **Test the connection**:
   - Click the API links on the frontend
   - Verify both services are talking to each other

---

## 🎉 Success!

If you see:
- ✅ Frontend at http://localhost:5173
- ✅ Backend API docs at http://localhost:8000/docs
- ✅ Both services showing "healthy"

**You're ready to start building!** 🚀

Pick a task from Phase 1 and let's code!

---

**Questions?** Check the documentation files or ask for help!

