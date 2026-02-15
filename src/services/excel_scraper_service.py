"""
Excel-based URL scraper service for Pro-Football-Reference data.

This service reads URLs from an Excel file and scrapes stat tables from each URL,
then stores them in the database with metadata.
"""

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import SessionLocal


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


def create_table_if_not_exists(db: Session, table_name: str, df: pd.DataFrame) -> None:
    """
    Dynamically create database table based on DataFrame structure.

    Args:
        db: Database session
        table_name: Name for the database table
        df: DataFrame to base table structure on
    """
    # Clean table name (remove special characters)
    clean_table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name.lower())

    # Build CREATE TABLE statement
    columns = []
    columns.append("id SERIAL PRIMARY KEY")

    for col in df.columns:
        clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(col).lower())

        # Determine data type based on pandas dtype
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            sql_type = "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            sql_type = "FLOAT"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            sql_type = "TIMESTAMP"
        else:
            sql_type = "TEXT"

        columns.append(f"{clean_col} {sql_type}")

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {clean_table_name} (
        {', '.join(columns)}
    )
    """

    try:
        db.execute(text(create_sql))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Warning: Could not create table {clean_table_name}: {e}")


def upsert_dataframe(db: Session, table_name: str, df: pd.DataFrame) -> int:
    """
    Insert or update DataFrame rows into database table.

    Uses a simple strategy: delete existing rows with same source_url and insert new ones.
    This ensures idempotent runs.

    Args:
        db: Database session
        table_name: Target table name
        df: DataFrame to insert

    Returns:
        Number of rows inserted
    """
    clean_table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name.lower())

    # Delete existing rows from same source_url (if that column exists)
    if 'source_url' in df.columns:
        source_urls = df['source_url'].unique()
        for source_url in source_urls:
            delete_sql = text(f"DELETE FROM {clean_table_name} WHERE source_url = :url")
            db.execute(delete_sql, {"url": source_url})

    # Insert new rows
    rows_inserted = 0
    for _, row in df.iterrows():
        # Clean column names
        clean_cols = []
        values = []
        placeholders = []

        for idx, (col, val) in enumerate(row.items()):
            clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(col).lower())
            clean_cols.append(clean_col)

            # Convert NaN to None
            if pd.isna(val):
                values.append(None)
            else:
                values.append(val)

            placeholders.append(f":val{idx}")

        insert_sql = text(f"""
            INSERT INTO {clean_table_name} ({', '.join(clean_cols)})
            VALUES ({', '.join(placeholders)})
        """)

        params = {f"val{idx}": val for idx, val in enumerate(values)}

        try:
            db.execute(insert_sql, params)
            rows_inserted += 1
        except Exception as e:
            print(f"Warning: Could not insert row: {e}")
            continue

    db.commit()
    return rows_inserted


async def scrape_from_excel(excel_path: str) -> Dict[str, Any]:
    """
    Main function to scrape URLs from Excel file and store in database.

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

    results = {
        'urls_processed': 0,
        'urls_success': 0,
        'urls_failed': 0,
        'tables_extracted': 0,
        'rows_inserted': 0,
        'errors': []
    }

    try:
        # Read URLs from Excel
        urls_df = read_excel_urls(excel_path)
        results['urls_processed'] = len(urls_df)

        # Process each URL
        for idx, row in urls_df.iterrows():
            url = row['url']

            # Extract metadata
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

                    # Add metadata
                    df = add_metadata_columns(df, url, metadata)

                    # Create table and insert data
                    table_name = f"scraped_{table_id}"
                    create_table_if_not_exists(db, table_name, df)
                    rows = upsert_dataframe(db, table_name, df)
                    results['rows_inserted'] += rows

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
