# API Endpoints

## Overview

BeatTheBooksModel exposes a RESTful API built with **FastAPI** for scraping and retrieving NFL statistics.

**Base URL:** `http://localhost:8000` (development)

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Endpoints

### 1. Health Check

```http
GET /
```

**Description:** Basic health check endpoint

**Response:**
```json
{
  "Hello": "World"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### 2. Scrape Team Data

```http
GET /scrape/{team}/{year}
```

**Description:** Scrape NFL data for a specific team and year from Pro-Football-Reference

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `team` | string | Team name or abbreviation | `chiefs`, `eagles` |
| `year` | integer | Season year | `2024` |

**Response:**
```json
{
  "status": "success",
  "team": "chiefs",
  "year": 2024,
  "tables_scraped": 5,
  "rows_inserted": 247
}
```

**Example:**
```bash
# Scrape Kansas City Chiefs 2024 season
curl http://localhost:8000/scrape/chiefs/2024

# Scrape Philadelphia Eagles 2023 season
curl http://localhost:8000/scrape/eagles/2023
```

**Service:** `src/services/scrape_service.py`

**Notes:**
- Uses Selenium for JavaScript-heavy pages
- Handles rate limiting automatically
- Stores data in multiple tables based on content

---

### 3. Scrape Team Offense Stats

```http
GET /scrape/{year}
```

**Description:** Scrape team-level offensive statistics for all teams for a given season

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `year` | integer | Season year | `2024` |

**Response:**
```json
{
  "status": "success",
  "year": 2024,
  "teams_scraped": 32,
  "rows_inserted": 32
}
```

**Example:**
```bash
# Scrape 2024 team offense stats for all teams
curl http://localhost:8000/scrape/2024
```

**Service:** `src/services/team_offense_service.py`

**Database Table:** `team_offense`

**Notes:**
- Scrapes aggregate team stats (not individual players)
- Stores in `team_offense` table
- Includes passing, rushing, and total offense stats

---

### 4. Scrape from Excel File

```http
POST /scrape/excel
```

**Description:** Scrape multiple Pro-Football-Reference URLs from an Excel file and store results in database

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `excel_path` | string | Yes | Path to Excel file | `/path/to/urls.xlsx` |

**Excel File Format:**

The Excel file should contain these columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `url` | ✅ Yes | Pro-Football-Reference URL | `https://www.pro-football-reference.com/years/2024/` |
| `season` | ❌ Optional | Season year | `2024` |
| `entity_type` | ❌ Optional | Type of entity | `team`, `player` |
| `table_type` | ❌ Optional | Type of table | `passing`, `rushing` |

**Example Excel:**
```
url                                                 | season | entity_type | table_type
https://www.pro-football-reference.com/years/2024/ | 2024   | team        | offense
https://www.pro-football-reference.com/years/2024/ | 2024   | player      | passing
```

**Request:**
```bash
curl -X POST "http://localhost:8000/scrape/excel?excel_path=/path/to/urls.xlsx"
```

**Response:**
```json
{
  "urls_processed": 15,
  "urls_success": 12,
  "urls_failed": 3,
  "tables_extracted": 24,
  "rows_inserted": 1847,
  "errors": [
    "URL 3: 403 Forbidden - https://...",
    "URL 7: 403 Forbidden - https://...",
    "URL 11: Timeout after 30 seconds"
  ]
}
```

**Service:** `src/services/excel_scraper_service.py`

**Features:**
- Bulk URL scraping
- 60-second delay between requests (rate limiting)
- Automatic table detection
- Dynamic table creation based on data structure
- Idempotent upserts (safe to re-run)
- Comprehensive error tracking

**Notes:**
- Each URL is scraped sequentially with 60-second delays
- Handles 403 errors gracefully
- Creates database tables dynamically based on scraped data
- Tracks metadata in `scraped_data_metadata` table

---

## Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 403 | Forbidden | Website blocking (Pro-Football-Reference) |
| 404 | Not Found | Endpoint or resource not found |
| 500 | Internal Server Error | Server error (database, scraping, etc.) |
| 503 | Service Unavailable | Database unavailable |

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 500
}
```

### Common Errors

**403 Forbidden (Pro-Football-Reference)**
```json
{
  "error": "Failed to scrape URL",
  "detail": "403 Forbidden - Website blocking automated requests",
  "url": "https://www.pro-football-reference.com/years/2025/#all_team_stats"
}
```

**Possible causes:**
- URL contains hashtags (`#all_team_stats`)
- Requesting too-recent data (2025 season)
- Rate limiting not sufficient
- Need to use Selenium instead of requests

**Database Connection Error**
```json
{
  "error": "Database connection failed",
  "detail": "Connection refused at postgresql://...",
  "status_code": 503
}
```

**Invalid Excel Path**
```json
{
  "error": "File not found",
  "detail": "Excel file not found at /path/to/file.xlsx",
  "status_code": 400
}
```

---

## Rate Limiting

### Current Implementation
- **60-second delay** between scraping requests
- Prevents Pro-Football-Reference from blocking IP
- Configurable in service layer

### Future Improvements
- Per-endpoint rate limits
- User-based rate limiting
- API key authentication with tier-based limits

---

## Authentication

### Current Status
- **No authentication** (development)

### Planned
- API key authentication
- JWT token-based auth
- Role-based access control (RBAC)

**Future endpoint:**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Request Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/

# Scrape team data
curl http://localhost:8000/scrape/chiefs/2024

# Scrape team offense stats
curl http://localhost:8000/scrape/2024

# Scrape from Excel
curl -X POST "http://localhost:8000/scrape/excel?excel_path=/path/to/urls.xlsx"
```

### Using Python Requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/")
print(response.json())

# Scrape team data
response = requests.get("http://localhost:8000/scrape/chiefs/2024")
print(response.json())

# Scrape from Excel
response = requests.post(
    "http://localhost:8000/scrape/excel",
    params={"excel_path": "/path/to/urls.xlsx"}
)
print(response.json())
```

### Using JavaScript Fetch

```javascript
// Health check
fetch('http://localhost:8000/')
  .then(res => res.json())
  .then(data => console.log(data));

// Scrape team data
fetch('http://localhost:8000/scrape/chiefs/2024')
  .then(res => res.json())
  .then(data => console.log(data));

// Scrape from Excel
fetch('http://localhost:8000/scrape/excel?excel_path=/path/to/urls.xlsx', {
  method: 'POST'
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI (Recommended)
**URL:** `http://localhost:8000/docs`

**Features:**
- Try out endpoints directly in browser
- See request/response schemas
- View parameter descriptions
- Test authentication

### ReDoc
**URL:** `http://localhost:8000/redoc`

**Features:**
- Alternative documentation UI
- Clean, readable format
- Better for reading documentation

---

## Running the API Server

### Development

```bash
# Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# http://localhost:8000
# http://127.0.0.1:8000
```

### Production

```bash
# Start with multiple workers
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use Gunicorn with Uvicorn workers
gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Future Endpoints (Planned)

### Retrieve Data Endpoints

```http
GET /teams/{team}/stats?season=2024
GET /players/{player_id}/stats?season=2024
GET /standings?season=2024
GET /games?season=2024&week=1
```

### Analytics Endpoints

```http
GET /analytics/team/{team}/trends?seasons=2020,2021,2022,2023,2024
GET /analytics/player/{player_id}/projections?season=2025
GET /analytics/matchup/{team1}/{team2}?season=2024
```

### Admin Endpoints

```http
POST /admin/scrape/schedule     # Schedule automatic scraping
GET /admin/scrape/status        # Check scraping job status
DELETE /admin/data/{table}      # Clear data from table
POST /admin/backup              # Trigger database backup
```

---

## API Design Principles

### RESTful
- Use HTTP verbs correctly (GET, POST, PUT, DELETE)
- Resource-based URLs (`/teams`, `/players`)
- Consistent naming conventions

### Versioning
- Future: `/v1/scrape/...`, `/v2/scrape/...`
- Maintain backward compatibility

### Pagination
- Future: `?page=1&limit=50`
- For large result sets

### Filtering
- Future: `?season=2024&team=chiefs&position=QB`
- For flexible queries

### Documentation
- OpenAPI/Swagger spec
- Interactive docs at `/docs`
- Clear error messages

---

## Performance Considerations

### Caching
- Cache frequently accessed data
- Use Redis for distributed caching
- Cache invalidation on updates

### Async Operations
- All endpoints use `async/await`
- Non-blocking I/O
- Better concurrency

### Database Connection Pooling
- Reuse database connections
- Configure pool size appropriately
- Monitor connection usage

---

## Security Considerations

### Input Validation
- Pydantic models validate inputs
- SQL injection prevention (parameterized queries)
- Path traversal prevention

### Rate Limiting
- Prevent abuse
- Per-IP or per-user limits
- Configurable thresholds

### CORS
- Configure allowed origins
- Restrict in production
- Enable for development

**Example:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Monitoring & Logging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

@app.get("/scrape/{team}/{year}")
async def scrape_data(team: str, year: int):
    logger.info(f"Scraping {team} for {year}")
    # ... endpoint logic
```

### Metrics
- Request count
- Response times
- Error rates
- Database query times

**Tools:**
- Prometheus
- Grafana
- Datadog
- New Relic

---

## Related Documentation

- [Architecture Overview](overview.md)
- [Database Schema](database-schema.md)
- [Data Flow](data-flow.md)

---

**Last Updated**: February 2026
