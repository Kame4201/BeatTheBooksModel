# BeatTheBooksModel - Claude AI Documentation

This file provides comprehensive context about the BeatTheBooksModel project for AI assistants and developers.

## Project Overview

**BeatTheBooksModel** is a Python FastAPI application that scrapes NFL data from Pro-Football-Reference.com and stores it in a PostgreSQL database for analysis and modeling.

### Technology Stack
- **Language**: Python 3.13+
- **Framework**: FastAPI (REST API)
- **Database**: PostgreSQL (Neon.tech hosted)
- **ORM**: SQLAlchemy
- **Web Scraping**: Selenium, BeautifulSoup4, Requests
- **Data Processing**: Pandas
- **Testing**: Pytest
- **Validation**: Pydantic

---

## Project Structure

```
BeatTheBooksModel/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│       ├── claude-code-review.yml
│       └── claude.yml
├── docs/                       # Documentation (see docs/README.md)
│   ├── architecture/          # Architecture documentation
│   ├── sdlc/                  # SDLC best practices
│   └── agents/                # AI agent role documentation
├── src/                       # Source code
│   ├── core/                  # Core functionality
│   │   └── database.py       # Database connection
│   ├── entities/              # SQLAlchemy ORM models
│   │   ├── base.py           # Base entity class
│   │   ├── team_game.py      # Team game entity
│   │   ├── team_offense.py   # Team offense entity
│   │   ├── scraped_data.py   # Scraped data metadata entity
│   │   └── ...               # Other stat entities
│   ├── dtos/                  # Pydantic DTOs (Data Transfer Objects)
│   │   ├── team_game_dto.py
│   │   └── scraped_data_dto.py
│   ├── repositories/          # Data access layer
│   │   ├── base_repo.py      # Base repository pattern
│   │   ├── team_game_repo.py
│   │   ├── scraped_data_repo.py
│   │   └── ...               # Other repositories
│   ├── services/              # Business logic layer
│   │   ├── scrape_service.py        # Selenium-based scraper
│   │   ├── team_offense_service.py  # Team offense scraping
│   │   └── excel_scraper_service.py # Excel URL scraper
│   ├── main.py               # FastAPI application entry point
│   └── requirements.txt      # Python dependencies
├── tests/                    # Test suite
│   ├── test_excel_scraper.py     # Unit tests
│   ├── test_integration.py       # Integration tests
│   └── conftest.py               # Pytest fixtures
├── pytest.ini                # Pytest configuration
├── CLAUDE.md                 # This file
├── TESTING.md                # Testing guide
└── README.md                 # Project README

```

---

## Architecture Layers

This project follows a **3-tier architecture** with clear separation of concerns:

### 1. **Presentation Layer** (API)
- **Location**: `src/main.py`
- **Responsibilities**: HTTP endpoints, request/response handling
- **Framework**: FastAPI

### 2. **Business Logic Layer** (Services)
- **Location**: `src/services/`
- **Responsibilities**: Business rules, data transformation, scraping logic
- **Pattern**: Service pattern

### 3. **Data Access Layer** (Repositories)
- **Location**: `src/repositories/`
- **Responsibilities**: Database operations, queries
- **Pattern**: Repository pattern

### 4. **Domain Layer** (Entities & DTOs)
- **Entities** (`src/entities/`): Database models (SQLAlchemy)
- **DTOs** (`src/dtos/`): Data validation and transfer (Pydantic)

**See**: `docs/architecture/` for detailed architecture documentation.

---

## Key Dependencies

### Core
```python
fastapi==0.129.0           # Web framework
uvicorn==0.40.0            # ASGI server
sqlalchemy==2.0.46         # ORM
psycopg2-binary==2.9.11    # PostgreSQL driver
pydantic==2.12.5           # Data validation
```

### Web Scraping
```python
selenium==4.40.0           # Browser automation
beautifulsoup4==4.14.3     # HTML parsing
requests==2.32.5           # HTTP client
lxml==6.0.2                # XML/HTML parser
```

### Data Processing
```python
pandas==3.0.0              # Data manipulation
openpyxl==3.1.5            # Excel file handling
```

### Testing
```python
pytest==9.0.2              # Testing framework
pytest-asyncio==1.3.0      # Async test support
```

**See**: `src/requirements.txt` for full dependency list.

---

## Database Schema

### Connection
- **Host**: Neon.tech (ep-purple-glade-adlsv7d9-pooler.c-2.us-east-1.aws.neon.tech)
- **Database**: neondb
- **ORM**: SQLAlchemy

### Key Tables

#### Static Entities (Pre-defined)
- `team_game` - Individual team game records
- `team_offense` - Team offensive statistics
- `defense_stats` - Defensive statistics
- `passing_stats`, `rushing_stats`, `receiving_stats` - Player stats
- `kicking_stats`, `punting_stats`, `return_stats` - Special teams

#### Dynamic Entities (Created at runtime)
- `scraped_data_metadata` - Tracks scraping operations
- `scraped_*` - Dynamically created tables for scraped data

**See**: `docs/architecture/database-schema.md` for detailed schema.

---

## Development Workflow

### ⚠️ IMPORTANT: Never Commit Directly to Main

This project follows **GitFlow** workflow:

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. **Push to remote**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request**
   - Never merge your own PR
   - Wait for code review
   - Address feedback
   - Merge after approval

**See**: `docs/sdlc/git-workflow.md` for detailed Git workflow.

---

## API Endpoints

### Health Check
```http
GET /
Returns: {"Hello": "World"}
```

### Scraping Endpoints

#### 1. Scrape Team Data (Selenium-based)
```http
GET /scrape/{team}/{year}
Example: GET /scrape/buf/2024
```
- Uses Selenium to avoid bot detection
- Scrapes team schedule and stats
- Stores in `team_game` table

#### 2. Scrape Team Offense Stats
```http
GET /scrape/{year}
Example: GET /scrape/2024
```
- Scrapes league-wide offensive stats
- Stores in `team_offense` table

#### 3. Scrape from Excel File
```http
POST /scrape/excel?excel_path=/path/to/file.xlsx
```
- Reads URLs from Excel file
- Scrapes multiple pages
- Creates dynamic tables
- Tracks metadata in `scraped_data_metadata`

**See**: `docs/architecture/api-endpoints.md` for detailed API documentation.

---

## Testing

### Unit Tests
```bash
pytest tests/test_excel_scraper.py -v
```
- Fast, no database required
- Mocked dependencies
- Tests business logic

### Integration Tests
```bash
pytest tests/test_integration.py -v -s
```
- Requires database connection
- Real HTTP requests
- End-to-end testing

**See**: `TESTING.md` for comprehensive testing guide.

---

## AI Agent Roles

This project supports multiple AI agent workflows:

### 1. **Code Review Agent**
- **Workflow**: `.github/workflows/claude-code-review.yml`
- **Role**: Automated PR code review
- **Trigger**: Pull request opened/updated

### 2. **Development Agent**
- **Role**: Feature development, bug fixes
- **Best Practices**:
  - Always create feature branches
  - Never commit to main
  - Write tests for new features
  - Follow existing patterns

### 3. **Testing Agent**
- **Role**: Test creation and execution
- **Responsibilities**: Unit tests, integration tests, test coverage

**See**: `docs/agents/` for detailed agent documentation.

---

## Software Development Lifecycle (SDLC)

### Branch Strategy
- `main` - Production-ready code (protected)
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Code Review Process
1. Create feature branch
2. Implement changes
3. Write tests
4. Open pull request
5. Code review (required)
6. Address feedback
7. Merge to main
8. Delete feature branch

### CI/CD Pipeline
- **On PR**: Code review, tests run
- **On Merge**: Deploy (if configured)

**See**: `docs/sdlc/` for detailed SDLC documentation.

---

## Coding Standards

### Python Style
- **Style Guide**: PEP 8
- **Formatter**: black (if configured)
- **Linter**: pylint/flake8 (if configured)

### Architecture Patterns
1. **Repository Pattern** for data access
2. **Service Pattern** for business logic
3. **DTO Pattern** for data validation
4. **Dependency Injection** where appropriate

### Best Practices
- ✅ Use type hints
- ✅ Write docstrings
- ✅ Handle errors gracefully
- ✅ Log important events
- ✅ Write tests
- ❌ Never hardcode credentials
- ❌ Never commit to main directly

---

## Common Tasks

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/Kame4201/BeatTheBooksModel.git
cd BeatTheBooksModel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r src/requirements.txt

# Run tests
pytest
```

### Start Development Server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_excel_scraper.py -v

# With coverage
pytest --cov=src --cov-report=html
```

### Create New Feature
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, commit
git add .
git commit -m "Add my feature"

# Push and create PR
git push origin feature/my-feature
gh pr create --title "Add my feature" --body "Description"
```

---

## Documentation

- **Architecture**: See `docs/architecture/`
- **SDLC**: See `docs/sdlc/`
- **Agents**: See `docs/agents/`
- **Testing**: See `TESTING.md`
- **API**: See `docs/architecture/api-endpoints.md`

---

## Important Notes

### Database Connection
- The database auto-suspends after inactivity
- Wake it up at: https://console.neon.tech
- Connection string is in `src/core/database.py`

### Web Scraping
- Pro-Football-Reference blocks automated requests
- Use 60-second delays between requests
- Selenium works better than requests library
- Respect robots.txt

### Security
- Never commit `DATABASE_URL` or credentials
- Use environment variables for secrets
- Keep `.env` in `.gitignore`

---

## Contact & Support

- **Repository**: https://github.com/Kame4201/BeatTheBooksModel
- **Issues**: Open GitHub issues for bugs/features
- **Documentation**: Check `docs/` folder

---

## Quick Reference

```bash
# Development
uvicorn src.main:app --reload

# Testing
pytest

# Scraping
curl http://localhost:8000/scrape/buf/2024

# Git Workflow
git checkout -b feature/name
git commit -m "message"
git push origin feature/name
gh pr create
```

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Python**: 3.13+
**Framework**: FastAPI 0.129.0
