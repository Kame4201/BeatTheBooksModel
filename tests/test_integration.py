"""
Integration test for scraping real Excel file.
Run this with: pytest tests/test_integration.py -v
"""
import pytest
import asyncio
from src.services.excel_scraper_service import scrape_from_excel


@pytest.mark.asyncio
async def test_scrape_real_excel():
    """
    Test scraping with your actual Excel file.

    This will:
    1. Read your Excel file
    2. Scrape all URLs
    3. Store data in database
    4. Return results
    """
    # Your Excel file path
    excel_path = r"C:\Users\PC\Downloads\Links and tables for data (4).xlsx"

    print("\n" + "="*70)
    print("STARTING EXCEL SCRAPER TEST")
    print("="*70)
    print(f"Excel file: {excel_path}")
    print("\nThis will scrape all URLs and store in database...")
    print("Note: With 60-second delays, this will take time!")
    print("="*70 + "\n")

    # Run the scraper
    result = await scrape_from_excel(excel_path)

    # Print results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"URLs Processed:     {result['urls_processed']}")
    print(f"URLs Success:       {result['urls_success']}")
    print(f"URLs Failed:        {result['urls_failed']}")
    print(f"Tables Extracted:   {result['tables_extracted']}")
    print(f"Rows Inserted:      {result['rows_inserted']}")

    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  - {error}")
    else:
        print("\n✓ No errors!")

    print("="*70 + "\n")

    # Assertions
    assert result['urls_processed'] > 0, "No URLs were processed"
    assert 'errors' in result

    if result['urls_failed'] > 0:
        pytest.fail(f"Some URLs failed: {result['errors']}")

    return result


def test_check_excel_file_exists():
    """Check if the Excel file exists before trying to scrape."""
    import os
    excel_path = r"C:\Users\PC\Downloads\Links and tables for data (4).xlsx"

    # Convert to Unix-style path for WSL
    if excel_path.startswith('C:\\'):
        unix_path = '/c/' + excel_path[3:].replace('\\', '/')
    else:
        unix_path = excel_path

    print(f"\nChecking for Excel file...")
    print(f"Windows path: {excel_path}")
    print(f"Unix path: {unix_path}")

    # Try both paths
    exists = os.path.exists(excel_path) or os.path.exists(unix_path)

    if not exists:
        pytest.skip(f"Excel file not found at {excel_path}")
    else:
        print(f"✓ Excel file found!")


if __name__ == '__main__':
    # Allow running directly with: python tests/test_integration.py
    print("Running integration test...")
    asyncio.run(test_scrape_real_excel())
