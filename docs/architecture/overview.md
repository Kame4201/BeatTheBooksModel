# Architecture Overview

## System Architecture

BeatTheBooksModel follows a **3-tier layered architecture** with clear separation of concerns.

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│      (FastAPI REST Endpoints)           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│           (Services)                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Data Access Layer               │
│    (Repositories & Entities)            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│            Database                     │
│   (PostgreSQL via Neon.tech)            │
└─────────────────────────────────────────┘
```

---

## Architecture Layers

### 1. Presentation Layer (API)

**Location:** `src/main.py`

**Responsibilities:**
- Expose REST API endpoints
- Handle HTTP requests/responses
- Input validation (via Pydantic)
- Route requests to services

**Example:**
```python
@app.post("/scrape/excel")
async def scrape_from_excel_file(excel_path: str):
    """Scrape data from Excel file URLs."""
    results = await excel_scraper_service.scrape_from_excel(excel_path)
    return results
```

**Key Principles:**
- Thin layer - minimal logic
- Delegates to service layer
- Returns DTOs, not entities
- Handles authentication/authorization

---

### 2. Business Logic Layer (Services)

**Location:** `src/services/`

**Responsibilities:**
- Implement business logic
- Orchestrate operations
- Call multiple repositories
- Transform data
- Handle complex workflows

**Example:**
```python
# src/services/excel_scraper_service.py
async def scrape_from_excel(excel_path: str) -> Dict[str, Any]:
    """
    Business logic for Excel scraping workflow:
    1. Read URLs from Excel
    2. Scrape each URL
    3. Extract tables
    4. Store in database
    5. Track metadata
    """
    db = SessionLocal()
    repo = ScrapedDataRepository(db)

    # Business logic here
    for url in urls:
        tables = extract_tables_from_url(url)
        for table in tables:
            repo.create_dynamic_table(table_name, df)
            repo.upsert_dataframe(table_name, df)

    return results
```

**Key Principles:**
- No direct database access
- Uses repositories for data operations
- Returns DTOs or domain objects
- Contains business rules and validations

---

### 3. Data Access Layer (Repositories & Entities)

**Location:**
- Repositories: `src/repositories/`
- Entities: `src/entities/`
- DTOs: `src/dtos/`

#### Repositories

**Responsibilities:**
- Database operations (CRUD)
- Query building
- Transaction management
- Data persistence

**Example:**
```python
# src/repositories/scraped_data_repo.py
class ScrapedDataRepository(BaseRepository[ScrapedData]):
    def create_dynamic_table(self, table_name: str, df: pd.DataFrame):
        """Create a new table based on DataFrame structure."""
        # SQL generation and execution

    def upsert_dataframe(self, table_name: str, df: pd.DataFrame) -> int:
        """Insert or update data from DataFrame."""
        # Bulk upsert logic
```

**Key Principles:**
- Encapsulate all SQL
- No business logic
- Return entities or DTOs
- Handle database connections

#### Entities

**Responsibilities:**
- Map to database tables
- Define schema
- Relationships

**Example:**
```python
# src/entities/scraped_data.py
class ScrapedData(Base):
    __tablename__ = 'scraped_data_metadata'

    id = Column(Integer, primary_key=True)
    source_url = Column(Text, nullable=False)
    table_id = Column(String(255), nullable=False)
    scraped_at = Column(DateTime, default=datetime.now)
```

**Key Principles:**
- Pure data models
- No business logic
- SQLAlchemy models
- Database schema definition

#### DTOs (Data Transfer Objects)

**Responsibilities:**
- Data validation
- API request/response models
- Type safety

**Example:**
```python
# src/dtos/scraped_data_dto.py
class ScrapedDataMetadataCreate(BaseModel):
    source_url: str
    table_id: str
    scraped_at: datetime
    season: Optional[int] = None
```

**Key Principles:**
- Pydantic models
- Validation rules
- Separate from entities
- API contract definition

---

### 4. Database Layer

**Technology:** PostgreSQL (hosted on Neon.tech)

**Connection:** SQLAlchemy ORM

**Configuration:**
```python
# src/core/database.py
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

---

## Design Patterns

### 1. Repository Pattern

**Purpose:** Abstract data access logic

**Structure:**
```
Service Layer
     ↓
Repository Interface
     ↓
Repository Implementation
     ↓
Database
```

**Benefits:**
- Testability (mock repositories)
- Decoupling (swap database easily)
- Maintainability (centralize queries)

**Example:**
```python
# Service uses repository
class TeamOffenseService:
    def __init__(self, repo: TeamOffenseRepository):
        self.repo = repo

    def get_team_stats(self, team_id: int):
        return self.repo.find_by_team_id(team_id)

# Repository handles database
class TeamOffenseRepository(BaseRepository[TeamOffense]):
    def find_by_team_id(self, team_id: int):
        return self.db.query(TeamOffense).filter_by(team_id=team_id).first()
```

### 2. DTO Pattern

**Purpose:** Transfer data between layers

**Benefits:**
- Validation
- Type safety
- API contracts
- Separation from database models

**Example:**
```python
# DTO for API
class TeamGameCreate(BaseModel):
    team_id: int
    game_date: date
    opponent: str

# Entity for database
class TeamGame(Base):
    __tablename__ = 'team_games'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, nullable=False)
    game_date = Column(Date, nullable=False)
```

### 3. Dependency Injection

**Purpose:** Loose coupling, better testing

**Example:**
```python
# Inject repository into service
def get_team_service():
    db = SessionLocal()
    repo = TeamOffenseRepository(db)
    service = TeamOffenseService(repo)
    return service

# Use in endpoint
@app.get("/teams/{team_id}")
def get_team(team_id: int, service: TeamOffenseService = Depends(get_team_service)):
    return service.get_team_stats(team_id)
```

---

## Project Structure

```
BeatTheBooksModel/
├── src/
│   ├── main.py                    # FastAPI application & endpoints
│   ├── core/
│   │   └── database.py           # Database configuration
│   ├── entities/                 # SQLAlchemy models
│   │   ├── base.py
│   │   ├── team_game.py
│   │   ├── team_offense.py
│   │   ├── passing_stats.py
│   │   ├── rushing_stats.py
│   │   ├── receiving_stats.py
│   │   ├── defense_stats.py
│   │   ├── kicking_stats.py
│   │   └── scraped_data.py
│   ├── dtos/                     # Pydantic models
│   │   ├── team_game_dto.py
│   │   └── scraped_data_dto.py
│   ├── repositories/             # Data access layer
│   │   ├── base_repo.py
│   │   ├── team_game_repo.py
│   │   ├── team_offense_repo.py
│   │   ├── passing_stats_repo.py
│   │   └── scraped_data_repo.py
│   └── services/                 # Business logic layer
│       ├── scrape_service.py
│       ├── excel_scraper_service.py
│       └── team_offense_service.py
├── tests/                        # Test suite
│   ├── test_excel_scraper.py
│   └── test_integration.py
├── docs/                         # Documentation
│   ├── architecture/
│   ├── sdlc/
│   └── agents/
├── .github/
│   └── workflows/                # CI/CD pipelines
└── requirements.txt              # Python dependencies
```

---

## Data Flow

### Example: Excel Scraping Workflow

```
1. API Request
   POST /scrape/excel
   Body: { excel_path: "path/to/file.xlsx" }
        ↓
2. Presentation Layer (main.py)
   async def scrape_from_excel_file(excel_path: str)
        ↓
3. Service Layer (excel_scraper_service.py)
   async def scrape_from_excel(excel_path: str)
   - Read Excel file
   - Extract URLs
   - Scrape each URL
        ↓
4. Repository Layer (scraped_data_repo.py)
   - create_dynamic_table()
   - upsert_dataframe()
   - track_scraped_data()
        ↓
5. Database (PostgreSQL)
   - Store scraped data
   - Track metadata
        ↓
6. Response
   {
     "urls_processed": 15,
     "urls_success": 10,
     "urls_failed": 5,
     "errors": [...]
   }
```

---

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for Python
- **Uvicorn**: ASGI server for FastAPI

### Database
- **PostgreSQL**: Relational database (Neon.tech hosted)
- **SQLAlchemy**: Python ORM
- **Alembic**: Database migrations

### Data Processing
- **Pandas**: Data manipulation and analysis
- **Selenium**: Web scraping (JavaScript-heavy sites)
- **BeautifulSoup**: HTML parsing
- **Requests**: HTTP client

### Testing
- **Pytest**: Testing framework
- **pytest-asyncio**: Async test support

### Code Quality
- **Black**: Code formatting
- **Flake8**: Linting
- **Pylint**: Code analysis
- **MyPy**: Type checking

---

## Key Architectural Decisions

### 1. Why Repository Pattern?

**Decision:** Use repository pattern for data access

**Rationale:**
- Testability: Easy to mock repositories in tests
- Maintainability: Centralize database logic
- Flexibility: Easy to swap databases
- Clear separation: Services don't know about SQL

**Example:**
```python
# Without repository (BAD)
def get_team_stats(team_id):
    result = db.execute(f"SELECT * FROM teams WHERE id = {team_id}")
    return result

# With repository (GOOD)
def get_team_stats(team_id):
    return team_repo.find_by_id(team_id)
```

### 2. Why DTOs?

**Decision:** Use Pydantic DTOs for API contracts

**Rationale:**
- Validation: Automatic input validation
- Documentation: OpenAPI schema generation
- Type Safety: Runtime type checking
- Separation: API models separate from database models

### 3. Why 3-Tier Architecture?

**Decision:** Separate presentation, business logic, and data access

**Rationale:**
- Maintainability: Each layer has clear responsibility
- Testability: Test each layer independently
- Scalability: Can scale layers independently
- Flexibility: Easy to modify one layer without affecting others

---

## Common Patterns

### Creating a New Feature

**Steps:**

1. **Define Entity** (if new table needed)
```python
# src/entities/player.py
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

2. **Create DTO**
```python
# src/dtos/player_dto.py
class PlayerCreate(BaseModel):
    name: str
    team_id: int
```

3. **Build Repository**
```python
# src/repositories/player_repo.py
class PlayerRepository(BaseRepository[Player]):
    def find_by_team(self, team_id: int):
        return self.db.query(Player).filter_by(team_id=team_id).all()
```

4. **Implement Service**
```python
# src/services/player_service.py
class PlayerService:
    def __init__(self, repo: PlayerRepository):
        self.repo = repo

    def get_team_players(self, team_id: int):
        return self.repo.find_by_team(team_id)
```

5. **Add Endpoint**
```python
# src/main.py
@app.get("/teams/{team_id}/players")
def get_players(team_id: int):
    service = PlayerService(PlayerRepository(SessionLocal()))
    return service.get_team_players(team_id)
```

---

## Performance Considerations

### Database Optimization
- Use indexes on frequently queried columns
- Batch inserts for large datasets
- Connection pooling
- Query optimization

### Caching Strategy
- Cache frequently accessed data
- Use Redis for distributed caching
- Implement cache invalidation

### Async Operations
- Use async/await for I/O operations
- Parallel scraping with rate limiting
- Non-blocking database queries

---

## Security Considerations

### Input Validation
- Validate all inputs with Pydantic
- Sanitize SQL inputs (use parameterized queries)
- Validate file uploads

### Authentication & Authorization
- API key authentication
- Role-based access control (RBAC)
- JWT tokens for stateless auth

### Data Protection
- Never commit secrets to git
- Use environment variables
- Encrypt sensitive data
- HTTPS only in production

---

## Scalability

### Horizontal Scaling
- Stateless API design
- Load balancer ready
- Database connection pooling

### Vertical Scaling
- Optimize queries
- Use caching
- Async operations

### Future Considerations
- Microservices architecture
- Message queues (RabbitMQ, Kafka)
- Containerization (Docker)
- Orchestration (Kubernetes)

---

## Related Documentation

- [Database Schema](database-schema.md)
- [API Endpoints](api-endpoints.md)
- [Data Flow](data-flow.md)

---

**Last Updated**: February 2026
