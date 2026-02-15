# Development Agent Role

## Overview

The Development Agent is an AI assistant (Claude) responsible for implementing features, fixing bugs, and maintaining code quality in the BeatTheBooksModel project.

---

## Primary Responsibilities

### 1. Feature Implementation
- Implement new features as specified in GitHub issues
- Follow existing architectural patterns
- Write clean, maintainable code
- Add comprehensive error handling

### 2. Bug Fixes
- Investigate and resolve reported bugs
- Root cause analysis
- Write regression tests
- Document fixes

### 3. Code Quality
- Follow PEP 8 style guidelines
- Write docstrings and type hints
- Ensure code is DRY (Don't Repeat Yourself)
- Maintain consistent patterns

### 4. Testing
- Write unit tests for new code
- Create integration tests
- Ensure tests pass before committing
- Maintain test coverage

### 5. Documentation
- Update CLAUDE.md with changes
- Document new endpoints in API docs
- Add inline comments where needed
- Update README if necessary

---

## Development Workflow

### Step 1: Understand the Task

```markdown
**Before coding:**
- Read the GitHub issue thoroughly
- Understand requirements and acceptance criteria
- Ask clarifying questions if needed
- Review related code and documentation
```

### Step 2: Create Feature Branch

```bash
# Always work on a feature branch, never on main
git checkout main
git pull origin main
git checkout -b feature/issue-number-description

# Examples:
# git checkout -b feature/14-excel-url-scraper
# git checkout -b bugfix/15-fix-403-errors
# git checkout -b docs/16-update-api-docs
```

### Step 3: Implement Following Architecture

**Always follow the 3-tier architecture:**

```
1. Create/Update Entity (if needed)
   └─> src/entities/

2. Create/Update DTO (if needed)
   └─> src/dtos/

3. Create/Update Repository (if needed)
   └─> src/repositories/

4. Create/Update Service
   └─> src/services/

5. Create/Update API Endpoint
   └─> src/main.py

6. Write Tests
   └─> tests/
```

**Example workflow:**

```python
# Step 1: Entity (src/entities/player.py)
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))

# Step 2: DTO (src/dtos/player_dto.py)
class PlayerCreate(BaseModel):
    name: str
    team_id: int

# Step 3: Repository (src/repositories/player_repo.py)
class PlayerRepository(BaseRepository[Player]):
    def find_by_team(self, team_id: int):
        return self.db.query(Player).filter_by(team_id=team_id).all()

# Step 4: Service (src/services/player_service.py)
class PlayerService:
    def __init__(self, repo: PlayerRepository):
        self.repo = repo

    def get_team_players(self, team_id: int):
        return self.repo.find_by_team(team_id)

# Step 5: Endpoint (src/main.py)
@app.get("/teams/{team_id}/players")
def get_players(team_id: int):
    service = PlayerService(PlayerRepository(SessionLocal()))
    return service.get_team_players(team_id)

# Step 6: Tests (tests/test_player_service.py)
def test_get_team_players():
    # Test implementation
    pass
```

### Step 4: Test Locally

```bash
# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_player_service.py -v

# Run with coverage
pytest tests/ --cov=src

# Manual testing
python src/main.py
# Or
uvicorn src.main:app --reload
```

### Step 5: Commit Changes

```bash
# Stage changes
git add src/entities/player.py
git add src/dtos/player_dto.py
git add src/repositories/player_repo.py
git add src/services/player_service.py
git add src/main.py
git add tests/test_player_service.py

# Commit with descriptive message
git commit -m "feat: add player management functionality

- Created Player entity for database mapping
- Added PlayerCreate DTO for validation
- Implemented PlayerRepository for data access
- Created PlayerService with business logic
- Added GET /teams/{team_id}/players endpoint
- Added comprehensive unit tests

Closes #23

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 6: Push and Create PR

```bash
# Push to remote
git push origin feature/23-player-management

# Create PR
gh pr create --title "feat: Add player management functionality" --body "$(cat <<'EOF'
## Summary
Implements player management functionality allowing retrieval of players by team.

## Changes
- Created `Player` entity for database mapping
- Added `PlayerCreate` DTO for validation
- Implemented `PlayerRepository` for data access
- Created `PlayerService` with business logic
- Added `GET /teams/{team_id}/players` endpoint
- Added comprehensive unit tests (8 tests)

## Type of Change
- [x] New feature
- [ ] Bug fix
- [x] Documentation
- [ ] Refactoring
- [x] Test additions

## Testing
- [x] Unit tests pass (8/8)
- [x] Integration test created
- [x] Manually tested

**Test Results:**
```
8 passed in 2.34s
```

## Architecture
- Follows repository pattern
- Uses DTOs for data validation
- Proper separation of concerns (service/repository layers)

Closes #23

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Architectural Guidelines

### ❌ DON'T: Direct SQL in Service Layer

```python
# BAD - Service contains SQL
def scrape_url(url):
    db.execute("INSERT INTO data VALUES ...")
```

### ✅ DO: Use Repository Pattern

```python
# GOOD - Service uses repository
def scrape_url(url):
    data = fetch_data(url)
    repo.save(data)

# Repository handles database
class DataRepository:
    def save(self, data):
        self.db.execute("INSERT INTO data VALUES ...")
```

### ❌ DON'T: Mix Responsibilities

```python
# BAD - Endpoint contains business logic and database calls
@app.get("/teams/{team_id}")
def get_team(team_id: int):
    # Business logic in endpoint
    team = db.query(Team).filter_by(id=team_id).first()
    stats = db.query(TeamStats).filter_by(team_id=team_id).all()
    # Complex calculations
    avg_points = sum(s.points for s in stats) / len(stats)
    return {"team": team, "avg_points": avg_points}
```

### ✅ DO: Separate Concerns

```python
# GOOD - Each layer has one responsibility

# Endpoint (presentation)
@app.get("/teams/{team_id}")
def get_team(team_id: int):
    service = TeamService(TeamRepository(SessionLocal()))
    return service.get_team_stats(team_id)

# Service (business logic)
class TeamService:
    def get_team_stats(self, team_id: int):
        team = self.repo.find_by_id(team_id)
        stats = self.repo.find_stats(team_id)
        avg_points = self._calculate_average(stats)
        return {"team": team, "avg_points": avg_points}

# Repository (data access)
class TeamRepository:
    def find_by_id(self, team_id: int):
        return self.db.query(Team).filter_by(id=team_id).first()
```

---

## Code Quality Standards

### 1. Docstrings

```python
def scrape_from_excel(excel_path: str) -> Dict[str, Any]:
    """
    Scrape Pro-Football-Reference URLs from an Excel file.

    Reads URLs from an Excel file and scrapes each URL sequentially
    with 60-second delays between requests. Creates dynamic database
    tables based on scraped data structure.

    Args:
        excel_path (str): Path to Excel file containing URLs

    Returns:
        Dict[str, Any]: Summary of scraping results with keys:
            - urls_processed (int): Total URLs attempted
            - urls_success (int): Successfully scraped URLs
            - urls_failed (int): Failed URLs
            - tables_extracted (int): Number of tables found
            - rows_inserted (int): Total rows added to database
            - errors (List[str]): Error messages for failed URLs

    Raises:
        FileNotFoundError: If Excel file doesn't exist
        ValueError: If Excel file missing required 'url' column

    Example:
        >>> result = scrape_from_excel("data/urls.xlsx")
        >>> print(f"Processed {result['urls_processed']} URLs")
    """
    # Implementation...
```

### 2. Type Hints

```python
from typing import List, Optional, Dict, Any

# Good
def get_players(team_id: int, season: Optional[int] = None) -> List[Player]:
    pass

# Bad (no type hints)
def get_players(team_id, season=None):
    pass
```

### 3. Error Handling

```python
# Good - Specific exceptions, logging, graceful handling
def scrape_url(url: str) -> DataFrame:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error scraping {url}: {e}")
        raise
    except requests.exceptions.Timeout:
        logger.error(f"Timeout scraping {url}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error scraping {url}: {e}")
        raise

# Bad - Bare except, no logging
def scrape_url(url):
    try:
        response = requests.get(url)
    except:
        pass
```

### 4. Input Validation

```python
# Good - Validate inputs
def get_team_stats(team_id: int, season: int) -> Dict:
    if team_id < 1:
        raise ValueError("team_id must be positive")
    if not (1920 <= season <= 2100):
        raise ValueError("season must be between 1920 and 2100")
    # Implementation...

# Bad - No validation
def get_team_stats(team_id, season):
    # Implementation...
```

---

## Testing Guidelines

### Unit Tests

```python
# tests/test_player_service.py
import pytest
from src.services.player_service import PlayerService
from src.repositories.player_repo import PlayerRepository

def test_get_team_players():
    """Test retrieving players for a specific team."""
    # Arrange
    mock_repo = MockPlayerRepository()
    service = PlayerService(mock_repo)

    # Act
    players = service.get_team_players(team_id=1)

    # Assert
    assert len(players) == 3
    assert players[0].name == "Patrick Mahomes"

def test_get_team_players_empty():
    """Test retrieving players when team has none."""
    mock_repo = MockPlayerRepository(players=[])
    service = PlayerService(mock_repo)

    players = service.get_team_players(team_id=999)

    assert players == []
```

### Integration Tests

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_scrape_real_excel():
    """Test full scraping workflow with real database."""
    excel_path = "tests/fixtures/test_urls.xlsx"

    result = await scrape_from_excel(excel_path)

    assert result['urls_processed'] > 0
    assert result['urls_success'] >= 0
    assert 'errors' in result
```

---

## Common Tasks

### Adding a New Endpoint

1. Define entity (if new table needed)
2. Create DTO for validation
3. Build repository for data access
4. Implement service with business logic
5. Add API endpoint
6. Write tests
7. Update API documentation

### Fixing a Bug

1. Reproduce the bug
2. Write a failing test
3. Fix the bug
4. Verify test passes
5. Check for similar issues elsewhere
6. Commit with descriptive message

### Refactoring Code

1. Ensure tests exist and pass
2. Make refactoring changes
3. Verify tests still pass
4. No functional changes (tests should not change)
5. Commit with "refactor:" prefix

---

## Tools & Commands

### Running the Application

```bash
# Development mode (auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_player_service.py::test_get_team_players -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

---

## Communication

### With Users
- Be clear and concise
- Explain technical decisions
- Ask clarifying questions when needed
- Provide progress updates

### In Commit Messages
- Use conventional commits format
- Explain why, not just what
- Reference issue numbers

### In Code Comments
- Explain why, not what
- Document complex logic
- Don't over-comment obvious code

---

## Decision-Making Framework

### When to Create a New File
- ✅ New entity/model
- ✅ New service with distinct responsibility
- ✅ New repository for new entity
- ❌ One-off helper function (add to existing file)

### When to Refactor
- ✅ Code duplication (DRY principle)
- ✅ Function too complex (>50 lines)
- ✅ Poor separation of concerns
- ❌ Working code that's just "not perfect"

### When to Add Dependencies
- ✅ Well-maintained, popular libraries
- ✅ Solves significant problem
- ✅ No suitable alternative in stdlib
- ❌ Unmaintained packages
- ❌ Tiny utility functions (write yourself)

---

## Learning & Improvement

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PEP 8 Style Guide](https://pep8.org/)

### Continuous Improvement
- Learn from code reviews
- Read project documentation
- Understand existing patterns
- Ask questions when unsure

---

## Related Documentation

- [Code Review Guidelines](../sdlc/code-review.md)
- [Git Workflow](../sdlc/git-workflow.md)
- [Pull Request Guide](../sdlc/pull-request-guide.md)
- [Architecture Overview](../architecture/overview.md)

---

**Remember**: Write code that your future self (and other developers) will thank you for! 🚀

**Last Updated**: February 2026
