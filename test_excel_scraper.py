"""
Test the Excel scraper service.
"""
import asyncio
from src.services.excel_scraper_service import (
    read_excel_urls,
    extract_tables_from_url,
    add_metadata_columns,
    scrape_from_excel
)

async def test_excel_reader():
    """Test reading URLs from Excel file."""
    print("=" * 60)
    print("TEST 1: Reading URLs from Excel")
    print("=" * 60)

    try:
        df = read_excel_urls('sample_urls.xlsx')
        print(f"✓ Successfully read {len(df)} URLs from Excel")
        print("\nURLs found:")
        for idx, row in df.iterrows():
            print(f"  {idx + 1}. {row['url']}")
            print(f"     Season: {row.get('season', 'N/A')}")
            print(f"     Entity Type: {row.get('entity_type', 'N/A')}")
            print(f"     Table Type: {row.get('table_type', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Failed to read Excel: {e}")
        return False

async def test_table_extraction():
    """Test extracting tables from a URL."""
    print("\n" + "=" * 60)
    print("TEST 2: Extracting tables from URL")
    print("=" * 60)

    # Use a simple URL for testing
    test_url = 'https://www.pro-football-reference.com/years/2024/'

    try:
        print(f"Fetching: {test_url}")
        tables = extract_tables_from_url(test_url)
        print(f"✓ Successfully extracted {len(tables)} tables")

        print("\nTables found:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table['table_id']} - {table['table_name']}")
            print(f"     Source: {table['source']}")
            print(f"     Rows: {len(table['dataframe'])}")
            print(f"     Columns: {list(table['dataframe'].columns[:5])}...")

        return True
    except Exception as e:
        print(f"✗ Failed to extract tables: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_scrape():
    """Test the full scraping pipeline."""
    print("\n" + "=" * 60)
    print("TEST 3: Full scraping pipeline")
    print("=" * 60)

    # Create a minimal test Excel file with just one URL
    import pandas as pd
    test_data = {
        'url': ['https://www.pro-football-reference.com/years/2024/'],
        'season': [2024],
        'entity_type': ['league'],
        'table_type': ['team_stats']
    }
    test_df = pd.DataFrame(test_data)
    test_excel = 'test_minimal.xlsx'
    test_df.to_excel(test_excel, index=False)
    print(f"Created test Excel: {test_excel}")

    try:
        results = await scrape_from_excel(test_excel)

        print(f"\n✓ Scraping completed")
        print(f"\nResults:")
        print(f"  URLs processed: {results['urls_processed']}")
        print(f"  URLs successful: {results['urls_success']}")
        print(f"  URLs failed: {results['urls_failed']}")
        print(f"  Tables extracted: {results['tables_extracted']}")
        print(f"  Rows inserted: {results['rows_inserted']}")

        if results['errors']:
            print(f"\n  Errors:")
            for error in results['errors']:
                print(f"    - {error}")

        return results['urls_success'] > 0
    except Exception as e:
        print(f"✗ Full scrape failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("EXCEL SCRAPER SERVICE TEST SUITE")
    print("=" * 60 + "\n")

    results = []

    # Test 1: Excel reading
    results.append(await test_excel_reader())

    # Test 2: Table extraction
    results.append(await test_table_extraction())

    # Test 3: Full pipeline (commented out to avoid hitting the database)
    print("\n" + "=" * 60)
    print("TEST 3: Full scraping pipeline (SKIPPED - requires DB)")
    print("=" * 60)
    print("This test would insert data into the database.")
    print("Run it manually if you want to test database insertion.")
    # results.append(await test_full_scrape())

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

if __name__ == '__main__':
    asyncio.run(main())
