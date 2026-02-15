"""
Create a sample Excel file for testing the Excel scraper.
"""
import pandas as pd

# Create sample data with Pro-Football-Reference URLs
data = {
    'url': [
        'https://www.pro-football-reference.com/teams/buf/2024.htm',
        'https://www.pro-football-reference.com/teams/kan/2024.htm',
        'https://www.pro-football-reference.com/years/2024/'
    ],
    'season': [2024, 2024, 2024],
    'entity_type': ['team', 'team', 'league'],
    'table_type': ['schedule', 'schedule', 'team_stats']
}

df = pd.DataFrame(data)

# Save to Excel
excel_path = 'sample_urls.xlsx'
df.to_excel(excel_path, index=False, sheet_name='URLs')

print(f"Sample Excel file created: {excel_path}")
print(f"\nContents:")
print(df)
