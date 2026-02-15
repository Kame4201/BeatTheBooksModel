# Testing Guide

## Running Tests

### Run All Unit Tests
```bash
./venv/bin/pytest
```

### Run Specific Test File
```bash
./venv/bin/pytest tests/test_excel_scraper.py -v
```

### Run Integration Test (with real Excel file and database)
```bash
./venv/bin/pytest tests/test_integration.py -v
```

### Run Tests by Category
```bash
# Unit tests only (no database needed)
./venv/bin/pytest -m unit

# Integration tests (requires database)
./venv/bin/pytest -m integration

# Skip slow tests
./venv/bin/pytest -m "not slow"
```

### Run with Coverage
```bash
./venv/bin/pytest --cov=src --cov-report=html
```

### Run in Verbose Mode
```bash
./venv/bin/pytest -v -s
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_excel_scraper.py    # Unit tests (mocked)
└── test_integration.py      # Integration test (real scraping)
```

## What's Tested

### Unit Tests (`test_excel_scraper.py`)
- ✅ Excel file reading
- ✅ URL validation
- ✅ Metadata column addition
- ✅ Table extraction (mocked)
- ✅ Error handling
- ⚡ Fast (no database or network calls)

### Integration Tests (`test_integration.py`)
- ✅ Full scraping flow with real Excel file
- ✅ Database connection
- ✅ Real HTTP requests to Pro-Football-Reference
- ⏱️ Slow (60-second delays between URLs)

## Important Notes

### Integration Test
The integration test (`test_integration.py`) will:
1. Read your actual Excel file
2. Scrape all URLs (with 60-second delays)
3. Store data in your Neon database
4. Take several minutes to complete

**Only run this when you're ready to scrape for real!**

### Database Connection
If database is unavailable (Neon suspended), tests requiring database will fail.
Wake up your Neon database first: https://console.neon.tech

## Troubleshooting

### Tests fail with "No module named 'src'"
Make sure you're running pytest from the project root:
```bash
cd /c/Users/PC/BeatTheBooksModel
./venv/bin/pytest
```

### Excel file not found
Update the path in `tests/test_integration.py` to match your file location.

### Database connection errors
Check that your Neon database is active and accepting connections.

## Quick Commands

```bash
# Fast unit tests only
./venv/bin/pytest tests/test_excel_scraper.py

# Full integration test (slow, scrapes for real)
./venv/bin/pytest tests/test_integration.py -v -s

# Run all tests with output
./venv/bin/pytest -v -s
```
