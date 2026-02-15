# Database Schema

## Overview

BeatTheBooksModel uses **PostgreSQL** (hosted on Neon.tech) with a relational schema designed to store NFL statistics at both team and player levels.

---

## Database Connection

```python
# src/core/database.py
DATABASE_URL = os.getenv("DATABASE_URL")
# Format: postgresql://user:password@host:5432/database

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

---

## Schema Categories

### 1. Team-Level Tables
Team aggregate statistics for a given season

### 2. Player-Level Tables
Individual player statistics for a given season

### 3. Games & Standings
Game results and team standings

### 4. Metadata Tables
Tracking scraped data

---

## Team-Level Tables

### team_offense

**Purpose:** Team offensive statistics by season

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer              -- Season year (e.g., 2024)
tm              varchar(64)          -- Team name (e.g., "Kansas City Chiefs")
g               integer              -- Games played
pf              integer              -- Points for
yds             integer              -- Total yards
ply             integer              -- Total plays run
turnovers       integer              -- Total turnovers

-- Passing stats
cmp             integer              -- Completions
att_pass        integer              -- Pass attempts
yds_pass        integer              -- Passing yards
td_pass         integer              -- Passing TDs
ints            integer              -- Interceptions

-- Rushing stats
att_rush        integer              -- Rush attempts
yds_rush        integer              -- Rushing yards
td_rush         integer              -- Rushing TDs

UNIQUE (tm, season)
```

**Entity:** `src/entities/team_offense.py`

**Example:**
```
season | tm           | pf  | yds  | td_pass | td_rush
2024   | Chiefs       | 456 | 6234 | 35      | 18
2024   | Eagles       | 478 | 6890 | 38      | 22
```

---

### team_defense

**Purpose:** Team defensive statistics by season

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
tm              varchar(64)          -- Team name
pa              integer              -- Points allowed
yds             integer              -- Yards allowed
turnovers       integer              -- Takeaways
ints            integer              -- Interceptions made
sk              integer              -- Sacks

UNIQUE (tm, season)
```

**Entity:** `src/entities/defense_stats.py`

---

### returns

**Purpose:** Team return statistics (punt returns, kick returns)

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
tm              varchar(64)
ret_punt        integer              -- Punt returns
yds_punt        integer              -- Punt return yards
td_punt         integer              -- Punt return TDs
ret_kick        integer              -- Kickoff returns
yds_kick        integer              -- Kickoff return yards
td_kick         integer              -- Kickoff return TDs

UNIQUE (tm, season)
```

**Entity:** `src/entities/returns.py`

---

### kicking

**Purpose:** Team kicking statistics (field goals, extra points, kickoffs)

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
tm              varchar(64)

-- Field goals by distance
fga_0_19        integer              -- FG attempts 0-19 yards
fgm_0_19        integer              -- FG made 0-19 yards
fga_20_29       integer              -- FG attempts 20-29 yards
fgm_20_29       integer              -- FG made 20-29 yards
-- ... (30-39, 40-49, 50+)

-- Totals
fga             integer              -- Total FG attempts
fgm             integer              -- Total FG made
fg_pct          numeric(5,2)         -- FG percentage

-- Kickoffs
ko              integer              -- Kickoffs
tb              integer              -- Touchbacks
tb_pct          numeric(5,2)         -- Touchback percentage

UNIQUE (tm, season)
```

**Entity:** `src/entities/kicking.py`

---

### punting

**Purpose:** Team punting statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
tm              varchar(64)
pnt             integer              -- Number of punts
yds             integer              -- Total punt yards
ypp             numeric(5,2)         -- Yards per punt
in20            integer              -- Punts inside 20
in20_pct        numeric(5,2)         -- Percentage inside 20

UNIQUE (tm, season)
```

**Entity:** `src/entities/punting.py`

---

## Player-Level Tables

### passing_stats

**Purpose:** Individual quarterback passing statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)         -- Player name (e.g., "Patrick Mahomes")
age             integer              -- Age during season
tm              varchar(64)          -- Team
pos             varchar(16)          -- Position (QB)
g               integer              -- Games played
gs              integer              -- Games started

-- Passing stats
cmp             integer              -- Completions
att             integer              -- Attempts
cmp_pct         numeric(5,2)         -- Completion %
yds             integer              -- Passing yards
td              integer              -- Touchdowns
ints            integer              -- Interceptions
rate            numeric(6,2)         -- Passer rating
qbr             numeric(6,2)         -- QBR

-- Sacks
sk              integer              -- Sacks taken
yds_sack        integer              -- Yards lost to sacks

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/passing_stats.py`

**Example:**
```
season | player_name      | tm      | cmp | att | yds  | td | ints | rate
2024   | Patrick Mahomes  | Chiefs  | 401 | 598 | 4839 | 36 | 10   | 105.2
2024   | Jalen Hurts      | Eagles  | 280 | 460 | 3858 | 23 | 15   | 89.1
```

---

### rushing_stats

**Purpose:** Individual rushing statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
pos             varchar(16)          -- RB, QB, WR, etc.
att             integer              -- Rush attempts
yds             integer              -- Rushing yards
td              integer              -- Rushing TDs
ypa             numeric(5,2)         -- Yards per attempt
fmb             integer              -- Fumbles

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/rushing_stats.py`

---

### receiving_stats

**Purpose:** Individual receiving statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
pos             varchar(16)          -- WR, TE, RB, etc.
tgt             integer              -- Targets
rec             integer              -- Receptions
yds             integer              -- Receiving yards
td              integer              -- Receiving TDs
ypr             numeric(5,2)         -- Yards per reception
catch_pct       numeric(5,2)         -- Catch percentage

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/receiving_stats.py`

---

### defense_stats

**Purpose:** Individual defensive player statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
pos             varchar(16)          -- LB, DB, DL, etc.
ints            integer              -- Interceptions
int_td          integer              -- Interception TDs
sk              numeric(5,2)         -- Sacks
comb            integer              -- Combined tackles
solo            integer              -- Solo tackles
ff              integer              -- Forced fumbles
fr              integer              -- Fumbles recovered

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/defense_stats.py`

---

### kicking_stats

**Purpose:** Individual kicker statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
fga             integer              -- FG attempts
fgm             integer              -- FG made
fg_pct          numeric(5,2)         -- FG percentage
xpa             integer              -- XP attempts
xpm             integer              -- XP made

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/kicking_stats.py`

---

### punting_stats

**Purpose:** Individual punter statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
pnt             integer              -- Number of punts
yds             integer              -- Punt yards
ypp             numeric(5,2)         -- Yards per punt
in20_pct        numeric(5,2)         -- Inside 20 percentage

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/punting_stats.py`

---

### return_stats

**Purpose:** Individual return specialist statistics

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
pr              integer              -- Punt returns
pr_yds          integer              -- Punt return yards
pr_td           integer              -- Punt return TDs
kr              integer              -- Kick returns
kr_yds          integer              -- Kick return yards
kr_td           integer              -- Kick return TDs

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/return_stats.py`

---

### scoring_stats

**Purpose:** Individual scoring statistics (all methods)

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
player_name     varchar(128)
tm              varchar(64)
rush_td         integer              -- Rushing TDs
rec_td          integer              -- Receiving TDs
pr_td           integer              -- Punt return TDs
kr_td           integer              -- Kick return TDs
int_td          integer              -- Interception TDs
all_td          integer              -- Total TDs
pts             integer              -- Total points
pts_pg          numeric(5,2)         -- Points per game

UNIQUE (player_name, season, tm)
```

**Entity:** `src/entities/scoring_stats.py`

---

## Games & Standings

### games

**Purpose:** Individual game results

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
week            integer              -- Week number (1-18)
game_day        varchar(16)          -- Day of week (e.g., "Sunday")
game_date       date                 -- Date of game
winner          varchar(64)          -- Winning team
loser           varchar(64)          -- Losing team
pts_w           integer              -- Points by winner
pts_l           integer              -- Points by loser
yds_w           integer              -- Yards by winner
yds_l           integer              -- Yards by loser

UNIQUE (season, week, winner, loser)
```

**Example:**
```
season | week | game_date  | winner  | loser   | pts_w | pts_l
2024   | 1    | 2024-09-05 | Chiefs  | Ravens  | 27    | 20
2024   | 1    | 2024-09-08 | Eagles  | Browns  | 31    | 17
```

---

### standings

**Purpose:** Team standings by season

**Key Fields:**
```sql
id              serial PRIMARY KEY
season          integer
tm              varchar(64)          -- Team name
w               integer              -- Wins
l               integer              -- Losses
t               integer              -- Ties
win_pct         numeric(6,3)         -- Win percentage
pf              integer              -- Points for
pa              integer              -- Points against
pd              integer              -- Point differential

UNIQUE (tm, season)
```

**Example:**
```
season | tm      | w  | l  | win_pct | pf  | pa
2024   | Chiefs  | 14 | 3  | 0.824   | 456 | 329
2024   | Eagles  | 13 | 4  | 0.765   | 478 | 341
```

---

## Metadata Tables

### scraped_data_metadata

**Purpose:** Track scraped data for auditing and debugging

**Key Fields:**
```sql
id              serial PRIMARY KEY
source_url      text                 -- URL scraped from
table_id        varchar(255)         -- HTML table ID
table_name      varchar(255)         -- Database table name
scraped_at      timestamp            -- When scraped
season          integer              -- Season year
rows_scraped    integer              -- Number of rows scraped
```

**Entity:** `src/entities/scraped_data.py`

**Example:**
```
id | source_url                               | table_id      | scraped_at          | rows_scraped
1  | https://www.pro-football-reference.com/  | passing_stats | 2024-02-15 10:30:00 | 128
2  | https://www.pro-football-reference.com/  | rushing_stats | 2024-02-15 10:32:00 | 95
```

---

## Unique Constraints

### Team Tables
- `UNIQUE (tm, season)` - One row per team per season

### Player Tables
- `UNIQUE (player_name, season, tm)` - One row per player per season per team
- Handles mid-season trades (different rows for each team)

### Games
- `UNIQUE (season, week, winner, loser)` - One row per matchup

---

## Data Types

### Numeric Types
- `integer` - Whole numbers (counts, attempts, yards)
- `numeric(5,2)` - Decimals with 2 decimal places (percentages, averages)
- `numeric(6,2)` - Decimals for larger values (passer rating, points per game)

### String Types
- `varchar(64)` - Team names (max 64 chars)
- `varchar(128)` - Player names (max 128 chars)
- `text` - Unlimited length (URLs, long strings)

### Date/Time Types
- `date` - Calendar date (game_date)
- `timestamp` / `datetime` - Date and time (scraped_at)

---

## Indexes

### Primary Keys
- All tables have `serial PRIMARY KEY` (auto-incrementing)

### Unique Indexes
- Automatically created on `UNIQUE` constraints
- Enable fast lookups by team/player/season

### Recommended Additional Indexes
```sql
-- Fast lookups by season
CREATE INDEX idx_passing_stats_season ON passing_stats(season);
CREATE INDEX idx_team_offense_season ON team_offense(season);

-- Fast lookups by player
CREATE INDEX idx_passing_stats_player ON passing_stats(player_name);

-- Fast lookups by team
CREATE INDEX idx_passing_stats_team ON passing_stats(tm);
```

---

## Common Queries

### Get Team Offense for a Season
```sql
SELECT * FROM team_offense
WHERE season = 2024
ORDER BY pf DESC;  -- Order by points scored
```

### Get Top Passers for a Season
```sql
SELECT player_name, tm, yds, td, rate
FROM passing_stats
WHERE season = 2024 AND att >= 200
ORDER BY rate DESC
LIMIT 10;
```

### Get Player Stats Across Multiple Seasons
```sql
SELECT season, SUM(yds) as total_yards, SUM(td) as total_tds
FROM passing_stats
WHERE player_name = 'Patrick Mahomes'
GROUP BY season
ORDER BY season;
```

### Get Team Record with Stats
```sql
SELECT s.tm, s.w, s.l, s.win_pct, t.pf, t.pa
FROM standings s
JOIN team_offense t ON s.tm = t.tm AND s.season = t.season
WHERE s.season = 2024
ORDER BY s.win_pct DESC;
```

---

## Database Migrations

### Creating Tables
```bash
# Using Alembic (recommended)
alembic revision --autogenerate -m "Add new table"
alembic upgrade head

# Or direct SQL
psql $DATABASE_URL -f Tables.sql
```

### Modifying Schema
```bash
# Create migration
alembic revision -m "Add column to team_offense"

# Edit migration file
# migrations/versions/xxx.py
def upgrade():
    op.add_column('team_offense', sa.Column('new_field', sa.Integer))

# Apply migration
alembic upgrade head
```

---

## Data Validation Rules

### Season
- Must be 4-digit year (e.g., 2024)
- Typically 1920-present

### Team Names
- Consistent naming (e.g., "Kansas City Chiefs", not "KC" or "Chiefs")
- Handle relocations/renames appropriately

### Player Names
- Full name (e.g., "Patrick Mahomes", not "P. Mahomes")
- Handle suffixes (Jr., II, III) consistently

### Statistics
- Non-negative values (can't have negative yards, TDs, etc.)
- Percentages: 0-100 or 0.0-1.0 (be consistent)

---

## Dynamic Tables

The scraper creates dynamic tables based on scraped data structure:

```python
# src/repositories/scraped_data_repo.py
def create_dynamic_table(self, table_name: str, df: pd.DataFrame):
    """Create table based on DataFrame columns."""
    # Infer schema from DataFrame
    # Generate CREATE TABLE statement
    # Execute SQL
```

**Example:**
If scraping a new stat type from Pro-Football-Reference, the system automatically creates a table with appropriate columns.

---

## Backup & Recovery

### Database Backup
```bash
# Full backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore
```bash
# From backup file
psql $DATABASE_URL < backup_20240215.sql

# From compressed backup
gunzip -c backup_20240215.sql.gz | psql $DATABASE_URL
```

---

## Schema Diagram

```
┌─────────────────┐     ┌──────────────────┐
│   team_offense  │     │  passing_stats   │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ season          │     │ season           │
│ tm (UNIQUE)     │     │ player_name      │
│ pf              │     │ tm               │
│ yds             │     │ yds              │
│ ...             │     │ td               │
└─────────────────┘     │ ... (UNIQUE)     │
                        └──────────────────┘

┌─────────────────┐     ┌──────────────────┐
│  team_defense   │     │  rushing_stats   │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ season          │     │ season           │
│ tm (UNIQUE)     │     │ player_name      │
│ pa              │     │ tm               │
│ ...             │     │ ... (UNIQUE)     │
└─────────────────┘     └──────────────────┘

         ┌──────────────────┐
         │    standings     │
         ├──────────────────┤
         │ id (PK)          │
         │ season           │
         │ tm (UNIQUE)      │
         │ w, l, t          │
         │ win_pct          │
         └──────────────────┘
```

---

## Related Documentation

- [Architecture Overview](overview.md)
- [API Endpoints](api-endpoints.md)
- [Tables.sql](/c/Users/PC/BeatTheBooksModel/Tables.sql)

---

**Last Updated**: February 2026
