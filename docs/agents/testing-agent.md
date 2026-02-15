# Testing Agent Role

## Overview

The Testing Agent is an AI assistant (Claude) responsible for creating, maintaining, and executing tests in the BeatTheBooksModel project.

---

## Primary Responsibilities

### 1. Test Creation
- Write unit tests for new features
- Create integration tests
- Develop end-to-end tests
- Add regression tests for bugs

### 2. Test Maintenance
- Update tests when code changes
- Remove obsolete tests
- Refactor test code
- Fix failing tests

### 3. Test Execution
- Run tests locally
- Monitor CI test results
- Debug test failures
- Analyze test coverage

### 4. Test Quality
- Ensure meaningful assertions
- Test edge cases
- Verify test isolation
- Maintain readable tests

---

## Testing Strategy

### Test Pyramid

```
          /\
         /  \       E2E Tests (Few)
        /----\      - Full workflow
       /      \     - Real database
      /--------\    - Slow (minutes)
     /          \
    /------------\  Integration Tests (Some)
   /              \ - Component interaction
  /----------------\- Test database
 /                  \- Medium (seconds)
/____________________\
    Unit Tests (Many)
    - Single functions
    - Mocked dependencies
    - Fast (milliseconds)
```

**Ratio:** 70% Unit, 20% Integration, 10% E2E

---

## Unit Testing

### Purpose
Test individual functions/methods in isolation

### Example: Service Layer Test

```python
# tests/test_player_service.py
import pytest
from unittest.mock import Mock, MagicMock
from src.services.player_service import PlayerService
from src.entities.player import Player

class TestPlayerService:
    """Unit tests for PlayerService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_repo = Mock()
        self.service = PlayerService(self.mock_repo)

    def test_get_team_players_success(self):
        """Test retrieving players for a team."""
        # Arrange
        mock_players = [
            Player(id=1, name="Player 1", team_id=1),
            Player(id=2, name="Player 2", team_id=1),
        ]
        self.mock_repo.find_by_team.return_value = mock_players

        # Act
        result = self.service.get_team_players(team_id=1)

        # Assert
        assert len(result) == 2
        assert result[0].name == "Player 1"
        self.mock_repo.find_by_team.assert_called_once_with(1)

    def test_get_team_players_empty(self):
        """Test retrieving players when team has none."""
        # Arrange
        self.mock_repo.find_by_team.return_value = []

        # Act
        result = self.service.get_team_players(team_id=999)

        # Assert
        assert result == []
        self.mock_repo.find_by_team.assert_called_once_with(999)

    def test_get_team_players_invalid_id(self):
        """Test with invalid team ID."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="team_id must be positive"):
            self.service.get_team_players(team_id=-1)

    def test_calculate_average_score(self):
        """Test average score calculation."""
        # Arrange
        players = [
            Player(id=1, name="P1", points=100),
            Player(id=2, name="P2", points=200),
            Player(id=3, name="P3", points=150),
        ]

        # Act
        avg = self.service._calculate_average_score(players)

        # Assert
        assert avg == 150.0

    def test_calculate_average_score_empty_list(self):
        """Test average score with no players."""
        # Arrange
        players = []

        # Act
        avg = self.service._calculate_average_score(players)

        # Assert
        assert avg == 0.0
```

### Best Practices

#### 1. Follow AAA Pattern
```python
def test_function():
    # Arrange - Setup
    input_data = create_test_data()

    # Act - Execute
    result = function_under_test(input_data)

    # Assert - Verify
    assert result == expected_value
```

#### 2. Test One Thing
```python
# ✅ Good - Tests one specific behavior
def test_scrape_url_returns_dataframe():
    result = scrape_url("https://example.com")
    assert isinstance(result, pd.DataFrame)

def test_scrape_url_has_correct_columns():
    result = scrape_url("https://example.com")
    assert result.columns.tolist() == ["col1", "col2", "col3"]

# ❌ Bad - Tests multiple things
def test_scrape_url():
    result = scrape_url("https://example.com")
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == ["col1", "col2", "col3"]
    assert len(result) > 0
    assert result["col1"].dtype == int
```

#### 3. Descriptive Test Names
```python
# ✅ Good - Clear what is being tested
def test_get_players_returns_empty_list_when_team_has_no_players():
    pass

def test_scrape_url_raises_http_error_on_403_response():
    pass

# ❌ Bad - Vague names
def test_get_players():
    pass

def test_scrape():
    pass
```

#### 4. Use Fixtures
```python
# conftest.py
import pytest
from src.core.database import SessionLocal
from src.entities.base import Base

@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_player():
    """Provide a sample player for tests."""
    return Player(
        id=1,
        name="Patrick Mahomes",
        team_id=1,
        position="QB"
    )

# Use in tests
def test_save_player(db_session, sample_player):
    """Test saving a player to database."""
    repo = PlayerRepository(db_session)
    saved = repo.save(sample_player)
    assert saved.id is not None
```

---

## Integration Testing

### Purpose
Test interaction between components (service + repository + database)

### Example: Database Integration Test

```python
# tests/test_integration.py
import pytest
from src.services.excel_scraper_service import scrape_from_excel
from src.core.database import SessionLocal
from src.repositories.scraped_data_repo import ScrapedDataRepository

@pytest.mark.asyncio
async def test_scrape_excel_integration():
    """
    Integration test for Excel scraping workflow.

    Tests:
    - Reading Excel file
    - Scraping URLs
    - Storing in database
    - Metadata tracking
    """
    # Arrange
    excel_path = "tests/fixtures/test_urls.xlsx"
    db = SessionLocal()

    # Act
    result = await scrape_from_excel(excel_path)

    # Assert
    assert result['urls_processed'] == 3
    assert result['urls_success'] >= 1
    assert result['tables_extracted'] >= 1

    # Verify data in database
    repo = ScrapedDataRepository(db)
    metadata = repo.find_all()
    assert len(metadata) > 0

    # Cleanup
    db.close()

@pytest.mark.asyncio
async def test_scrape_and_retrieve_team_offense():
    """
    Integration test for scraping and retrieving team offense data.
    """
    # Arrange
    year = 2024

    # Act - Scrape data
    scrape_result = await team_offense_service.scrape_and_store_team_offense(year)

    # Assert - Verify scraping worked
    assert scrape_result['teams_scraped'] == 32

    # Act - Retrieve data
    db = SessionLocal()
    repo = TeamOffenseRepository(db)
    teams = repo.find_by_season(year)

    # Assert - Verify data stored correctly
    assert len(teams) == 32
    assert all(t.season == year for t in teams)

    # Cleanup
    db.close()
```

---

## End-to-End Testing

### Purpose
Test complete user workflows from API to database

### Example: E2E API Test

```python
# tests/test_e2e.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_complete_scraping_workflow():
    """
    E2E test for complete scraping workflow.

    Workflow:
    1. Health check
    2. Scrape team data
    3. Verify data via API
    """
    # Step 1: Health check
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

    # Step 2: Scrape team data
    response = client.get("/scrape/chiefs/2024")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert data['tables_scraped'] > 0

    # Step 3: Verify data stored (via future endpoint)
    # response = client.get("/teams/chiefs/stats?season=2024")
    # assert response.status_code == 200
    # assert response.json()['season'] == 2024

def test_excel_scraping_e2e():
    """E2E test for Excel scraping via API."""
    # Prepare test Excel file
    excel_path = "/tmp/test_urls.xlsx"
    # ... create test Excel file ...

    # Scrape via API
    response = client.post(
        "/scrape/excel",
        params={"excel_path": excel_path}
    )

    assert response.status_code == 200
    result = response.json()
    assert result['urls_processed'] > 0
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_unit/              # Unit tests
│   ├── test_services/
│   │   ├── test_player_service.py
│   │   ├── test_scrape_service.py
│   │   └── test_excel_scraper_service.py
│   ├── test_repositories/
│   │   ├── test_player_repo.py
│   │   └── test_scraped_data_repo.py
│   └── test_utils/
│       └── test_validators.py
├── test_integration/       # Integration tests
│   ├── test_scraping_workflow.py
│   └── test_database_operations.py
├── test_e2e/              # End-to-end tests
│   └── test_api_workflows.py
└── fixtures/              # Test data
    ├── test_urls.xlsx
    └── sample_data.json
```

---

## Testing Patterns

### Pattern 1: Mock External Dependencies

```python
import pytest
from unittest.mock import patch, Mock

def test_scrape_url_success():
    """Test scraping with mocked HTTP request."""
    # Mock requests.get
    with patch('requests.get') as mock_get:
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><table>...</table></html>"
        mock_get.return_value = mock_response

        # Test function
        result = scrape_url("https://example.com")

        # Verify
        assert result is not None
        mock_get.assert_called_once_with("https://example.com", timeout=30)
```

### Pattern 2: Database Rollback

```python
@pytest.fixture
def db_session():
    """Provide transactional database session."""
    session = SessionLocal()

    # Start transaction
    session.begin()

    yield session

    # Rollback after test (don't persist test data)
    session.rollback()
    session.close()
```

### Pattern 3: Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("season,expected_valid", [
    (2024, True),
    (1920, True),
    (2100, True),
    (1919, False),  # Too old
    (2101, False),  # Too new
    (-1, False),    # Negative
])
def test_validate_season(season, expected_valid):
    """Test season validation with multiple inputs."""
    if expected_valid:
        validate_season(season)  # Should not raise
    else:
        with pytest.raises(ValueError):
            validate_season(season)
```

### Pattern 4: Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_scrape():
    """Test async scraping function."""
    result = await scrape_from_excel("test.xlsx")
    assert result['urls_processed'] > 0
```

---

## Test Coverage

### Measuring Coverage

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals

- **Overall:** 80%+ coverage
- **Critical paths:** 95%+ coverage
- **Service layer:** 90%+ coverage
- **Repository layer:** 85%+ coverage
- **Entities/DTOs:** 70%+ coverage (less logic)

### What to Focus On

```python
# High priority - Test thoroughly
- Business logic in services
- Data validation
- Error handling
- Edge cases
- Integration points

# Lower priority - Less coverage OK
- Simple getters/setters
- Configuration code
- DTOs with just fields
```

---

## Testing Checklist

### Before Committing

- [ ] All tests pass locally
- [ ] New code has tests
- [ ] Coverage maintained or improved
- [ ] No skipped/disabled tests without reason
- [ ] Test names are descriptive
- [ ] Tests are isolated (no interdependencies)

### Test Quality

- [ ] Tests are readable
- [ ] Tests test behavior, not implementation
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Mocks used appropriately
- [ ] No hardcoded values (use constants)

---

## Common Testing Mistakes

### ❌ Mistake 1: Testing Implementation Details

```python
# Bad - Tests internal implementation
def test_get_players_calls_query():
    service = PlayerService(repo)
    service.get_players(1)
    # Testing that it calls specific internal method
    assert service._internal_method_called

# Good - Tests behavior/outcome
def test_get_players_returns_correct_data():
    service = PlayerService(repo)
    players = service.get_players(1)
    assert len(players) == 3
    assert players[0].name == "Patrick Mahomes"
```

### ❌ Mistake 2: Dependent Tests

```python
# Bad - Tests depend on order
def test_create_player():
    player = create_player("Test Player")
    assert player.id == 1

def test_get_player():
    # Assumes previous test ran and created player with id=1
    player = get_player(1)
    assert player.name == "Test Player"

# Good - Independent tests
def test_create_player():
    player = create_player("Test Player")
    assert player.id is not None

def test_get_player():
    # Setup own test data
    player = create_player("Test Player")
    retrieved = get_player(player.id)
    assert retrieved.name == "Test Player"
```

### ❌ Mistake 3: Vague Assertions

```python
# Bad - Vague assertions
def test_scrape_url():
    result = scrape_url("https://example.com")
    assert result  # What does this test?

# Good - Specific assertions
def test_scrape_url_returns_non_empty_dataframe():
    result = scrape_url("https://example.com")
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert "player_name" in result.columns
```

### ❌ Mistake 4: Testing Multiple Things

```python
# Bad - One test does too much
def test_player_workflow():
    # Create
    player = create_player("Test")
    assert player.id is not None

    # Update
    player.name = "Updated"
    updated = update_player(player)
    assert updated.name == "Updated"

    # Delete
    delete_player(player.id)
    assert get_player(player.id) is None

# Good - Separate tests
def test_create_player():
    player = create_player("Test")
    assert player.id is not None

def test_update_player():
    player = create_player("Test")
    player.name = "Updated"
    updated = update_player(player)
    assert updated.name == "Updated"

def test_delete_player():
    player = create_player("Test")
    delete_player(player.id)
    assert get_player(player.id) is None
```

---

## Debugging Failing Tests

### Step 1: Reproduce Locally

```bash
# Run specific failing test
pytest tests/test_player_service.py::test_get_players -v

# Run with print output
pytest tests/test_player_service.py::test_get_players -v -s

# Run with debugger
pytest tests/test_player_service.py::test_get_players --pdb
```

### Step 2: Check Error Message

```python
# Good error message
def test_get_players():
    players = service.get_players(1)
    assert len(players) == 3, f"Expected 3 players, got {len(players)}"

# Output: AssertionError: Expected 3 players, got 2
```

### Step 3: Add Debug Logging

```python
import logging
logger = logging.getLogger(__name__)

def test_get_players():
    logger.info("Starting test_get_players")
    players = service.get_players(1)
    logger.info(f"Retrieved {len(players)} players")
    assert len(players) == 3
```

### Step 4: Check Test Isolation

```python
# Ensure tests don't affect each other
def setup_method(self):
    """Reset state before each test."""
    self.db.rollback()
    self.clear_cache()
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## Tools & Commands

### Running Tests

```bash
# All tests
pytest tests/

# Verbose output
pytest tests/ -v

# Specific test file
pytest tests/test_player_service.py

# Specific test function
pytest tests/test_player_service.py::test_get_players

# With coverage
pytest tests/ --cov=src

# HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Stop on first failure
pytest tests/ -x

# Show print output
pytest tests/ -s

# Parallel execution
pytest tests/ -n auto
```

### Test Discovery

```bash
# List all tests
pytest tests/ --collect-only

# List tests matching pattern
pytest tests/ -k "player" --collect-only
```

---

## Related Documentation

- [Development Agent Role](development-agent.md)
- [Code Review Agent Role](code-review-agent.md)
- [CI/CD Pipeline](../sdlc/ci-cd.md)
- [Architecture Overview](../architecture/overview.md)

---

**Remember**: Good tests are the foundation of reliable software! 🧪

**Last Updated**: February 2026
