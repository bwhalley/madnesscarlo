# Web App Migration Plan: MTG Madness Carlo Simulator

## Executive Summary

This document outlines a comprehensive plan to migrate the MTG Madness Carlo Simulator from a command-line Python application to a full-featured web application. The web app will enable users to:

- Edit deck lists in the browser
- Configure simulation parameters via UI
- Run experiments and comparisons
- View results in real-time with interactive visualizations
- Save/load configurations and deck lists
- Share results with others

## Current State Analysis

### Existing Architecture

**Core Components:**
1. **Simulation Engine** (`madness.py`) - Monte Carlo simulation of MTG games
2. **Experiment Framework** (`experiment_runner.py`, `experiment_config.py`, `variant_generator.py`) - Automated deck optimization
3. **Deck Comparison** (`deck_comparison.py`, `comparison_utils.py`) - Side-by-side deck analysis
4. **Configuration System** - JSON-based configs for simulations, experiments, and sideboards
5. **Export System** - Excel output with 11+ sheets of statistics

**Key Features:**
- 🎲 Monte Carlo simulation (1000s of games)
- 📊 Comprehensive statistics (card stats, mulligan, opening hands, etc.)
- 🔬 Experimental framework with parallel execution
- ⚖️ Deck comparison with delta tracking
- 🎴 Sideboarding support
- 🎯 Pattern recognition and analysis

**Current Dependencies:**
- pandas==2.3.3
- openpyxl==3.1.5
- tqdm==4.67.1
- pytest>=7.0.0

**Strengths:**
- ✅ Well-structured Python codebase
- ✅ Comprehensive test coverage (80%)
- ✅ Clean separation of concerns
- ✅ Parallel processing support
- ✅ Rich statistical output

**Limitations for Web:**
- ❌ Command-line only interface
- ❌ No real-time progress feedback
- ❌ Excel-only output (not web-friendly)
- ❌ No user accounts or saved sessions
- ❌ No visual deck editor
- ❌ No interactive charts/graphs

---

## Proposed Architecture

### Technology Stack

#### Backend: FastAPI (Python)
**Rationale:**
- Native Python integration with existing codebase
- Async support for long-running simulations
- WebSocket support for real-time progress
- Automatic API documentation (Swagger/OpenAPI)
- High performance and modern async patterns

**Alternatives Considered:**
- Flask: Simpler but lacks native async/WebSocket support
- Django: Too heavyweight for this use case

#### Frontend: React with TypeScript
**Rationale:**
- Component-based architecture ideal for complex UIs
- Rich ecosystem for data visualization (Recharts, Victory)
- TypeScript for type safety and better developer experience
- Modern tooling (Vite for fast development)

**Key Libraries:**
- **React**: UI framework
- **TypeScript**: Type safety
- **TanStack Query**: Data fetching and caching
- **Zustand**: Lightweight state management
- **Recharts**: Data visualization
- **React Hook Form**: Form management
- **TailwindCSS**: Styling
- **shadcn/ui**: Component library
- **Axios**: HTTP client

#### Database: PostgreSQL + Redis
**PostgreSQL** for persistent data:
- User accounts
- Saved deck lists
- Saved configurations
- Simulation history
- Shared results

**Redis** for:
- Job queue (simulation tasks)
- Session storage
- Real-time progress tracking
- Cache layer

#### Task Queue: Celery + Redis
**Rationale:**
- Handle long-running simulations asynchronously
- Parallel worker support (leverage existing multiprocessing)
- Progress tracking and cancellation
- Automatic retry on failure

#### Deployment
- **Frontend**: Vercel or Netlify (static hosting)
- **Backend**: Railway, Render, or AWS ECS
- **Database**: Managed PostgreSQL (Railway, Supabase)
- **Redis**: Redis Cloud or Upstash
- **Storage**: S3 for exported files (Excel, CSV)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              React Frontend (TypeScript)             │   │
│  │                                                       │   │
│  │  • Deck Editor      • Config Editor                  │   │
│  │  • Experiment UI    • Results Dashboard              │   │
│  │  • Comparison Tool  • Interactive Charts             │   │
│  └───────────────────┬─────────────────────────────────┘   │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     │
┌────────────────────┴─────────────────────────────────────────┐
│                   FastAPI Backend (Python)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  REST API Endpoints                                  │    │
│  │  • /api/simulations     • /api/experiments          │    │
│  │  • /api/decks           • /api/comparisons          │    │
│  │  • /api/configs         • /api/auth                 │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                     │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │  WebSocket Server (Real-time Progress)              │    │
│  │  • Simulation progress  • Experiment updates        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────┬────────────────────────────┬───────────────────────┘
          │                            │
          │                            │
    ┌─────┴──────┐              ┌─────┴──────────┐
    │ PostgreSQL │              │ Redis          │
    │            │              │                │
    │ • Users    │              │ • Job Queue    │
    │ • Decks    │              │ • Sessions     │
    │ • Results  │              │ • Cache        │
    └────────────┘              └────┬───────────┘
                                     │
                             ┌───────┴────────┐
                             │ Celery Workers │
                             │                │
                             │ • Simulation   │
                             │ • Experiment   │
                             │ • Comparison   │
                             └────────────────┘
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Decks Table
```sql
CREATE TABLE decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cards JSONB NOT NULL,  -- Array of {card, quantity, type, mana_cost, conditions}
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_decks_user_id ON decks(user_id);
CREATE INDEX idx_decks_public ON decks(is_public) WHERE is_public = true;
```

### Simulation Configs Table
```sql
CREATE TABLE simulation_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    config JSONB NOT NULL,  -- Full simulation config JSON
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_configs_user_id ON simulation_configs(user_id);
```

### Simulations Table
```sql
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    deck_id UUID REFERENCES decks(id) ON DELETE SET NULL,
    config_id UUID REFERENCES simulation_configs(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,  -- 'pending', 'running', 'completed', 'failed'
    runs INTEGER NOT NULL,
    turns INTEGER NOT NULL,
    results JSONB,  -- Full results data
    progress INTEGER DEFAULT 0,  -- 0-100
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_simulations_user_id ON simulations(user_id);
CREATE INDEX idx_simulations_status ON simulations(status);
```

### Experiments Table
```sql
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    base_deck_id UUID REFERENCES decks(id) ON DELETE SET NULL,
    config JSONB NOT NULL,  -- Experiment configuration
    status VARCHAR(20) NOT NULL,
    variant_count INTEGER,
    results JSONB,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_experiments_user_id ON experiments(user_id);
CREATE INDEX idx_experiments_status ON experiments(status);
```

### Comparisons Table
```sql
CREATE TABLE comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    baseline_deck_id UUID REFERENCES decks(id) ON DELETE SET NULL,
    variant_deck_id UUID REFERENCES decks(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,
    results JSONB,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_comparisons_user_id ON comparisons(user_id);
```

### Shared Results Table
```sql
CREATE TABLE shared_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(20) NOT NULL,  -- 'simulation', 'experiment', 'comparison'
    resource_id UUID NOT NULL,
    share_token VARCHAR(50) UNIQUE NOT NULL,
    views INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shared_results_token ON shared_results(share_token);
```

---

## API Endpoints

### Authentication
```
POST   /api/auth/register          # Create new account
POST   /api/auth/login             # Login (returns JWT)
POST   /api/auth/logout            # Logout
GET    /api/auth/me                # Get current user
POST   /api/auth/refresh           # Refresh JWT token
```

### Decks
```
GET    /api/decks                  # List user's decks
POST   /api/decks                  # Create new deck
GET    /api/decks/{id}             # Get deck details
PUT    /api/decks/{id}             # Update deck
DELETE /api/decks/{id}             # Delete deck
POST   /api/decks/{id}/duplicate   # Duplicate deck
GET    /api/decks/public           # Browse public decks
POST   /api/decks/import           # Import from CSV/text
GET    /api/decks/{id}/export      # Export to CSV
POST   /api/decks/validate         # Validate deck format
```

### Simulation Configs
```
GET    /api/configs                # List user's configs
POST   /api/configs                # Create config
GET    /api/configs/{id}           # Get config
PUT    /api/configs/{id}           # Update config
DELETE /api/configs/{id}           # Delete config
GET    /api/configs/default        # Get default config
```

### Simulations
```
GET    /api/simulations            # List user's simulations
POST   /api/simulations            # Start new simulation
GET    /api/simulations/{id}       # Get simulation details & results
DELETE /api/simulations/{id}       # Cancel/delete simulation
GET    /api/simulations/{id}/export # Export results to Excel
WS     /ws/simulations/{id}        # WebSocket for real-time progress
```

### Experiments
```
GET    /api/experiments            # List user's experiments
POST   /api/experiments            # Start new experiment
GET    /api/experiments/{id}       # Get experiment details & results
DELETE /api/experiments/{id}       # Cancel/delete experiment
GET    /api/experiments/{id}/export # Export results to Excel
WS     /ws/experiments/{id}        # WebSocket for real-time progress
```

### Comparisons
```
GET    /api/comparisons            # List user's comparisons
POST   /api/comparisons            # Start new comparison
GET    /api/comparisons/{id}       # Get comparison details & results
DELETE /api/comparisons/{id}       # Delete comparison
GET    /api/comparisons/{id}/export # Export results to Excel
WS     /ws/comparisons/{id}        # WebSocket for real-time progress
```

### Sharing
```
POST   /api/share                  # Create shareable link
GET    /api/share/{token}          # View shared results (public)
DELETE /api/share/{token}          # Revoke share link
```

### Utilities
```
POST   /api/cards/search           # Search for MTG cards
GET    /api/cards/autocomplete     # Autocomplete card names
GET    /api/system/status          # System health check
GET    /api/system/workers         # Worker status
```

---

## Frontend Component Structure

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx
│   │
│   ├── deck/
│   │   ├── DeckEditor.tsx           # Main deck editor
│   │   ├── CardRow.tsx              # Individual card in deck
│   │   ├── CardSearch.tsx           # Search/autocomplete
│   │   ├── DeckList.tsx             # List of saved decks
│   │   ├── DeckImportDialog.tsx     # Import CSV/text
│   │   ├── DeckExportDialog.tsx     # Export options
│   │   └── DeckValidation.tsx       # Validation messages
│   │
│   ├── config/
│   │   ├── SimulationConfigEditor.tsx
│   │   ├── ExperimentConfigEditor.tsx
│   │   ├── MulliganStrategyEditor.tsx
│   │   ├── IdealSetupEditor.tsx
│   │   └── SideboardPlanEditor.tsx
│   │
│   ├── simulation/
│   │   ├── SimulationForm.tsx       # Setup new simulation
│   │   ├── SimulationList.tsx       # History of simulations
│   │   ├── SimulationProgress.tsx   # Real-time progress bar
│   │   ├── SimulationResults.tsx    # Results dashboard
│   │   └── SimulationCharts.tsx     # Visualization
│   │
│   ├── experiment/
│   │   ├── ExperimentForm.tsx
│   │   ├── ExperimentList.tsx
│   │   ├── ExperimentProgress.tsx
│   │   ├── ExperimentResults.tsx
│   │   ├── VariantComparison.tsx    # Compare variants
│   │   └── OptimizationGoals.tsx
│   │
│   ├── comparison/
│   │   ├── ComparisonForm.tsx
│   │   ├── ComparisonList.tsx
│   │   ├── ComparisonProgress.tsx
│   │   ├── ComparisonResults.tsx
│   │   └── DeltaVisualization.tsx   # Show deltas
│   │
│   ├── results/
│   │   ├── CardStatsTable.tsx
│   │   ├── KeyCardStatsTable.tsx
│   │   ├── IdealSetupsTable.tsx
│   │   ├── MulliganStatsChart.tsx
│   │   ├── OpeningHandsTable.tsx
│   │   ├── GraveyardStatsTable.tsx
│   │   ├── BattlefieldStatsTable.tsx
│   │   └── ExportButton.tsx
│   │
│   ├── charts/
│   │   ├── SuccessRateChart.tsx
│   │   ├── MulliganDistribution.tsx
│   │   ├── TurnByTurnChart.tsx
│   │   └── ComparisonChart.tsx
│   │
│   ├── shared/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Table.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ProgressBar.tsx
│   │
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       ├── Footer.tsx
│       └── Layout.tsx
│
├── pages/
│   ├── HomePage.tsx
│   ├── DashboardPage.tsx
│   ├── DecksPage.tsx
│   ├── DeckEditorPage.tsx
│   ├── SimulationsPage.tsx
│   ├── SimulationResultsPage.tsx
│   ├── ExperimentsPage.tsx
│   ├── ExperimentResultsPage.tsx
│   ├── ComparisonsPage.tsx
│   ├── ComparisonResultsPage.tsx
│   ├── ConfigsPage.tsx
│   └── SharedResultsPage.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useDecks.ts
│   ├── useSimulations.ts
│   ├── useExperiments.ts
│   ├── useComparisons.ts
│   ├── useWebSocket.ts
│   └── useExport.ts
│
├── services/
│   ├── api.ts              # Axios instance & interceptors
│   ├── auth.service.ts
│   ├── deck.service.ts
│   ├── simulation.service.ts
│   ├── experiment.service.ts
│   ├── comparison.service.ts
│   └── websocket.service.ts
│
├── store/
│   ├── authStore.ts        # Zustand store
│   ├── deckStore.ts
│   └── uiStore.ts
│
├── types/
│   ├── deck.types.ts
│   ├── simulation.types.ts
│   ├── experiment.types.ts
│   ├── comparison.types.ts
│   └── api.types.ts
│
├── utils/
│   ├── validation.ts
│   ├── formatting.ts
│   ├── export.ts
│   └── constants.ts
│
├── App.tsx
├── main.tsx
└── routes.tsx
```

---

## Backend Structure (FastAPI)

```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings and environment variables
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── decks.py            # Deck management endpoints
│   │   ├── simulations.py      # Simulation endpoints
│   │   ├── experiments.py      # Experiment endpoints
│   │   ├── comparisons.py      # Comparison endpoints
│   │   ├── configs.py          # Config management endpoints
│   │   ├── share.py            # Sharing endpoints
│   │   └── websockets.py       # WebSocket endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # SQLAlchemy User model
│   │   ├── deck.py             # SQLAlchemy Deck model
│   │   ├── simulation.py       # SQLAlchemy Simulation model
│   │   ├── experiment.py       # SQLAlchemy Experiment model
│   │   ├── comparison.py       # SQLAlchemy Comparison model
│   │   └── shared_result.py    # SQLAlchemy SharedResult model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic User schemas
│   │   ├── deck.py             # Pydantic Deck schemas
│   │   ├── simulation.py       # Pydantic Simulation schemas
│   │   ├── experiment.py       # Pydantic Experiment schemas
│   │   └── comparison.py       # Pydantic Comparison schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── deck_service.py     # Deck operations
│   │   ├── simulation_service.py
│   │   ├── experiment_service.py
│   │   └── comparison_service.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── simulation_tasks.py # Celery tasks for simulations
│   │   ├── experiment_tasks.py # Celery tasks for experiments
│   │   └── comparison_tasks.py # Celery tasks for comparisons
│   │
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── madness.py          # Core simulation (refactored from existing)
│   │   ├── experiment_runner.py
│   │   ├── experiment_config.py
│   │   ├── variant_generator.py
│   │   ├── deck_comparison.py
│   │   └── comparison_utils.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         # Password hashing, JWT
│   │   ├── database.py         # Database session management
│   │   ├── redis_client.py     # Redis connection
│   │   ├── export.py           # Excel/CSV export
│   │   └── validators.py       # Input validation
│   │
│   └── middleware/
│       ├── __init__.py
│       ├── auth_middleware.py
│       ├── cors_middleware.py
│       └── error_handler.py
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── test_api/
│   ├── test_services/
│   └── test_tasks/
│
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Migration Strategy: Phased Approach

### Phase 1: Core Backend API (Weeks 1-3)

**Goal:** Build minimum viable backend with basic simulation support

**Tasks:**
1. **Setup FastAPI project structure**
   - Initialize FastAPI app
   - Setup PostgreSQL with SQLAlchemy
   - Configure Redis connection
   - Setup Celery workers
   - Add CORS middleware
   - Create Dockerfile and docker-compose

2. **Database & Models**
   - Create SQLAlchemy models (Users, Decks, Simulations, Configs)
   - Setup Alembic migrations
   - Create database indexes

3. **Authentication System**
   - JWT-based authentication
   - Password hashing (bcrypt)
   - Register/Login endpoints
   - Protected route decorator

4. **Deck Management API**
   - CRUD endpoints for decks
   - CSV import/export
   - Deck validation
   - Store deck data as JSONB

5. **Configuration Management API**
   - CRUD endpoints for simulation configs
   - Default config support
   - Validation

6. **Refactor Simulation Core**
   - Extract `madness.py` functions into modular services
   - Make simulation engine importable and testable
   - Add progress callbacks
   - Remove command-line dependencies

7. **Basic Simulation API**
   - POST endpoint to start simulation
   - Store simulation in database
   - Queue Celery task
   - GET endpoint for status/results

8. **Celery Tasks**
   - Create `run_simulation_task`
   - Progress tracking with Redis
   - Error handling
   - Result storage in database

**Deliverables:**
- Working FastAPI backend
- Deck and simulation CRUD APIs
- Celery workers running simulations
- Basic authentication

**Testing:**
- Unit tests for API endpoints
- Integration tests for simulation tasks
- Test database migrations

---

### Phase 2: Frontend Foundation (Weeks 3-5)

**Goal:** Build React frontend with deck editor and basic simulation UI

**Tasks:**
1. **Setup React Project**
   - Initialize Vite + React + TypeScript
   - Configure TailwindCSS
   - Setup routing (React Router)
   - Configure Axios with interceptors
   - Setup TanStack Query

2. **Authentication UI**
   - Login page
   - Register page
   - JWT token storage (localStorage)
   - Protected routes
   - Auth context/hooks

3. **Layout & Navigation**
   - Header with user menu
   - Sidebar navigation
   - Responsive layout
   - Toast notifications

4. **Deck Editor**
   - Deck list view (all user decks)
   - Create/edit/delete decks
   - Card row component with inline editing
   - Add/remove cards
   - Card search/autocomplete
   - Import from CSV/text
   - Export to CSV
   - Validation messages

5. **Configuration Editor**
   - Edit simulation config
   - Key cards editor
   - Ideal setups editor
   - Mulligan strategy editor
   - Save/load configs

6. **Basic Simulation UI**
   - Simulation form (select deck, set parameters)
   - Start simulation
   - Simulation history list
   - Basic results view (tables)

**Deliverables:**
- Functional deck editor
- Config editor
- Basic simulation UI
- Authentication flow

**Testing:**
- Component tests (Vitest + React Testing Library)
- E2E tests for critical flows (Playwright)

---

### Phase 3: Real-Time Progress & Results (Weeks 5-6)

**Goal:** Add WebSocket support for real-time progress and rich results visualization

**Tasks:**
1. **Backend WebSocket Support**
   - WebSocket endpoint for simulations
   - Redis pub/sub for progress updates
   - Update Celery tasks to publish progress
   - Handle WebSocket disconnections

2. **Frontend WebSocket Integration**
   - WebSocket service/hook
   - Connect to simulation WebSocket
   - Real-time progress bar
   - Auto-reconnect on disconnect

3. **Results Dashboard**
   - Card stats table (sortable, filterable)
   - Key card stats table
   - Ideal setups table
   - Mulligan distribution chart
   - Opening hands table
   - Graveyard/Battlefield stats
   - Madness/Flashback/Tutored stats

4. **Data Visualization**
   - Success rate charts (Recharts)
   - Mulligan distribution pie chart
   - Turn-by-turn progression
   - Interactive tooltips
   - Export to Excel button

**Deliverables:**
- Real-time progress updates
- Comprehensive results dashboard
- Interactive charts
- Excel export

---

### Phase 4: Experiments & Comparisons (Weeks 6-8)

**Goal:** Add experiment and comparison features

**Tasks:**
1. **Experiment Backend**
   - Refactor experiment runner for web
   - Create Experiment model and API
   - Celery tasks for experiments
   - Progress tracking for multi-variant experiments
   - Results storage

2. **Experiment UI**
   - Experiment configuration form
   - Support for all experiment types:
     - Replace quantity
     - Slot testing
     - Land ratio
     - Combinatorial
   - Real-time progress (multi-variant)
   - Results with variant rankings
   - Top variants comparison view

3. **Comparison Backend**
   - Refactor deck comparison for web
   - Create Comparison model and API
   - Celery tasks for comparisons
   - Delta calculations

4. **Comparison UI**
   - Select two decks to compare
   - Real-time progress
   - Delta visualization (green/red indicators)
   - Side-by-side pattern comparison
   - Insights generation
   - Impact ranking

**Deliverables:**
- Full experiment system
- Deck comparison tool
- Advanced visualizations

---

### Phase 5: Advanced Features (Weeks 8-10)

**Goal:** Add advanced features and polish

**Tasks:**
1. **Sideboard Support**
   - Sideboard plan editor
   - Pre-board vs post-board comparison
   - Matchup-specific configs

2. **Public Deck Sharing**
   - Make decks public
   - Browse public decks
   - Duplicate/fork decks

3. **Results Sharing**
   - Generate shareable links
   - Public results page (no login required)
   - Expiring shares
   - View count tracking

4. **Advanced Deck Editor**
   - Drag-and-drop reordering
   - Bulk card operations
   - Card images (Scryfall API)
   - Mana curve visualization
   - Color distribution pie chart

5. **User Dashboard**
   - Recent simulations/experiments
   - Quick stats
   - Favorite decks
   - Activity history

6. **Performance Optimizations**
   - Database query optimization
   - Redis caching for results
   - Frontend code splitting
   - Lazy loading

7. **Mobile Responsiveness**
   - Mobile-friendly deck editor
   - Touch-optimized UI
   - Responsive tables
   - Mobile navigation

**Deliverables:**
- Polished, production-ready app
- Mobile support
- Sharing features
- Performance optimizations

---

### Phase 6: Deployment & Production (Weeks 10-12)

**Goal:** Deploy to production and add monitoring

**Tasks:**
1. **Infrastructure Setup**
   - Setup production database (PostgreSQL on Railway/Supabase)
   - Setup Redis (Redis Cloud/Upstash)
   - Configure S3 for file storage
   - Setup CI/CD pipeline (GitHub Actions)

2. **Backend Deployment**
   - Deploy to Render/Railway/AWS
   - Configure environment variables
   - Setup Celery workers (multiple instances)
   - Configure autoscaling
   - SSL certificates

3. **Frontend Deployment**
   - Build optimized production bundle
   - Deploy to Vercel/Netlify
   - Configure custom domain
   - CDN optimization

4. **Monitoring & Logging**
   - Setup Sentry for error tracking
   - Add application logging
   - Database performance monitoring
   - Celery task monitoring
   - Uptime monitoring (UptimeRobot)

5. **Security Hardening**
   - Rate limiting (API endpoints)
   - CORS configuration
   - SQL injection prevention
   - XSS protection
   - HTTPS enforcement

6. **Documentation**
   - API documentation (Swagger)
   - User guide
   - Developer documentation
   - Deployment guide

**Deliverables:**
- Production deployment
- Monitoring and alerting
- Security hardening
- Documentation

---

## Key Technical Decisions

### 1. Handling Long-Running Simulations

**Challenge:** Simulations can take 30s to 2+ minutes depending on parameters.

**Solution:**
- Use Celery to run simulations in background workers
- Return immediately with job ID
- Client polls for status or connects via WebSocket
- Store progress in Redis (0-100%)
- Support cancellation (revoke Celery task)

**WebSocket Flow:**
```
Client                  Backend                  Celery Worker
  |                        |                            |
  |-- POST /simulations -->|                            |
  |<---- {id, status} -----|                            |
  |                        |---- queue task ----------->|
  |                        |                            |
  |-- WS connect ---------->|                            |
  |                        |                            |
  |                        |<--- progress update(10%)----|
  |<---- progress(10%) ----|                            |
  |                        |<--- progress update(50%)----|
  |<---- progress(50%) ----|                            |
  |                        |<--- complete --------------|
  |<---- complete ---------|                            |
  |-- WS disconnect ------->|                            |
```

### 2. Storing Results

**Challenge:** Results are large (11+ sheets of data per simulation).

**Options:**
1. **PostgreSQL JSONB** (chosen for MVP)
   - Pros: Simple, queryable, no extra infrastructure
   - Cons: Large JSONB fields, potential size limits
   
2. **S3 + Database pointer**
   - Pros: Scalable, no size limits
   - Cons: More complex, additional cost
   
3. **Hybrid**: Store summary in DB, full results in S3

**Decision:** Start with JSONB, migrate to hybrid if needed.

### 3. Excel Export in Browser

**Challenge:** Current system generates Excel files server-side with openpyxl.

**Options:**
1. **Server-side generation** (chosen)
   - Generate Excel on demand
   - Stream file to client
   - Cache generated files (S3)
   
2. **Client-side generation**
   - Use SheetJS (xlsx library)
   - Generate in browser
   - Pros: No server load
   - Cons: Large library size

**Decision:** Server-side for MVP, client-side as optimization.

### 4. Parallel Experiment Execution

**Challenge:** Experiments test 10-50+ variants in parallel.

**Solution:**
- Launch multiple Celery tasks (one per variant)
- Use Celery groups for coordination
- Track overall experiment progress
- Aggregate results when all complete
- Support multiple Celery workers for true parallelism

### 5. Authentication Strategy

**Options:**
1. **JWT tokens** (chosen)
   - Stateless
   - Works well with REST APIs
   - Access token (15 min) + Refresh token (7 days)
   
2. **Session-based**
   - Server-side sessions
   - Requires sticky sessions or Redis

**Decision:** JWT for simplicity and scalability.

### 6. Database vs. Redis for Progress

**Redis Advantages:**
- Fast writes for frequent progress updates
- TTL for automatic cleanup
- Pub/Sub for WebSocket broadcasting

**PostgreSQL Advantages:**
- Persistent progress history
- Queryable

**Decision:** Use Redis for active progress, persist to PostgreSQL on completion.

---

## Development Environment Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker (optional but recommended)

### Backend Setup

```bash
# 1. Clone repository
cd madnesscarlo

# 2. Create backend directory
mkdir backend
cd backend

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic redis celery pydantic python-jose[cryptography] passlib[bcrypt] python-multipart

# 5. Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/madnesscarlo
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
EOF

# 6. Initialize database
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 7. Run backend
uvicorn app.main:app --reload --port 8000

# 8. Run Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
# 1. Create frontend directory
cd ..
mkdir frontend
cd frontend

# 2. Initialize React + TypeScript project
npm create vite@latest . -- --template react-ts

# 3. Install dependencies
npm install axios @tanstack/react-query zustand react-router-dom react-hook-form recharts
npm install -D tailwindcss postcss autoprefixer @types/node
npx tailwindcss init -p

# 4. Install shadcn/ui
npx shadcn-ui@latest init

# 5. Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF

# 6. Run frontend
npm run dev
```

### Docker Setup (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: madnesscarlo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/madnesscarlo
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/madnesscarlo
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: celery -A app.tasks.celery_app worker --loglevel=info

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
```

---

## Migration Checklist

### Pre-Migration
- [ ] Review current codebase thoroughly
- [ ] Identify all features to migrate
- [ ] Create development environment
- [ ] Setup version control branches (dev, staging, main)
- [ ] Define success metrics

### Backend Migration
- [ ] Setup FastAPI project structure
- [ ] Configure database (PostgreSQL)
- [ ] Create database models
- [ ] Setup database migrations (Alembic)
- [ ] Configure Redis connection
- [ ] Setup Celery workers
- [ ] Implement authentication (JWT)
- [ ] Create deck management API
- [ ] Create config management API
- [ ] Refactor simulation core for web
- [ ] Create simulation API endpoints
- [ ] Implement Celery tasks for simulations
- [ ] Add WebSocket support
- [ ] Refactor experiment runner
- [ ] Create experiment API endpoints
- [ ] Implement Celery tasks for experiments
- [ ] Refactor deck comparison
- [ ] Create comparison API endpoints
- [ ] Implement Excel export
- [ ] Add API documentation (Swagger)
- [ ] Write backend tests
- [ ] Setup error handling and logging

### Frontend Development
- [ ] Setup React + TypeScript project
- [ ] Configure routing
- [ ] Setup API client (Axios)
- [ ] Configure state management (Zustand)
- [ ] Configure data fetching (TanStack Query)
- [ ] Setup TailwindCSS + shadcn/ui
- [ ] Implement authentication pages
- [ ] Create layout components
- [ ] Build deck editor
- [ ] Build deck list view
- [ ] Implement CSV import/export
- [ ] Build config editor
- [ ] Build simulation form
- [ ] Build simulation results dashboard
- [ ] Add real-time progress (WebSocket)
- [ ] Build data visualization charts
- [ ] Build experiment UI
- [ ] Build comparison UI
- [ ] Implement sharing functionality
- [ ] Add mobile responsiveness
- [ ] Write frontend tests

### Testing
- [ ] Unit tests for backend services
- [ ] Integration tests for API endpoints
- [ ] E2E tests for critical user flows
- [ ] Performance testing for simulations
- [ ] Load testing for concurrent users
- [ ] Security testing (authentication, authorization)
- [ ] Cross-browser testing
- [ ] Mobile device testing

### Deployment
- [ ] Setup production database
- [ ] Setup Redis instance
- [ ] Configure S3 for file storage
- [ ] Setup CI/CD pipeline
- [ ] Deploy backend to hosting service
- [ ] Deploy Celery workers
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Configure custom domain
- [ ] Setup SSL certificates
- [ ] Configure environment variables
- [ ] Setup monitoring (Sentry, logs)
- [ ] Setup database backups
- [ ] Configure rate limiting
- [ ] Security audit

### Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] User guide
- [ ] Developer documentation
- [ ] Deployment guide
- [ ] Contributing guidelines
- [ ] Changelog

### Post-Launch
- [ ] Monitor error rates
- [ ] Monitor performance metrics
- [ ] Gather user feedback
- [ ] Plan feature iterations
- [ ] Regular security updates

---

## Estimated Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1: Core Backend** | 3 weeks | FastAPI backend, basic simulation API, Celery workers |
| **Phase 2: Frontend Foundation** | 2 weeks | Deck editor, config editor, basic simulation UI |
| **Phase 3: Real-Time & Results** | 1 week | WebSocket progress, results dashboard, charts |
| **Phase 4: Experiments & Comparisons** | 2 weeks | Full experiment system, deck comparison |
| **Phase 5: Advanced Features** | 2 weeks | Sharing, sideboard, polish, optimizations |
| **Phase 6: Deployment** | 2 weeks | Production deployment, monitoring, documentation |
| **Total** | **12 weeks** | Full-featured web application |

**Note:** Timeline assumes 1 developer working full-time. Adjust accordingly for team size and availability.

---

## Budget Estimates (Monthly Costs)

### Development (Local)
- **Cost:** $0 (use Docker for local Postgres/Redis)

### Production (Small Scale - <1000 users)
- **Hosting (Railway):** $20-50/month
  - Backend API + Workers
  - PostgreSQL (1GB)
  - Redis (256MB)
- **Frontend (Vercel):** $0 (free tier)
- **Monitoring (Sentry):** $0 (free tier, 5k errors/month)
- **Domain:** $12/year
- **Total:** ~$30-60/month

### Production (Medium Scale - 1000-10k users)
- **Hosting (Railway/Render):** $100-200/month
  - Scaled backend + workers
  - PostgreSQL (5GB)
  - Redis (1GB)
- **Frontend (Vercel):** $0-20/month
- **S3 Storage:** $5-20/month
- **Monitoring:** $29/month (Sentry paid)
- **Total:** ~$150-270/month

### Production (Large Scale - 10k+ users)
- **AWS/GCP:** $500-2000+/month
- Consider managed services at scale

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Long simulation times** | High | High | Use WebSocket for progress, set timeouts, optimize algorithm |
| **Database performance** | Medium | High | Use indexes, Redis caching, consider read replicas |
| **Celery worker crashes** | Medium | Medium | Implement retry logic, monitoring, autoscaling |
| **Concurrent user load** | Low | High | Load testing, autoscaling, rate limiting |
| **Excel export performance** | Medium | Low | Cache generated files, async generation |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Low user adoption** | Medium | High | MVP validation, user feedback early |
| **Hosting costs exceed budget** | Low | Medium | Start with cheap tier, optimize before scaling |
| **Feature creep** | High | Medium | Stick to phased plan, prioritize ruthlessly |

---

## Success Metrics

### Technical Metrics
- [ ] API response time < 200ms (p95)
- [ ] Simulation completion < 2 minutes (1000 runs)
- [ ] WebSocket latency < 100ms
- [ ] Frontend load time < 2 seconds
- [ ] 95% test coverage (backend)
- [ ] Zero critical security vulnerabilities

### User Metrics
- [ ] User registration rate
- [ ] Daily active users (DAU)
- [ ] Average simulations per user
- [ ] Feature usage rates
- [ ] User retention (week 1, week 4)
- [ ] Net Promoter Score (NPS)

### Business Metrics
- [ ] Time to complete simulation (vs CLI)
- [ ] User satisfaction score
- [ ] Monthly recurring users
- [ ] Conversion rate (visitor → registered user)

---

## Future Enhancements (Post-MVP)

### Phase 7+
1. **Advanced Analytics**
   - Historical tracking of deck changes
   - Performance trends over time
   - Meta-game analysis

2. **Collaboration Features**
   - Teams and shared workspaces
   - Comment on results
   - Real-time collaborative editing

3. **AI-Powered Insights**
   - LLM analysis of results (already have prompts!)
   - Automated deck suggestions
   - Pattern recognition

4. **Tournament Support**
   - Multiple matchup testing
   - Swiss pairing simulation
   - Tournament meta analysis

5. **Mobile App**
   - Native iOS/Android app
   - Offline mode for viewing results
   - Push notifications

6. **Premium Features**
   - Unlimited simulations
   - Priority processing
   - Advanced analytics
   - Longer result retention

7. **Community Features**
   - Public deck database
   - Rating/voting system
   - Deck categories/tags
   - User profiles

8. **Integration**
   - Import from popular deck sites (MTGGoldfish, Archidekt)
   - Export to TappedOut, Moxfield
   - Discord bot integration

---

## Conclusion

This migration plan provides a comprehensive roadmap for transforming the MTG Madness Carlo Simulator from a command-line tool into a modern web application. The phased approach ensures incremental progress with testable milestones, while the technology choices leverage Python's strengths and modern web development best practices.

**Key Advantages of Web App:**
- ✅ Accessible from any device with a browser
- ✅ No installation required
- ✅ Real-time collaboration and sharing
- ✅ Visual deck editing
- ✅ Interactive results visualization
- ✅ Saved history and configurations
- ✅ Mobile support

**Estimated Effort:** 12 weeks (1 developer full-time)  
**Estimated Cost:** $30-60/month (small scale)  
**Tech Stack:** FastAPI + React + PostgreSQL + Redis + Celery

The plan is designed to be executed incrementally, allowing for early validation and iteration based on user feedback. Each phase delivers tangible value, making it possible to launch an MVP after Phase 3 (6 weeks) if needed.

