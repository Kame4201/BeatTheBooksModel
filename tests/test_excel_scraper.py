"""
Pytest tests for Excel scraper functionality.
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.excel_scraper_service import (
    read_excel_urls,
    add_metadata_columns,
    extract_tables_from_url
)


class TestExcelReading:
    """Tests for Excel file reading."""

    def test_read_excel_urls_with_valid_file(self, tmp_path):
        """Test reading a valid Excel file with URL column."""
        # Create temporary Excel file
        excel_file = tmp_path / "test_urls.xlsx"
        df = pd.DataFrame({
            'url': ['https://example.com/1', 'https://example.com/2'],
            'season': [2024, 2024],
            'entity_type': ['team', 'league']
        })
        df.to_excel(excel_file, index=False)

        # Read it back
        result = read_excel_urls(str(excel_file))

        assert len(result) == 2
        assert 'url' in result.columns
        assert result['url'].iloc[0] == 'https://example.com/1'
        assert result['season'].iloc[0] == 2024

    def test_read_excel_urls_missing_url_column(self, tmp_path):
        """Test that reading Excel without 'url' column raises error."""
        excel_file = tmp_path / "bad_urls.xlsx"
        df = pd.DataFrame({
            'link': ['https://example.com/1'],  # Wrong column name
            'season': [2024]
        })
        df.to_excel(excel_file, index=False)

        with pytest.raises(ValueError, match="must contain 'url' column"):
            read_excel_urls(str(excel_file))

    def test_read_excel_urls_filters_empty_urls(self, tmp_path):
        """Test that empty URLs are filtered out."""
        excel_file = tmp_path / "test_urls.xlsx"
        df = pd.DataFrame({
            'url': ['https://example.com/1', None, 'https://example.com/2'],
            'season': [2024, 2024, 2024]
        })
        df.to_excel(excel_file, index=False)

        result = read_excel_urls(str(excel_file))

        assert len(result) == 2  # Only non-null URLs


class TestMetadataColumns:
    """Tests for adding metadata columns to DataFrames."""

    def test_add_metadata_columns_basic(self):
        """Test adding basic metadata columns."""
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        url = 'https://example.com/test'
        metadata = {}

        result = add_metadata_columns(df, url, metadata)

        assert 'source_url' in result.columns
        assert 'scraped_at' in result.columns
        assert result['source_url'].iloc[0] == url
        assert isinstance(result['scraped_at'].iloc[0], datetime)

    def test_add_metadata_columns_with_season(self):
        """Test adding metadata with season."""
        df = pd.DataFrame({'col1': [1, 2]})
        metadata = {'season': 2024, 'entity_type': 'team'}

        result = add_metadata_columns(df, 'https://example.com', metadata)

        assert 'season' in result.columns
        assert 'entity_type' in result.columns
        assert result['season'].iloc[0] == 2024
        assert result['entity_type'].iloc[0] == 'team'

    def test_add_metadata_columns_skips_nan_values(self):
        """Test that NaN metadata values are skipped."""
        df = pd.DataFrame({'col1': [1, 2]})
        metadata = {'season': float('nan'), 'entity_type': 'team'}

        result = add_metadata_columns(df, 'https://example.com', metadata)

        assert 'season' not in result.columns
        assert 'entity_type' in result.columns


class TestTableExtraction:
    """Tests for table extraction from URLs."""

    @patch('src.services.excel_scraper_service.requests.get')
    @patch('src.services.excel_scraper_service.time.sleep')
    def test_extract_tables_basic(self, mock_sleep, mock_get):
        """Test basic table extraction from HTML."""
        # Mock HTML response with a simple table
        mock_response = Mock()
        mock_response.text = """
        <html>
            <table id="test_table">
                <caption>Test Table</caption>
                <tr><th>Col1</th><th>Col2</th></tr>
                <tr><td>1</td><td>A</td></tr>
                <tr><td>2</td><td>B</td></tr>
            </table>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Skip the sleep
        mock_sleep.return_value = None

        # Extract tables
        result = extract_tables_from_url('https://example.com/test')

        assert len(result) > 0
        assert 'table_id' in result[0]
        assert 'dataframe' in result[0]
        assert isinstance(result[0]['dataframe'], pd.DataFrame)

    @patch('src.services.excel_scraper_service.requests.get')
    @patch('src.services.excel_scraper_service.time.sleep')
    def test_extract_tables_handles_errors(self, mock_sleep, mock_get):
        """Test that extraction handles HTTP errors gracefully."""
        mock_get.side_effect = Exception("Connection error")
        mock_sleep.return_value = None

        with pytest.raises(Exception):
            extract_tables_from_url('https://example.com/test')


class TestEndToEndMocked:
    """End-to-end tests with mocked dependencies."""

    @pytest.mark.asyncio
    @patch('src.services.excel_scraper_service.SessionLocal')
    @patch('src.services.excel_scraper_service.extract_tables_from_url')
    @patch('src.services.excel_scraper_service.read_excel_urls')
    async def test_scrape_from_excel_success(self, mock_read, mock_extract, mock_session):
        """Test full scraping flow with mocked dependencies."""
        from src.services.excel_scraper_service import scrape_from_excel

        # Mock Excel reading
        mock_df = pd.DataFrame({
            'url': ['https://example.com/1'],
            'season': [2024],
            'entity_type': ['team']
        })
        mock_read.return_value = mock_df

        # Mock table extraction
        mock_table_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_extract.return_value = [{
            'table_id': 'test_table',
            'table_name': 'Test Table',
            'dataframe': mock_table_df,
            'source': 'visible'
        }]

        # Mock database session and repository
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        # Run the scraper
        result = await scrape_from_excel('test.xlsx')

        # Verify results
        assert result['urls_processed'] == 1
        assert result['urls_success'] == 1
        assert result['urls_failed'] == 0
        assert result['tables_extracted'] == 1
        assert len(result['errors']) == 0


# Integration test (requires actual database connection)
class TestIntegration:
    """Integration tests - require database connection."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scrape_real_excel_file(self):
        """
        Test scraping with real Excel file (requires database).
        Run with: pytest -m integration
        """
        pytest.skip("Requires database connection and real Excel file")
        # This would be run manually when you want to test the full flow
        # from src.services.excel_scraper_service import scrape_from_excel
        # excel_path = r"C:\Users\PC\Downloads\Links and tables for data (4).xlsx"
        # result = await scrape_from_excel(excel_path)
        # assert result['urls_processed'] > 0
