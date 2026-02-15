"""
Excel-based URL scraper service for Pro-Football-Reference data.

This service reads URLs from an Excel file and scrapes stat tables from each URL,
then stores them in the database with metadata using the repository layer.
"""

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from typing import List, Dict, Any

from src.core.database import SessionLocal
from src.repositories.scraped_data_repo import ScrapedDataRepository
from src.dtos.scraped_data_dto import ScrapedDataMetadataCreate


def read_excel_urls(excel_path: str) -> pd.DataFrame:
    """
    Read URLs and metadata from Excel file.

    Args:
        excel_path: Path to Excel file

    Returns:
        DataFrame with columns: url (required), season, entity_type, table_type (optional)

    Raises:
        ValueError: If 'url' column is missing
        FileNotFoundError: If Excel file doesn't exist
    """
    # Read all sheets and concatenate them
    excel_file = pd.ExcelFile(excel_path)
    all_dfs = []

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        all_dfs.append(df)

    # Combine all sheets
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Validate required column
    if 'url' not in combined_df.columns:
        raise ValueError("Excel file must contain 'url' column")

    # Remove rows with empty URLs
    combined_df = combined_df[combined_df['url'].notna()]

    return combined_df


def extract_tables_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Fetch HTML from URL and extract all stat tables.

    Args:
        url: Pro-Football-Reference URL to scrape

    Returns:
        List of dictionaries containing table data and metadata
        Each dict has keys: table_id, table_name, dataframe, source
    """
    # Enhanced headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # Add delay to be respectful to the server
    time.sleep(2)  # 2 second delay between requests

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    extracted_tables = []

    # Method 1: Extract visible tables
    visible_tables = soup.find_all('table')
    for table in visible_tables:
        table_id = table.get('id', 'unknown')
        table_caption = table.find('caption')
        table_name = table_caption.get_text(strip=True) if table_caption else table_id

        try:
            # Convert HTML table to DataFrame
            df = pd.read_html(str(table))[0]

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(str(c).strip() for c in col if str(c) != 'nan' and not str(c).startswith('Unnamed'))
                             or col[0] for col in df.columns.values]

            extracted_tables.append({
                'table_id': table_id,
                'table_name': table_name,
                'dataframe': df,
                'source': 'visible'
            })
        except Exception as e:
            print(f"Warning: Could not parse visible table {table_id}: {e}")
            continue

    # Method 2: Extract tables from HTML comments (PFR often hides tables in comments)
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if 'table' in comment:
            try:
                comment_soup = BeautifulSoup(comment, 'lxml')
                tables = comment_soup.find_all('table')

                for table in tables:
                    table_id = table.get('id', 'unknown_comment')
                    table_caption = table.find('caption')
                    table_name = table_caption.get_text(strip=True) if table_caption else table_id

                    try:
                        df = pd.read_html(str(table))[0]

                        # Flatten MultiIndex columns
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = ['_'.join(str(c).strip() for c in col if str(c) != 'nan' and not str(c).startswith('Unnamed'))
                                         or col[0] for col in df.columns.values]

                        extracted_tables.append({
                            'table_id': table_id,
                            'table_name': table_name,
                            'dataframe': df,
                            'source': 'comment'
                        })
                    except Exception as e:
                        print(f"Warning: Could not parse commented table {table_id}: {e}")
                        continue
            except Exception as e:
                print(f"Warning: Could not parse comment: {e}")
                continue

    return extracted_tables


def add_metadata_columns(df: pd.DataFrame, url: str, metadata: Dict[str, Any]) -> pd.DataFrame:
    """
    Add metadata columns to DataFrame.

    Args:
        df: DataFrame to add metadata to
        url: Source URL
        metadata: Additional metadata from Excel row

    Returns:
        DataFrame with added metadata columns
    """
    df = df.copy()

    # Add standard metadata
    df['source_url'] = url
    df['scraped_at'] = datetime.now()

    # Add optional metadata from Excel
    if 'season' in metadata and pd.notna(metadata['season']):
        df['season'] = metadata['season']

    if 'entity_type' in metadata and pd.notna(metadata['entity_type']):
        df['entity_type'] = metadata['entity_type']

    if 'table_type' in metadata and pd.notna(metadata['table_type']):
        df['table_type'] = metadata['table_type']

    return df


# Database operations have been moved to the repository layer
# See src/repositories/scraped_data_repo.py for:
# - create_dynamic_table()
# - upsert_dataframe()
# - delete_by_source_url()
# - insert_dataframe_rows()


async def scrape_from_excel(excel_path: str) -> Dict[str, Any]:
    """
    Main function to scrape URLs from Excel file and store in database.

    Uses the repository layer for all database operations following proper
    architectural patterns with entities, DTOs, and repositories.

    Args:
        excel_path: Path to Excel file containing URLs

    Returns:
        Dictionary with summary of scraping results:
        - urls_processed: Number of URLs attempted
        - urls_success: Number of URLs successfully scraped
        - urls_failed: Number of URLs that failed
        - tables_extracted: Total number of tables extracted
        - rows_inserted: Total number of rows inserted
        - errors: List of error messages
    """
    db = SessionLocal()
    repo = ScrapedDataRepository(db)

    results = {
        'urls_processed': 0,
        'urls_success': 0,
        'urls_failed': 0,
        'tables_extracted': 0,
        'rows_inserted': 0,
        'errors': []
    }

    try:
        # Ensure metadata tracking table exists
        repo.create_metadata_table_if_not_exists()

        # Read URLs from Excel
        urls_df = read_excel_urls(excel_path)
        results['urls_processed'] = len(urls_df)

        # Process each URL
        for idx, row in urls_df.iterrows():
            url = row['url']

            # Extract metadata from Excel row
            metadata = {
                'season': row.get('season'),
                'entity_type': row.get('entity_type'),
                'table_type': row.get('table_type')
            }

            try:
                # Extract tables from URL
                tables = extract_tables_from_url(url)
                results['tables_extracted'] += len(tables)

                # Process each table
                for table_info in tables:
                    df = table_info['dataframe']
                    table_id = table_info['table_id']
                    table_name = table_info['table_name']
                    source_type = table_info['source']

                    # Add metadata columns to DataFrame
                    df = add_metadata_columns(df, url, metadata)

                    # Create dynamic table name
                    dynamic_table_name = f"scraped_{table_id}"

                    # Use repository to create table if needed
                    repo.create_dynamic_table(dynamic_table_name, df)

                    # Use repository to upsert data (idempotent)
                    rows = repo.upsert_dataframe(dynamic_table_name, df)
                    results['rows_inserted'] += rows

                    # Track metadata in scraped_data_metadata table using DTO
                    metadata_dto = ScrapedDataMetadataCreate(
                        source_url=url,
                        table_id=table_id,
                        table_name=table_name,
                        scraped_at=datetime.now(),
                        season=metadata.get('season'),
                        entity_type=metadata.get('entity_type'),
                        table_type=metadata.get('table_type'),
                        rows_scraped=rows,
                        source_type=source_type
                    )
                    repo.track_scraped_data(metadata_dto)

                results['urls_success'] += 1

            except Exception as e:
                error_msg = f"Failed to process {url}: {str(e)}"
                results['errors'].append(error_msg)
                results['urls_failed'] += 1
                print(error_msg)
                continue

        return results

    except Exception as e:
        results['errors'].append(f"Fatal error: {str(e)}")
        return results

    finally:
        db.close()
