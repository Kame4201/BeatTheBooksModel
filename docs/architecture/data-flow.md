# Data Flow

## Overview

This document describes how data flows through the BeatTheBooksModel system from external sources to the database.

---

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                    │
│              (Pro-Football-Reference.com)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scraping Layer                           │
│         (Selenium, BeautifulSoup, Requests)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│        (Business Logic, Data Transformation)                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Repository Layer                          │
│            (Data Access, SQL Operations)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database                               │
│              (PostgreSQL via Neon.tech)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Data Flows

### Flow 1: Single Team Scraping

**Endpoint:** `GET /scrape/{team}/{year}`

```
1. API Request
   │
   ├─> User/Client sends: GET /scrape/chiefs/2024
   │
   ▼
2. Presentation Layer (main.py)
   │
   ├─> FastAPI endpoint receives request
   ├─> Validates parameters (team, year)
   ├─> Calls: scrape_service.scrape_and_store(team, year)
   │
   ▼
3. Service Layer (scrape_service.py)
   │
   ├─> Construct Pro-Football-Reference URL
   │   Example: "https://www.pro-football-reference.com/teams/kan/2024.htm"
   │
   ├─> Initialize Selenium WebDriver
   │
   ├─> Navigate to URL and wait for page load
   │
   ├─> Extract HTML content
   │
   ├─> Parse HTML with BeautifulSoup
   │
   ├─> Identify tables on page (by ID or class)
   │
   ├─> For each table:
   │   ├─> Extract table data into pandas DataFrame
   │   ├─> Clean and transform data
   │   ├─> Determine target database table name
   │   └─> Call repository to store data
   │
   ▼
4. Repository Layer (team_game_repo.py, etc.)
   │
   ├─> Validate data with Pydantic DTOs
   │
   ├─> Convert DTO to SQLAlchemy entity
   │
   ├─> Execute database operations:
   │   ├─> Check for existing records (by unique key)
   │   ├─> Insert new records OR
   │   └─> Update existing records (upsert)
   │
   ▼
5. Database (PostgreSQL)
   │
   ├─> Store data in appropriate tables:
   │   ├─> team_offense
   │   ├─> passing_stats
   │   ├─> rushing_stats
   │   └─> etc.
   │
   ▼
6. Response
   │
   └─> Return summary to client:
       {
         "status": "success",
         "team": "chiefs",
         "year": 2024,
         "tables_scraped": 5,
         "rows_inserted": 247
       }
```

---

### Flow 2: Team Offense Scraping

**Endpoint:** `GET /scrape/{year}`

```
1. API Request
   │
   ├─> User/Client sends: GET /scrape/2024
   │
   ▼
2. Presentation Layer (main.py)
   │
   ├─> Endpoint: scrape_team_offense(year)
   ├─> Calls: team_offense_service.scrape_and_store_team_offense(year)
   │
   ▼
3. Service Layer (team_offense_service.py)
   │
   ├─> Construct URL for team stats page
   │   Example: "https://www.pro-football-reference.com/years/2024/"
   │
   ├─> Scrape page using Selenium/BeautifulSoup
   │
   ├─> Extract team offense table
   │
   ├─> Parse into pandas DataFrame with columns:
   │   ├─> season, rk, tm, g, pf, yds, ply, ...
   │   ├─> cmp, att_pass, yds_pass, td_pass, ...
   │   └─> att_rush, yds_rush, td_rush, ...
   │
   ├─> For each row (32 teams):
   │   ├─> Create TeamOffenseDTO
   │   └─> Call repository.create_or_update(dto)
   │
   ▼
4. Repository Layer (team_offense_repo.py)
   │
   ├─> For each team:
   │   ├─> Check if record exists (UNIQUE: tm, season)
   │   ├─> If exists: UPDATE
   │   └─> If not: INSERT
   │
   ├─> Commit transaction
   │
   ▼
5. Database (team_offense table)
   │
   ├─> Store 32 rows (one per team)
   │
   ▼
6. Response
   │
   └─> {
         "status": "success",
         "year": 2024,
         "teams_scraped": 32,
         "rows_inserted": 32
       }
```

---

### Flow 3: Excel Bulk Scraping

**Endpoint:** `POST /scrape/excel?excel_path=/path/to/file.xlsx`

```
1. API Request
   │
   ├─> User sends: POST /scrape/excel?excel_path=...
   │
   ▼
2. Presentation Layer (main.py)
   │
   ├─> Endpoint: scrape_from_excel_file(excel_path)
   ├─> Calls: excel_scraper_service.scrape_from_excel(excel_path)
   │
   ▼
3. Service Layer (excel_scraper_service.py)
   │
   ├─> Step 1: Read Excel File
   │   ├─> Use openpyxl/pandas to read .xlsx
   │   ├─> Extract columns: url, season, entity_type, table_type
   │   └─> Validate required columns present
   │
   ├─> Step 2: Initialize Tracking
   │   ├─> Create ScrapedDataRepository
   │   ├─> Ensure metadata table exists
   │   └─> Initialize counters (urls_processed, urls_success, etc.)
   │
   ├─> Step 3: Process Each URL
   │   │
   │   └─> For each row in Excel:
   │       │
   │       ├─> A. Extract URL and metadata
   │       │
   │       ├─> B. Rate Limiting
   │       │   └─> Sleep 60 seconds (except first URL)
   │       │
   │       ├─> C. Scrape URL
   │       │   ├─> Send HTTP request (with retry logic)
   │       │   ├─> Handle 403 errors gracefully
   │       │   └─> Parse HTML with BeautifulSoup
   │       │
   │       ├─> D. Extract Tables
   │       │   ├─> Find all <table> elements
   │       │   ├─> For each table:
   │       │   │   ├─> Extract table ID
   │       │   │   ├─> Parse into pandas DataFrame
   │       │   │   └─> Store in list
   │       │   │
   │       │   ▼
   │       ├─> E. Store in Database
   │       │   │
   │       │   └─> For each table/DataFrame:
   │       │       │
   │       │       ├─> Generate table name
   │       │       │   Example: "team_offense_2024"
   │       │       │
   │       │       ├─> Call: repo.create_dynamic_table()
   │       │       │   ├─> Inspect DataFrame columns and types
   │       │       │   ├─> Generate CREATE TABLE IF NOT EXISTS
   │       │       │   └─> Execute SQL
   │       │       │
   │       │       ├─> Call: repo.upsert_dataframe()
   │       │       │   ├─> Generate INSERT ... ON CONFLICT UPDATE
   │       │       │   ├─> Batch insert rows
   │       │       │   └─> Return rows_inserted count
   │       │       │
   │       │       └─> Call: repo.track_scraped_data()
   │       │           ├─> Create ScrapedDataMetadataCreate DTO
   │       │           └─> Insert into scraped_data_metadata
   │       │
   │       ├─> F. Update Counters
   │       │   ├─> urls_processed += 1
   │       │   ├─> urls_success += 1 (if success)
   │       │   ├─> urls_failed += 1 (if error)
   │       │   ├─> tables_extracted += len(tables)
   │       │   └─> rows_inserted += total_rows
   │       │
   │       └─> G. Error Handling
   │           ├─> Catch exceptions
   │           ├─> Log error
   │           ├─> Append to errors list
   │           └─> Continue to next URL (don't fail entire job)
   │
   ▼
4. Repository Layer (scraped_data_repo.py)
   │
   ├─> create_dynamic_table(table_name, df)
   │   ├─> Map pandas dtypes to SQL types
   │   │   int64 → INTEGER
   │   │   float64 → NUMERIC(10,2)
   │   │   object → TEXT
   │   │   datetime64 → TIMESTAMP
   │   │
   │   ├─> Build CREATE TABLE statement
   │   └─> Execute (IF NOT EXISTS)
   │
   ├─> upsert_dataframe(table_name, df)
   │   ├─> Identify unique key columns
   │   ├─> Generate ON CONFLICT clause
   │   ├─> Batch insert with upsert logic
   │   └─> Return row count
   │
   └─> track_scraped_data(metadata)
       ├─> Insert into scraped_data_metadata
       └─> Track: source_url, table_id, scraped_at, rows_scraped
   │
   ▼
5. Database (PostgreSQL)
   │
   ├─> Create tables dynamically (if needed)
   │
   ├─> Insert/Update data in dynamic tables
   │
   └─> Track metadata in scraped_data_metadata
   │
   ▼
6. Response
   │
   └─> {
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

---

## Data Transformation Steps

### Step 1: HTML → DataFrame

```python
# Input: Raw HTML
<table id="passing_stats">
  <thead>
    <tr><th>Player</th><th>Yds</th><th>TD</th></tr>
  </thead>
  <tbody>
    <tr><td>Patrick Mahomes</td><td>4839</td><td>36</td></tr>
  </tbody>
</table>

# Output: pandas DataFrame
   Player           Yds   TD
0  Patrick Mahomes  4839  36
```

**Tools:** BeautifulSoup, pandas `read_html()`

---

### Step 2: DataFrame → DTO

```python
# Input: DataFrame row
row = {
    "player_name": "Patrick Mahomes",
    "yds": 4839,
    "td": 36,
    "season": 2024,
    "tm": "Chiefs"
}

# Output: Pydantic DTO
dto = PassingStatsCreate(
    player_name="Patrick Mahomes",
    yds=4839,
    td=36,
    season=2024,
    tm="Chiefs"
)
# Validated with type checking and constraints
```

**Tools:** Pydantic models

---

### Step 3: DTO → Entity

```python
# Input: DTO
dto = PassingStatsCreate(player_name="Patrick Mahomes", ...)

# Output: SQLAlchemy Entity
entity = PassingStats(
    player_name="Patrick Mahomes",
    yds=4839,
    td=36,
    season=2024,
    tm="Chiefs"
)
```

**Tools:** SQLAlchemy ORM

---

### Step 4: Entity → Database

```python
# Input: Entity
entity = PassingStats(...)

# Output: SQL INSERT/UPDATE
db.add(entity)
db.commit()

# SQL executed:
# INSERT INTO passing_stats (player_name, yds, td, season, tm)
# VALUES ('Patrick Mahomes', 4839, 36, 2024, 'Chiefs')
# ON CONFLICT (player_name, season, tm)
# DO UPDATE SET yds = EXCLUDED.yds, td = EXCLUDED.td
```

**Tools:** SQLAlchemy, PostgreSQL

---

## Error Handling Flow

### Scenario: 403 Forbidden Error

```
1. Request to Pro-Football-Reference
   │
   ├─> HTTP GET https://www.pro-football-reference.com/years/2025/
   │
   ▼
2. Server Response: 403 Forbidden
   │
   ├─> Status code: 403
   ├─> Reason: Bot detection, rate limiting, or URL issue
   │
   ▼
3. Service Layer
   │
   ├─> Catch HTTPError exception
   ├─> Log error with details:
   │   ├─> URL attempted
   │   ├─> Status code
   │   └─> Timestamp
   │
   ├─> Append to errors list
   │
   ├─> Increment urls_failed counter
   │
   └─> Continue to next URL (don't fail entire batch)
   │
   ▼
4. Response
   │
   └─> Include error in response.errors array
       "errors": [
         "URL 3: 403 Forbidden - https://www.pro-football-reference.com/years/2025/"
       ]
```

### Scenario: Database Connection Error

```
1. Attempt Database Operation
   │
   ├─> db.execute("INSERT INTO ...")
   │
   ▼
2. Database Error
   │
   ├─> Connection refused / Database unavailable
   │
   ▼
3. Repository Layer
   │
   ├─> Catch SQLAlchemyError
   ├─> Log error
   ├─> Rollback transaction
   │
   ▼
4. Service Layer
   │
   ├─> Re-raise exception to API layer
   │
   ▼
5. API Layer
   │
   ├─> Catch exception
   ├─> Return HTTP 503 Service Unavailable
   └─> Response:
       {
         "error": "Database connection failed",
         "detail": "Connection refused",
         "status_code": 503
       }
```

---

## Data Validation Flow

```
1. Raw Data (from website)
   │
   ├─> String: "4839" (yards)
   ├─> String: "Patrick Mahomes" (player)
   │
   ▼
2. DataFrame (pandas)
   │
   ├─> Type conversion:
   │   ├─> "4839" → int: 4839
   │   └─> "Patrick Mahomes" → str: "Patrick Mahomes"
   │
   ▼
3. DTO (Pydantic)
   │
   ├─> Validation:
   │   ├─> yds: int (required)
   │   ├─> player_name: str (max length 128)
   │   ├─> season: int (range 1920-2100)
   │   └─> tm: str (not empty)
   │
   ├─> If validation fails:
   │   └─> Raise ValidationError with details
   │
   ▼
4. Entity (SQLAlchemy)
   │
   ├─> Database constraints:
   │   ├─> NOT NULL checks
   │   ├─> UNIQUE constraints
   │   └─> Data type enforcement
   │
   ▼
5. Database
   │
   └─> Data stored successfully
```

---

## Concurrency & Rate Limiting

### Sequential Processing

```
URL 1 → Scrape → Store → Wait 60s →
URL 2 → Scrape → Store → Wait 60s →
URL 3 → Scrape → Store → Wait 60s →
...
```

**Why sequential?**
- Respect website rate limits
- Avoid IP banning
- Prevent 403 errors

**Future improvement:**
- Parallel scraping with IP rotation
- Multiple concurrent workers
- Distributed task queue (Celery, RabbitMQ)

---

## Database Transaction Flow

### Single Operation

```
1. Begin Transaction
   │
   ├─> db.begin()
   │
   ▼
2. Execute Operations
   │
   ├─> db.query(...)
   ├─> db.add(entity)
   ├─> db.update(...)
   │
   ▼
3. Commit or Rollback
   │
   ├─> If success: db.commit()
   └─> If error: db.rollback()
```

### Batch Operations

```
1. Begin Transaction
   │
   ▼
2. Bulk Insert (1000 rows)
   │
   ├─> db.bulk_insert_mappings(PassingStats, rows)
   │
   ▼
3. Commit
   │
   └─> db.commit()
      All 1000 rows inserted atomically
      (all succeed or all fail)
```

---

## Data Consistency

### Unique Constraints

Ensure data consistency:

```sql
-- Prevent duplicate team records
UNIQUE (tm, season)

-- Prevent duplicate player records
UNIQUE (player_name, season, tm)
```

### Upsert Logic

Handle conflicts gracefully:

```sql
INSERT INTO passing_stats (player_name, season, tm, yds, td)
VALUES ('Patrick Mahomes', 2024, 'Chiefs', 4839, 36)
ON CONFLICT (player_name, season, tm)
DO UPDATE SET
  yds = EXCLUDED.yds,
  td = EXCLUDED.td
```

**Result:**
- If record exists: UPDATE
- If record doesn't exist: INSERT
- Idempotent operation (safe to re-run)

---

## Monitoring Data Flow

### Logging Points

```
1. API Request Received
   └─> Log: timestamp, endpoint, parameters

2. Scraping Started
   └─> Log: URL, timestamp

3. Scraping Completed
   └─> Log: rows extracted, duration

4. Database Operation
   └─> Log: table, operation (insert/update), row count

5. Error Occurred
   └─> Log: error type, message, stack trace

6. API Response Sent
   └─> Log: status code, response time
```

### Metrics

- **Scraping success rate**: `urls_success / urls_processed`
- **Average scraping time**: `total_time / urls_processed`
- **Database insert rate**: `rows_inserted / time`
- **Error rate**: `urls_failed / urls_processed`

---

## Related Documentation

- [Architecture Overview](overview.md)
- [Database Schema](database-schema.md)
- [API Endpoints](api-endpoints.md)

---

**Last Updated**: February 2026
