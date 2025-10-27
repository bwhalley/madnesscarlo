# Web App Quick Start Guide

## 🚀 Getting Started with Migration

This guide provides quick commands to bootstrap your web app development.

---

## Step 1: Backend Setup (15 minutes)

### Create Backend Structure

```bash
# Create backend directory
mkdir -p backend/app/{api,models,schemas,services,tasks,simulation,utils,middleware}
mkdir -p backend/alembic/versions
mkdir -p backend/tests/{test_api,test_services,test_tasks}

# Move existing simulation code
cp madness.py backend/app/simulation/
cp experiment_runner.py backend/app/simulation/
cp experiment_config.py backend/app/simulation/
cp variant_generator.py backend/app/simulation/
cp deck_comparison.py backend/app/simulation/
cp comparison_utils.py backend/app/simulation/
```

### Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    sqlalchemy==2.0.23 \
    alembic==1.12.1 \
    psycopg2-binary==2.9.9 \
    redis==5.0.1 \
    celery==5.3.4 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    websockets==12.0 \
    pandas==2.3.3 \
    openpyxl==3.1.5 \
    tqdm==4.67.1

# Save requirements
pip freeze > requirements.txt
```

### Create Basic FastAPI App

```bash
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MTG Madness Carlo API",
    description="Monte Carlo simulation API for MTG deck analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MTG Madness Carlo API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

### Run Backend

```bash
uvicorn app.main:app --reload --port 8000
# Visit: http://localhost:8000/docs (Swagger UI)
```

---

## Step 2: Database Setup (10 minutes)

### Install PostgreSQL (macOS)

```bash
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb madnesscarlo
```

### Install PostgreSQL (Docker - Recommended)

```bash
docker run --name madness-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=user \
  -e POSTGRES_DB=madnesscarlo \
  -p 5432:5432 \
  -d postgres:14
```

### Install Redis (Docker - Recommended)

```bash
docker run --name madness-redis \
  -p 6379:6379 \
  -d redis:7
```

### Configure Environment

```bash
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/madnesscarlo

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Environment
ENVIRONMENT=development
EOF
```

### Initialize Database with Alembic

```bash
# Initialize alembic
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial schema"

# Run migration
alembic upgrade head
```

---

## Step 3: Frontend Setup (10 minutes)

### Create React App

```bash
cd ..
npm create vite@latest frontend -- --template react-ts
cd frontend
```

### Install Dependencies

```bash
# Core dependencies
npm install \
  axios \
  @tanstack/react-query \
  zustand \
  react-router-dom \
  react-hook-form

# UI libraries
npm install \
  recharts \
  lucide-react \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-select \
  @radix-ui/react-tabs \
  @radix-ui/react-toast

# Dev dependencies
npm install -D \
  tailwindcss \
  postcss \
  autoprefixer \
  @types/node

# Initialize Tailwind
npx tailwindcss init -p
```

### Configure Tailwind

```bash
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
```

### Create Environment Config

```bash
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
```

### Run Frontend

```bash
npm run dev
# Visit: http://localhost:5173
```

---

## Step 4: Docker Compose (All-in-One)

### Create docker-compose.yml

```bash
cd ..
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: madnesscarlo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/madnesscarlo
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: dev-secret-key-change-me
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/madnesscarlo
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_WS_URL: ws://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  postgres_data:
  redis_data:
EOF
```

### Create Dockerfiles

**Backend Dockerfile:**
```bash
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations on startup
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF
```

**Frontend Dockerfile:**
```bash
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application
COPY . .

# Expose port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host"]
EOF
```

### Start Everything

```bash
docker-compose up -d
docker-compose logs -f
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Stop Everything

```bash
docker-compose down
# Or with data cleanup:
docker-compose down -v
```

---

## Step 5: First API Endpoint (Decks)

### Create Deck Model

```bash
cat > backend/app/models/deck.py << 'EOF'
from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.utils.database import Base

class Deck(Base):
    __tablename__ = "decks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(String)
    cards = Column(JSON, nullable=False)  # Array of card objects
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
EOF
```

### Create Deck Schema

```bash
cat > backend/app/schemas/deck.py << 'EOF'
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class CardInDeck(BaseModel):
    card_name: str
    quantity: int
    type: Optional[str] = None
    mana_cost: Optional[str] = None
    conditions: Optional[str] = None

class DeckBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    cards: List[CardInDeck]
    is_public: bool = False

class DeckCreate(DeckBase):
    pass

class DeckUpdate(DeckBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    cards: Optional[List[CardInDeck]] = None

class DeckInDB(DeckBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
EOF
```

### Create Deck API

```bash
cat > backend/app/api/decks.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.deck import DeckCreate, DeckUpdate, DeckInDB
from app.models.deck import Deck
from app.utils.database import get_db
# from app.utils.security import get_current_user  # Add later

router = APIRouter(prefix="/api/decks", tags=["decks"])

@router.get("/", response_model=List[DeckInDB])
def list_decks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all decks."""
    decks = db.query(Deck).offset(skip).limit(limit).all()
    return decks

@router.post("/", response_model=DeckInDB, status_code=201)
def create_deck(
    deck: DeckCreate,
    db: Session = Depends(get_db)
):
    """Create a new deck."""
    db_deck = Deck(**deck.dict(), user_id="00000000-0000-0000-0000-000000000000")  # Temp
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

@router.get("/{deck_id}", response_model=DeckInDB)
def get_deck(deck_id: UUID, db: Session = Depends(get_db)):
    """Get a specific deck."""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

@router.put("/{deck_id}", response_model=DeckInDB)
def update_deck(
    deck_id: UUID,
    deck_update: DeckUpdate,
    db: Session = Depends(get_db)
):
    """Update a deck."""
    db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    update_data = deck_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deck, field, value)
    
    db.commit()
    db.refresh(db_deck)
    return db_deck

@router.delete("/{deck_id}", status_code=204)
def delete_deck(deck_id: UUID, db: Session = Depends(get_db)):
    """Delete a deck."""
    db_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    db.delete(db_deck)
    db.commit()
    return None
EOF
```

### Register API Router

```python
# In app/main.py, add:
from app.api import decks

app.include_router(decks.router)
```

---

## Step 6: First Frontend Component

### Create API Client

```bash
cat > frontend/src/services/api.ts << 'EOF'
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
EOF
```

### Create Deck Service

```bash
cat > frontend/src/services/deck.service.ts << 'EOF'
import api from './api';

export interface Card {
  card_name: string;
  quantity: number;
  type?: string;
  mana_cost?: string;
  conditions?: string;
}

export interface Deck {
  id: string;
  name: string;
  description?: string;
  cards: Card[];
  is_public: boolean;
  created_at: string;
  updated_at?: string;
}

export const deckService = {
  // Get all decks
  async getDecks(): Promise<Deck[]> {
    const response = await api.get('/api/decks');
    return response.data;
  },

  // Get single deck
  async getDeck(id: string): Promise<Deck> {
    const response = await api.get(`/api/decks/${id}`);
    return response.data;
  },

  // Create deck
  async createDeck(deck: Omit<Deck, 'id' | 'created_at' | 'updated_at'>): Promise<Deck> {
    const response = await api.post('/api/decks', deck);
    return response.data;
  },

  // Update deck
  async updateDeck(id: string, deck: Partial<Deck>): Promise<Deck> {
    const response = await api.put(`/api/decks/${id}`, deck);
    return response.data;
  },

  // Delete deck
  async deleteDeck(id: string): Promise<void> {
    await api.delete(`/api/decks/${id}`);
  },
};
EOF
```

### Create Deck List Component

```bash
cat > frontend/src/components/DeckList.tsx << 'EOF'
import { useQuery } from '@tanstack/react-query';
import { deckService, Deck } from '../services/deck.service';

export function DeckList() {
  const { data: decks, isLoading, error } = useQuery({
    queryKey: ['decks'],
    queryFn: deckService.getDecks,
  });

  if (isLoading) return <div>Loading decks...</div>;
  if (error) return <div>Error loading decks</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">My Decks</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {decks?.map((deck: Deck) => (
          <div key={deck.id} className="border rounded-lg p-4 hover:shadow-lg transition">
            <h2 className="text-xl font-semibold">{deck.name}</h2>
            <p className="text-gray-600 text-sm mt-2">{deck.description}</p>
            <p className="text-sm text-gray-500 mt-2">
              {deck.cards.reduce((sum, card) => sum + card.quantity, 0)} cards
            </p>
            <div className="mt-4 flex gap-2">
              <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">
                Edit
              </button>
              <button className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600">
                Simulate
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
EOF
```

---

## Development Workflow

### Daily Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery Worker
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev

# Terminal 4: Database/Redis (if not using Docker)
# Already running or use Docker
```

### Using Docker (Simplified)

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop everything
docker-compose down
```

### Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create migration after model changes
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Next Steps

After completing this quick start:

1. ✅ **Add Authentication** - JWT tokens, login/register
2. ✅ **Complete Deck API** - CSV import/export, validation
3. ✅ **Add Simulation API** - Integrate existing madness.py
4. ✅ **Add Celery Tasks** - Background simulation jobs
5. ✅ **Add WebSocket** - Real-time progress updates
6. ✅ **Build Deck Editor UI** - Rich editing experience
7. ✅ **Add Results Dashboard** - Charts and tables
8. ✅ **Implement Experiments** - Full experiment framework
9. ✅ **Add Comparisons** - Deck comparison tool
10. ✅ **Polish & Deploy** - Production ready

---

## Useful Commands

### Backend

```bash
# Run specific module
python -m app.simulation.madness

# Interactive Python shell with app context
python
>>> from app.models import Deck
>>> from app.utils.database import SessionLocal
>>> db = SessionLocal()
>>> decks = db.query(Deck).all()

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Frontend

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

### Docker

```bash
# Rebuild images
docker-compose build

# Remove all containers and volumes
docker-compose down -v

# Shell into container
docker-compose exec backend bash
docker-compose exec frontend sh

# View database
docker-compose exec postgres psql -U user -d madnesscarlo
```

---

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check Redis is running: `redis-cli ping`
- Verify environment variables in `.env`
- Check migrations: `alembic current`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/app/main.py`
- Verify `VITE_API_URL` in `frontend/.env`

### Celery worker not processing tasks
- Check Redis connection: `redis-cli ping`
- Verify Celery configuration
- Check worker logs: `celery -A app.tasks.celery_app inspect active`

### Database migration issues
- Reset database: `alembic downgrade base && alembic upgrade head`
- Check migration files in `alembic/versions/`
- Manually fix migration if needed

---

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **TanStack Query:** https://tanstack.com/query/latest
- **Celery Docs:** https://docs.celeryproject.org/
- **Alembic Docs:** https://alembic.sqlalchemy.org/
- **Tailwind CSS:** https://tailwindcss.com/docs

---

**Ready to build? Start with Step 1 and work your way through!** 🚀

