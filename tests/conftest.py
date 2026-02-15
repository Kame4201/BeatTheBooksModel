"""
Pytest configuration and fixtures.
"""
import pytest
import sys
from pathlib import Path

# Add src to path so tests can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_excel_data():
    """Sample Excel data for testing."""
    import pandas as pd
    return pd.DataFrame({
        'url': [
            'https://www.pro-football-reference.com/teams/buf/2024.htm',
            'https://www.pro-football-reference.com/years/2024/'
        ],
        'season': [2024, 2024],
        'entity_type': ['team', 'league'],
        'table_type': ['schedule', 'team_stats']
    })


@pytest.fixture
def sample_scraped_table():
    """Sample scraped table data for testing."""
    import pandas as pd
    return pd.DataFrame({
        'Team': ['BUF', 'KC', 'SF'],
        'Wins': [11, 14, 12],
        'Losses': [6, 3, 5]
    })
