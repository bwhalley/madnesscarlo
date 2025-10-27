# MTG Madness Carlo: Web Application Project Plan

## Executive Summary

**Project:** Convert MTG Madness Carlo Simulator from CLI to Web Application  
**Timeline:** 12 weeks (3 months)  
**Team Size:** 1 developer (full-time) or 2-3 developers (part-time)  
**Budget:** $30-50/month (hosting) + development time  

---

## 🎯 Project Goals

### Primary Objectives
1. **Accessibility** - Make simulator accessible via web browser (no installation)
2. **User Experience** - Provide visual deck editor and interactive results
3. **Collaboration** - Enable deck sharing and results sharing
4. **Mobile Support** - Full responsive design for phones/tablets
5. **Feature Parity** - Maintain all existing CLI functionality

### Success Metrics
- ✅ Setup time: 15 minutes → 30 seconds
- ✅ User satisfaction: 8+/10
- ✅ Mobile usage: 20%+ of sessions
- ✅ Sharing rate: 30%+ of results
- ✅ Simulation speed: Equal to CLI (±10%)

---

## 🛠 Technology Stack

### Backend Technologies

#### Core Framework
```yaml
Framework: FastAPI 0.104+
- Modern async Python web framework
- Automatic OpenAPI/Swagger documentation
- Native WebSocket support
- High performance (comparable to Node.js)
- Type hints with Pydantic validation

Python Version: 3.11+
- Latest stable Python
- Performance improvements
- Better error messages
```

#### Database Layer
```yaml
Primary Database: PostgreSQL 14+
- Stores: users, decks, configs, simulations, experiments
- JSONB support for flexible data (simulation results)
- Strong ACID guarantees
- Excellent performance

ORM: SQLAlchemy 2.0+
- Python SQL toolkit
- Async support
- Type-safe queries

Migrations: Alembic 1.12+
- Database version control
- Automatic migration generation
- Safe schema changes
```

#### Caching & Job Queue
```yaml
Cache/Queue: Redis 7+
- Session storage
- Job queue backend
- Real-time progress tracking
- Cache layer for results
- Pub/Sub for WebSocket broadcasting

Task Queue: Celery 5.3+
- Background job processing
- Distributed task execution
- Parallel simulation execution
- Progress tracking
- Retry logic and error handling
```

#### Authentication & Security
```yaml
Authentication: JWT (JSON Web Tokens)
- Stateless authentication
- Access tokens (15 min expiry)
- Refresh tokens (7 day expiry)

Libraries:
- python-jose: JWT encoding/decoding
- passlib: Password hashing (bcrypt)
- python-multipart: File upload support
```

#### Additional Backend Libraries
```yaml
Data Processing:
- pandas==2.3.3 (existing)
- openpyxl==3.1.5 (existing)
- numpy==2.0+ (if needed)

API & Middleware:
- uvicorn: ASGI server
- python-dotenv: Environment variables
- pydantic-settings: Configuration management
- python-cors: CORS middleware

Monitoring & Logging:
- sentry-sdk: Error tracking
- structlog: Structured logging
- prometheus-client: Metrics (optional)
```

### Frontend Technologies

#### Core Framework
```yaml
Framework: React 18+
- Component-based architecture
- Virtual DOM for performance
- Large ecosystem
- Industry standard

Language: TypeScript 5+
- Type safety
- Better IDE support
- Fewer runtime errors
- Self-documenting code

Build Tool: Vite 5+
- Fast dev server (instant HMR)
- Optimized production builds
- Modern ES modules
- Better than Create React App
```

#### State Management & Data Fetching
```yaml
State Management: Zustand
- Lightweight (1KB)
- Simple API
- No boilerplate
- Perfect for small-medium apps

Data Fetching: TanStack Query (React Query) 5+
- Automatic caching
- Background refetching
- Optimistic updates
- Request deduplication
- Pagination support

HTTP Client: Axios 1.6+
- Promise-based
- Interceptors for auth
- Request/response transformation
- Error handling
```

#### Routing & Forms
```yaml
Routing: React Router 6+
- Declarative routing
- Nested routes
- Protected routes
- URL parameters

Forms: React Hook Form 7+
- Performant (uncontrolled)
- Easy validation
- TypeScript support
- Small bundle size
```

#### UI & Styling
```yaml
Styling: TailwindCSS 3+
- Utility-first CSS
- Highly customizable
- Small production bundle
- Responsive by default

Component Library: shadcn/ui
- Copy-paste components (not NPM package)
- Built on Radix UI primitives
- Accessible by default
- Customizable with Tailwind

Icons: Lucide React
- Modern icon library
- Tree-shakeable
- Consistent design
```

#### Data Visualization
```yaml
Charts: Recharts 2+
- React-native charts
- Composable
- Responsive
- Good documentation

Alternatives considered:
- Victory: More features but larger
- Chart.js: Canvas-based (less React-native)
- D3.js: Too low-level for this use case
```

#### Additional Frontend Libraries
```yaml
Utilities:
- date-fns: Date manipulation
- clsx: Conditional classNames
- zod: Runtime validation

Development:
- Vitest: Unit testing
- React Testing Library: Component testing
- Playwright: E2E testing
- ESLint: Linting
- Prettier: Code formatting
```

### WebSocket Technology
```yaml
Backend: FastAPI WebSocket support
- Native async WebSocket
- Connection management
- Broadcasting via Redis Pub/Sub

Frontend: Native WebSocket API
- Built into browsers
- Wrapped in React hooks
- Automatic reconnection
- Heartbeat/ping-pong
```

---

## 🏗 Infrastructure Requirements

### Development Environment

#### Local Development
```yaml
Required Software:
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (recommended)
- Git

Development Tools:
- VS Code (recommended IDE)
- Postman/Insomnia (API testing)
- TablePlus/pgAdmin (database GUI)
- Redis Commander (Redis GUI)

Environment Variables:
- DATABASE_URL
- REDIS_URL
- SECRET_KEY
- CORS_ORIGINS
```

#### Docker Setup (Recommended)
```yaml
Containers:
- postgres:14-alpine (database)
- redis:7-alpine (cache/queue)
- Backend container (Python app)
- Celery worker container
- Frontend container (development)

Volumes:
- postgres_data (persistent)
- redis_data (persistent)

Networks:
- Internal network for containers
```

### Production Infrastructure

#### Hosting Options

**Option 1: Railway (Recommended for MVP)**
```yaml
Platform: Railway.app
Cost: $20-50/month

Services:
- Web Service (FastAPI + Uvicorn)
  - Auto-scaling
  - 512MB-1GB RAM
  - 0.5-1 vCPU
  
- Celery Worker Service
  - Dedicated worker dyno
  - 1GB RAM
  - 1 vCPU
  
- PostgreSQL Database
  - Managed PostgreSQL
  - 1GB storage (starter)
  - Automatic backups
  
- Redis Instance
  - Managed Redis
  - 256MB memory
  - Persistence enabled

Pros:
+ Simple deployment (git push)
+ Integrated database/Redis
+ Automatic SSL certificates
+ Good free tier to start
+ Fair pricing

Cons:
- Newer platform (less mature)
- Limited regions
```

**Option 2: Render**
```yaml
Platform: Render.com
Cost: $25-75/month

Services:
- Web Service (FastAPI)
  - $7/month (starter)
  - Auto-deploy from git
  
- Background Worker (Celery)
  - $7/month (starter)
  
- PostgreSQL
  - $7/month (1GB)
  - Daily backups
  
- Redis
  - $10/month (256MB)

Pros:
+ Reliable platform
+ Good documentation
+ Auto-scaling available
+ Multiple regions

Cons:
- Slightly more expensive
- Separate billing for each service
```

**Option 3: AWS (For Scale)**
```yaml
Platform: Amazon Web Services
Cost: $100-500+/month (depends on usage)

Services:
- ECS/Fargate (Container hosting)
  - FastAPI service
  - Celery workers (auto-scaling)
  
- RDS PostgreSQL
  - db.t3.micro or larger
  - Multi-AZ for production
  
- ElastiCache Redis
  - cache.t3.micro
  
- Application Load Balancer
  - SSL termination
  - Health checks
  
- S3 (File storage)
  - Excel exports
  - Static assets
  
- CloudWatch (Monitoring)
  - Logs and metrics

Pros:
+ Highly scalable
+ Full control
+ Many features
+ Global infrastructure

Cons:
- Complex setup
- More expensive
- Requires AWS expertise
- Overkill for MVP
```

**Option 4: DigitalOcean**
```yaml
Platform: DigitalOcean
Cost: $50-150/month

Services:
- App Platform (FastAPI + Celery)
  - $12/month per service
  
- Managed PostgreSQL
  - $15/month (1GB RAM)
  
- Managed Redis
  - $15/month (1GB RAM)

Pros:
+ Simple and reliable
+ Good documentation
+ Predictable pricing
+ Developer-friendly

Cons:
- Less feature-rich than AWS
- Limited auto-scaling
```

#### Frontend Hosting

**Option 1: Vercel (Recommended)**
```yaml
Platform: Vercel
Cost: $0 (Free tier sufficient)

Features:
- Automatic deployments from git
- Global CDN
- SSL certificates
- Preview deployments
- Build optimization
- Edge functions (if needed)
- 100GB bandwidth/month (free)

Deployment:
- Push to GitHub
- Automatic build & deploy
- Custom domain support
```

**Option 2: Netlify**
```yaml
Platform: Netlify
Cost: $0 (Free tier sufficient)

Features:
- Git-based deployments
- Global CDN
- SSL certificates
- Form handling
- 100GB bandwidth/month
- Deploy previews

Deployment:
- Connect GitHub repo
- Configure build command
- Automatic deployments
```

**Option 3: Cloudflare Pages**
```yaml
Platform: Cloudflare Pages
Cost: $0 (Free tier very generous)

Features:
- Unlimited bandwidth
- Unlimited requests
- Global CDN (excellent performance)
- SSL certificates
- Git integration

Pros:
+ Best performance (Cloudflare CDN)
+ Most generous free tier
+ Easy setup
```

### Database & Storage

#### Database Specifications
```yaml
Development:
- PostgreSQL 14+ via Docker
- 100MB storage sufficient
- No replication needed

Production (Small - <1000 users):
- PostgreSQL 14+
- 1-5GB storage
- Daily automated backups
- Point-in-time recovery (optional)

Production (Medium - 1k-10k users):
- PostgreSQL 14+
- 10-50GB storage
- Hourly backups
- Read replicas (optional)
- Connection pooling (PgBouncer)

Production (Large - 10k+ users):
- PostgreSQL 14+
- 100GB+ storage
- Multi-AZ deployment
- Read replicas (required)
- Connection pooling
- Performance monitoring
```

#### Redis Specifications
```yaml
Development:
- Redis 7+ via Docker
- 256MB memory
- No persistence needed

Production (Small):
- Redis 7+
- 256MB-512MB memory
- RDB persistence enabled
- No clustering needed

Production (Medium):
- Redis 7+
- 1-2GB memory
- AOF persistence
- Sentinel for HA (optional)

Production (Large):
- Redis 7+
- 4GB+ memory
- Redis Cluster
- AOF persistence
- Sentinel for HA
```

#### File Storage (Optional)
```yaml
Use Case: Store large Excel exports

Development:
- Local filesystem

Production:
- AWS S3 (recommended)
  - $0.023/GB/month
  - 99.999999999% durability
  - CDN via CloudFront
  
- Alternatives:
  - Cloudflare R2 ($0.015/GB, no egress fees)
  - DigitalOcean Spaces ($5/250GB)
  - Backblaze B2 ($0.005/GB)

Implementation:
- Store Excel files > 10MB in S3
- Store smaller results in PostgreSQL JSONB
- Pre-signed URLs for downloads
- 24-hour expiration
```

### CI/CD Pipeline

#### GitHub Actions (Recommended)
```yaml
Workflows:
1. Backend Tests
   - Trigger: Push to main, pull requests
   - Steps: Lint, test, coverage report
   
2. Frontend Tests
   - Trigger: Push to main, pull requests
   - Steps: Lint, type-check, test, build
   
3. Deploy Backend
   - Trigger: Push to main (after tests pass)
   - Steps: Build Docker image, push to registry, deploy
   
4. Deploy Frontend
   - Trigger: Push to main (after tests pass)
   - Steps: Build, deploy to Vercel/Netlify

Free Tier:
- 2000 minutes/month (sufficient)
- Private repos included
```

#### Alternative: GitLab CI
```yaml
Similar to GitHub Actions
- Integrated with GitLab
- More generous free tier (10k minutes)
- Built-in Docker registry
```

### Monitoring & Logging

#### Error Tracking
```yaml
Platform: Sentry
Cost: $0 (free tier: 5k errors/month)

Features:
- Real-time error tracking
- Source map support
- Breadcrumbs
- Release tracking
- Performance monitoring
- User feedback

Integration:
- Backend: sentry-sdk
- Frontend: @sentry/react
```

#### Application Monitoring
```yaml
Logging:
- structlog (Python)
- Console logs (JavaScript)
- Centralized logs in hosting platform

Metrics:
- Prometheus + Grafana (if needed)
- Built-in platform metrics
- Custom business metrics

Uptime Monitoring:
- UptimeRobot (free tier)
- Pingdom
- Better Uptime
```

### Security Infrastructure

#### SSL/TLS Certificates
```yaml
Provider: Let's Encrypt (free)
- Automatic renewal
- Provided by hosting platforms
- No manual configuration needed
```

#### Secrets Management
```yaml
Development:
- .env files (git-ignored)
- .env.example template

Production:
- Platform environment variables
- Railway/Render secrets
- AWS Secrets Manager (if AWS)
```

#### Rate Limiting
```yaml
Implementation:
- FastAPI slowapi middleware
- Redis-backed rate limiting
- IP-based limits
- User-based limits (authenticated)

Limits:
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Simulation endpoints: 10 concurrent/user
```

### Backup Strategy

#### Database Backups
```yaml
Automated:
- Daily full backups (managed by hosting)
- Point-in-time recovery (7-30 days)
- Stored in separate region

Manual:
- Weekly exports to S3 (optional)
- Pre-deployment snapshots
```

#### Application Backups
```yaml
Code:
- Git repository (primary backup)
- GitHub (cloud backup)

Configuration:
- Version controlled
- Secrets documented (not stored)
```

---

## 📅 Project Timeline

### Phase 1: Backend Foundation (Weeks 1-3)

**Week 1: Project Setup & Database**
```yaml
Tasks:
- Setup FastAPI project structure
- Configure PostgreSQL with SQLAlchemy
- Create database models (Users, Decks, Simulations)
- Setup Alembic migrations
- Configure Redis connection
- Setup development Docker Compose

Deliverables:
- Working local development environment
- Database schema implemented
- Health check endpoint
- API documentation (auto-generated)

Technologies Used:
- FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Docker
```

**Week 2: Authentication & Deck Management**
```yaml
Tasks:
- Implement JWT authentication
- Create user registration/login endpoints
- Implement password hashing
- Create Deck CRUD endpoints
- Add CSV import/export
- Implement deck validation

Deliverables:
- Authentication system working
- Deck management API complete
- Protected routes implemented
- API tests written

Technologies Used:
- python-jose, passlib, FastAPI dependencies
```

**Week 3: Simulation Integration & Celery**
```yaml
Tasks:
- Refactor madness.py for API integration
- Create simulation endpoints
- Setup Celery workers
- Implement background task execution
- Add progress tracking with Redis
- Basic WebSocket for progress

Deliverables:
- Simulations can be started via API
- Background processing working
- Progress tracking functional
- Results stored in database

Technologies Used:
- Celery, Redis, WebSocket, existing simulation code
```

### Phase 2: Frontend Foundation (Weeks 3-5)

**Week 3-4: React Setup & Authentication UI**
```yaml
Tasks:
- Setup React + TypeScript + Vite
- Configure TailwindCSS
- Setup React Router
- Implement authentication pages (login/register)
- Create protected routes
- Setup Axios with JWT interceptors
- Setup TanStack Query

Deliverables:
- React app running
- Authentication flow working
- JWT token management
- API client configured

Technologies Used:
- React, TypeScript, Vite, TailwindCSS, Axios, React Router
```

**Week 4-5: Deck Editor & List**
```yaml
Tasks:
- Create deck list view
- Build deck editor component
- Implement card search/autocomplete
- Add/remove/edit cards
- CSV import dialog
- Mana curve visualization
- Color distribution chart

Deliverables:
- Visual deck editor working
- Deck CRUD operations in UI
- Import/export functionality
- Basic validation

Technologies Used:
- React Hook Form, Recharts, shadcn/ui components
```

**Week 5: Simulation UI**
```yaml
Tasks:
- Create simulation setup form
- Display simulation history
- Basic results view (tables)
- Configuration editor UI

Deliverables:
- Can start simulations from UI
- View simulation history
- Basic results display

Technologies Used:
- React components, TanStack Query, forms
```

### Phase 3: Real-Time Features (Weeks 5-6)

**Week 6: WebSocket & Results Dashboard**
```yaml
Tasks:
- Enhance WebSocket implementation
- Real-time progress component
- Interactive results dashboard
- All 11 result sheets as components
- Interactive charts (Recharts)
- Excel export button

Deliverables:
- Real-time progress updates
- Comprehensive results dashboard
- Interactive data visualization
- Export functionality

Technologies Used:
- WebSocket, Recharts, React components
```

### Phase 4: Advanced Features (Weeks 6-8)

**Week 7: Experiments Backend & UI**
```yaml
Tasks:
- Refactor experiment_runner.py for API
- Create experiment endpoints
- Multi-variant Celery tasks
- Experiment configuration UI
- Experiment progress (multi-variant)
- Results with rankings

Deliverables:
- Experiments working via API
- Visual experiment builder
- Real-time multi-variant progress
- Ranked results display

Technologies Used:
- Celery groups, existing experiment code, React
```

**Week 8: Deck Comparison**
```yaml
Tasks:
- Refactor deck_comparison.py for API
- Comparison endpoints
- Comparison UI
- Delta visualization (green/red)
- Side-by-side comparison charts

Deliverables:
- Deck comparison functional
- Visual delta display
- Interactive comparison charts

Technologies Used:
- Existing comparison code, Recharts, React
```

### Phase 5: Polish & Features (Weeks 8-10)

**Week 9: Sharing & Mobile**
```yaml
Tasks:
- Shareable results links
- Public results page
- Make decks public
- Mobile responsive design
- Touch-friendly UI
- Navigation improvements

Deliverables:
- Sharing functionality working
- Fully responsive design
- Good mobile experience

Technologies Used:
- TailwindCSS responsive classes, React
```

**Week 10: Configuration & Sideboard**
```yaml
Tasks:
- Configuration editor (full)
- Ideal setups editor
- Mulligan strategy editor
- Sideboard plans editor
- Performance optimizations
- Loading states
- Error boundaries

Deliverables:
- Complete configuration management
- Sideboard support
- Polished UX
- Error handling

Technologies Used:
- React Hook Form, validation, UI components
```

### Phase 6: Deployment (Weeks 10-12)

**Week 11: Infrastructure & Deployment**
```yaml
Tasks:
- Setup production database (Railway/Render)
- Setup production Redis
- Configure environment variables
- Deploy backend to production
- Deploy Celery workers
- Deploy frontend to Vercel
- Configure custom domain
- Setup SSL certificates

Deliverables:
- Production environment live
- Backend deployed and accessible
- Frontend deployed
- HTTPS working

Technologies Used:
- Railway/Render, Vercel, DNS configuration
```

**Week 12: Monitoring & Launch**
```yaml
Tasks:
- Setup Sentry error tracking
- Configure logging
- Setup uptime monitoring
- Performance testing
- Security audit
- Write user documentation
- Beta testing
- Launch!

Deliverables:
- Monitoring in place
- Documentation complete
- Production-ready application
- Launched to users

Technologies Used:
- Sentry, UptimeRobot, documentation tools
```

---

## 💰 Budget Breakdown

### Development Costs

**Option 1: Self-Development**
```yaml
Cost: $0 (your time)
Time: 12 weeks full-time
     or 24 weeks part-time (20 hrs/week)
     or 36 weeks side-project (10-15 hrs/week)
```

**Option 2: Contract Development**
```yaml
Rate: $50-100/hour (varies by location)
Hours: ~480 hours (12 weeks × 40 hours)
Cost: $24,000 - $48,000

Alternative: Fixed price project: $20,000 - $40,000
```

### Infrastructure Costs

**Development (Local)**
```yaml
Cost: $0/month
- Run everything locally via Docker
- PostgreSQL: Local container
- Redis: Local container
```

**Production: Small Scale (<1000 users)**
```yaml
Recommended Stack: Railway + Vercel

Railway:
- Web service (FastAPI): $10-15/month
- Worker service (Celery): $10-15/month
- PostgreSQL: $5-10/month
- Redis: $5-10/month
Subtotal: $30-50/month

Vercel:
- Frontend hosting: $0/month (free tier)

Additional:
- Domain name: $12/year ($1/month)
- Sentry: $0/month (free tier)

Total: $31-51/month
```

**Production: Medium Scale (1k-10k users)**
```yaml
Recommended Stack: Render + Vercel

Render:
- Web service: $25/month
- Worker service (2 instances): $50/month
- PostgreSQL (upgraded): $20/month
- Redis (upgraded): $20/month
Subtotal: $115/month

Vercel:
- Frontend: $20/month (Pro plan)

Storage:
- S3 for exports: $10/month

Monitoring:
- Sentry: $29/month
- Better Uptime: $10/month

Total: $184/month
```

**Production: Large Scale (10k+ users)**
```yaml
Recommended Stack: AWS

AWS Costs (estimated):
- ECS Fargate (API): $100/month
- ECS Fargate (Workers, auto-scaling): $200/month
- RDS PostgreSQL (db.t3.medium): $100/month
- ElastiCache Redis: $50/month
- Application Load Balancer: $25/month
- S3 + CloudFront: $30/month
- CloudWatch: $20/month
Subtotal: $525/month

Vercel:
- Frontend: $20/month

Monitoring:
- Sentry: $99/month (Business)
- Datadog: $150/month (optional)

Total: $644-794/month
```

### First Year Total Cost Estimates

**Scenario 1: Solo Developer + Small Scale**
```yaml
Development: $0 (self-built)
Year 1 Hosting: $31/month × 12 = $372
Domain: $12
Total First Year: $384
```

**Scenario 2: Contract Dev + Medium Scale**
```yaml
Development: $30,000 (one-time)
Year 1 Hosting: $184/month × 12 = $2,208
Domain: $12
Total First Year: $32,220
```

---

## 🏛 Architecture Diagram

```
┌─────────────────── USERS ───────────────────┐
│                                              │
│  💻 Desktop    📱 Mobile    🖥 Tablet       │
│     Browser       Browser      Browser      │
└──────────────────┬───────────────────────────┘
                   │
                   │ HTTPS
                   │
┌──────────────────▼───────────────────────────┐
│         FRONTEND (Vercel/Netlify)            │
│                                              │
│  React + TypeScript + TailwindCSS            │
│  • Deck Editor                               │
│  • Simulation UI                             │
│  • Results Dashboard                         │
│  • Charts (Recharts)                         │
│                                              │
│  Deployment: Vercel (git push)               │
│  CDN: Global edge network                    │
│  Cost: Free tier                             │
└──────────────────┬───────────────────────────┘
                   │
                   │ REST API / WebSocket
                   │
┌──────────────────▼───────────────────────────┐
│      BACKEND API (Railway/Render/AWS)        │
│                                              │
│  FastAPI + Python 3.11                       │
│  • Authentication (JWT)                      │
│  • Deck CRUD                                 │
│  • Simulation Orchestration                  │
│  • Experiment Management                     │
│  • WebSocket Server                          │
│                                              │
│  Workers: Uvicorn (async)                    │
│  Deployment: Docker container                │
│  Auto-scaling: Available                     │
└──────┬────────────┬──────────────┬───────────┘
       │            │              │
       │            │              │
       │            │              └─────────────┐
       │            │                            │
       │            │                            │
┌──────▼────────┐ ┌▼────────────┐ ┌─────────────▼─────┐
│  PostgreSQL   │ │   Redis     │ │  Celery Workers   │
│               │ │             │ │                   │
│  • Users      │ │ • Sessions  │ │  • Simulations    │
│  • Decks      │ │ • Cache     │ │  • Experiments    │
│  • Results    │ │ • Job Queue │ │  • Comparisons    │
│  • Configs    │ │ • Progress  │ │                   │
│               │ │ • Pub/Sub   │ │  Existing Python  │
│  Managed DB   │ │             │ │  simulation code  │
│  Backups: Yes │ │ Managed     │ │                   │
└───────────────┘ └─────────────┘ │  Workers: 2-4     │
                                  │  Auto-scale: Yes  │
                                  └───────────────────┘
                                           │
                                           │
                                  ┌────────▼────────┐
                                  │   S3 Storage    │
                                  │                 │
                                  │  Excel Exports  │
                                  │  (Optional)     │
                                  └─────────────────┘

┌────────────────── MONITORING ────────────────┐
│                                              │
│  Sentry (Error Tracking)                     │
│  UptimeRobot (Uptime Monitoring)             │
│  Platform Logs (Railway/Render)              │
└──────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

### Authentication & Authorization
```yaml
Strategy: JWT tokens
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Secure HTTP-only cookies (optional)
- CORS properly configured

Password Security:
- bcrypt hashing (cost factor: 12)
- Minimum password length: 8 characters
- Password strength validation

Authorization:
- User can only access their own data
- Public decks accessible to all
- Shared results: token-based access
```

### API Security
```yaml
Rate Limiting:
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour
- Simulation: 10 concurrent per user

Input Validation:
- Pydantic schemas (backend)
- Zod schemas (frontend)
- SQL injection prevention (ORM)
- XSS prevention (React escaping)

HTTPS:
- Force HTTPS in production
- HSTS headers
- Secure cookies
```

### Data Security
```yaml
Encryption:
- TLS 1.3 in transit
- Database encryption at rest (platform-managed)
- Sensitive config in environment variables

Privacy:
- Decks private by default
- User email not exposed in API
- Results shareable with token
- GDPR considerations (if EU users)
```

---

## 📊 Success Metrics & KPIs

### Technical Metrics
```yaml
Performance:
- API response time (p95): <200ms
- Simulation speed: Equal to CLI ±10%
- Frontend load time: <2 seconds
- WebSocket latency: <100ms

Reliability:
- Uptime: >99.5% (target: 99.9%)
- Error rate: <1%
- Failed background jobs: <2%

Scalability:
- Concurrent users: 100+ (initial)
- Concurrent simulations: 50+
- Database size: <5GB (year 1)
```

### User Metrics
```yaml
Adoption:
- New users/month: 10+
- Daily active users: 20+
- Weekly active users: 50+

Engagement:
- Average session duration: >10 min
- Simulations per user/month: 5+
- Decks per user: 3+

Satisfaction:
- User satisfaction score: >8/10
- Task completion rate: >90%
- Feature usage: All features used
```

### Business Metrics
```yaml
Growth:
- User growth rate: 20% MoM
- Retention (week 1): >60%
- Retention (month 1): >40%

Cost Efficiency:
- Cost per user: <$1/month
- Infrastructure cost: <20% of budget

Sharing:
- Shared results rate: >30%
- Public decks: >10% of total
```

---

## 🚧 Risk Management

### Technical Risks

**Risk 1: Performance Degradation**
```yaml
Risk: Web version slower than CLI
Likelihood: Low
Impact: High

Mitigation:
- Use same Python engine
- Optimize database queries
- Add Redis caching
- Monitor performance metrics
- Load testing before launch

Contingency:
- Optimize hot paths
- Add more workers
- Database query optimization
```

**Risk 2: Concurrent User Load**
```yaml
Risk: Too many concurrent simulations
Likelihood: Medium (as users grow)
Impact: Medium

Mitigation:
- Queue management with Celery
- Rate limiting per user
- Worker auto-scaling
- Queue priority system

Contingency:
- Add more workers
- Implement job priority
- Add user limits
```

**Risk 3: Database Size**
```yaml
Risk: Results data grows too large
Likelihood: Medium
Impact: Medium

Mitigation:
- Store full results in JSONB (efficient)
- Archive old results (>6 months)
- Option to move large files to S3
- Data retention policy

Contingency:
- Implement result expiration
- Move to S3 storage
- Upgrade database tier
```

### Business Risks

**Risk 4: Low User Adoption**
```yaml
Risk: Users prefer CLI
Likelihood: Low
Impact: High

Mitigation:
- Keep CLI working (both options)
- Beta testing with real users
- Gather feedback early
- Focus on ease of use

Contingency:
- Hybrid approach (both tools)
- Improve UX based on feedback
```

**Risk 5: Infrastructure Costs**
```yaml
Risk: Costs exceed budget
Likelihood: Low
Impact: Medium

Mitigation:
- Start with cheap tier
- Monitor costs daily
- Set billing alerts
- Optimize before scaling

Contingency:
- Downgrade services
- Optimize performance
- Implement usage limits
```

---

## ✅ Acceptance Criteria

### MVP Requirements (Phase 1-3 Complete)

**Must Have:**
- [ ] User registration and login
- [ ] Visual deck editor
- [ ] CSV import/export
- [ ] Run basic simulations
- [ ] View results (all 11 sheets)
- [ ] Real-time progress
- [ ] Save deck history
- [ ] Mobile responsive

**Performance:**
- [ ] Simulations run at CLI speed
- [ ] API responds in <200ms
- [ ] Frontend loads in <2s

**Testing:**
- [ ] 80%+ test coverage
- [ ] All critical paths tested
- [ ] E2E tests pass

### Full Release Requirements (All Phases Complete)

**Additional Features:**
- [ ] Experiments system
- [ ] Deck comparison
- [ ] Sharing functionality
- [ ] Configuration management
- [ ] Sideboard support

**Production Ready:**
- [ ] Deployed to production
- [ ] Monitoring configured
- [ ] Backups working
- [ ] Documentation complete
- [ ] Security audit passed

**User Validated:**
- [ ] Beta testing complete
- [ ] User feedback incorporated
- [ ] User satisfaction >8/10

---

## 📖 Deliverables

### Code Deliverables
1. ✅ Backend API (FastAPI)
2. ✅ Frontend App (React + TypeScript)
3. ✅ Database migrations (Alembic)
4. ✅ Docker Compose setup
5. ✅ CI/CD pipeline (GitHub Actions)
6. ✅ Test suite (80%+ coverage)

### Documentation Deliverables
1. ✅ API documentation (auto-generated Swagger)
2. ✅ User guide
3. ✅ Developer documentation
4. ✅ Deployment guide
5. ✅ Architecture documentation

### Infrastructure Deliverables
1. ✅ Production environment (Railway/Render)
2. ✅ Database (PostgreSQL)
3. ✅ Cache/Queue (Redis)
4. ✅ Frontend hosting (Vercel)
5. ✅ Monitoring (Sentry)
6. ✅ Backups configured

---

## 🎯 Next Steps

### Immediate Actions (This Week)

1. **Review and Approve Plan**
   - Review this document
   - Identify any concerns
   - Get stakeholder buy-in

2. **Setup Development Environment**
   - Install required software
   - Clone repository
   - Follow Quick Start Guide

3. **Create Project Structure**
   ```bash
   mkdir backend frontend
   cd backend && python -m venv venv
   cd ../frontend && npm create vite@latest . -- --template react-ts
   ```

4. **Setup Project Management**
   - Create GitHub project
   - Create issues for Phase 1
   - Setup milestone tracking

### Week 1 Kickoff

1. **Backend Foundation**
   - Initialize FastAPI project
   - Setup Docker Compose
   - Create first API endpoint
   - Connect to PostgreSQL

2. **Database Design**
   - Create SQLAlchemy models
   - Generate first migration
   - Test database connection

3. **Basic Authentication**
   - Implement JWT generation
   - Create registration endpoint
   - Create login endpoint

### Regular Checkpoints

**Weekly:**
- Review progress against timeline
- Update project board
- Address blockers
- Adjust timeline if needed

**Bi-weekly:**
- Demo working features
- Gather feedback
- Update documentation
- Deploy to staging

**Monthly:**
- Review metrics
- Check budget
- Adjust priorities
- Plan next phase

---

## 📞 Support & Resources

### Key Documentation
- [Full Migration Plan](./WEB_APP_MIGRATION_PLAN.md)
- [Quick Start Guide](./WEBAPP_QUICK_START.md)
- [UI Wireframes](./WEBAPP_UI_WIREFRAMES.md)
- [CLI vs Web Comparison](./WEBAPP_COMPARISON_SUMMARY.md)

### Technology Documentation
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- PostgreSQL: https://www.postgresql.org/docs
- Celery: https://docs.celeryproject.org
- TailwindCSS: https://tailwindcss.com

### Recommended Learning Resources
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial
- React TypeScript: https://react-typescript-cheatsheet.netlify.app
- Celery Best Practices: https://docs.celeryproject.org/en/stable/userguide
- PostgreSQL Performance: https://wiki.postgresql.org/wiki/Performance_Optimization

---

## 📝 Project Summary

### What We're Building
A web-based version of the MTG Madness Carlo Simulator that makes deck testing accessible to everyone through a browser, with visual editing, real-time progress, and easy sharing.

### Why It Matters
- **Accessibility**: No installation required
- **User Experience**: Visual interface vs command line
- **Collaboration**: Easy sharing and public decks
- **Mobile**: Works on phones and tablets
- **Growth**: Lower barrier to entry = more users

### Technology Choice Rationale
- **FastAPI**: Modern, fast, async Python framework perfect for our use case
- **React**: Industry standard, great ecosystem, component-based
- **PostgreSQL**: Robust, JSONB support for flexible data
- **Celery**: Proven background job processing for Python
- **Railway/Vercel**: Simple, cost-effective, developer-friendly

### Timeline & Budget
- **Duration**: 12 weeks
- **Cost**: $30-50/month (hosting)
- **Team**: 1 developer full-time (or 2-3 part-time)

### Risk Level
**Low-Medium** - Well-structured existing codebase, proven technologies, clear requirements, 80% code reusability.

---

**Ready to start? Begin with Phase 1, Week 1 tasks!** 🚀

For questions or clarifications, refer to the detailed migration documentation or reach out to the project team.

