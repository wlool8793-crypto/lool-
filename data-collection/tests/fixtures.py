"""
Test Fixtures and Mock Data
Provides reusable test data, mock objects, and utilities for testing.
"""

import json
from datetime import datetime
from typing import Dict, List
from unittest.mock import Mock, MagicMock
import pytest


# =============================================================================
# Mock Database Records
# =============================================================================

def mock_legal_case(**kwargs) -> Dict:
    """
    Generate a mock legal case record.

    Args:
        **kwargs: Override default values

    Returns:
        Dictionary with legal case data
    """
    defaults = {
        'id': 1,
        'case_url': 'https://indiankanoon.org/doc/12345/',
        'title': 'Test Case v. State of Testing',
        'citation': '2024 SCC 1',
        'court': 'Supreme Court of India',
        'case_date': '2024-01-15',
        'bench': 'Hon\'ble Justice Test',
        'author': 'Justice Test',
        'snippet': 'This is a test case snippet...',
        'full_text': 'This is the full text of the judgment...',
        'pdf_link': 'https://indiankanoon.org/doc/12345/',
        'pdf_downloaded': False,
        'pdf_path': None,
        'scraped_at': datetime.now(),
        'case_metadata': json.dumps({'tags': ['test', 'mock']}),
        'court_type': None,
        'court_name': 'Supreme Court',
        'state': None,
        'document_type': 'judgment',
        'year': 2024,
        'scrape_tier': 1,
        'pagination_page': 0,
        'is_historical': False
    }
    defaults.update(kwargs)
    return defaults


def mock_url_tracker(**kwargs) -> Dict:
    """
    Generate a mock URL tracker record.

    Args:
        **kwargs: Override default values

    Returns:
        Dictionary with URL tracker data
    """
    defaults = {
        'id': 1,
        'doc_url': 'https://indiankanoon.org/doc/12345/',
        'doc_id': '12345',
        'title': 'Test Case v. State of Testing',
        'citation': '2024 SCC 1',
        'court': 'Supreme Court',
        'collected_at': datetime.now(),
        'collection_page': 0,
        'download_status': 'PENDING',
        'download_attempts': 0,
        'last_attempt_at': None,
        'error_message': None,
        'pdf_downloaded': False,
        'pdf_path': None,
        'pdf_size': None,
        'uploaded_to_drive': False,
        'drive_file_id': None,
        'uploaded_at': None,
        'metadata_json': json.dumps({})
    }
    defaults.update(kwargs)
    return defaults


def generate_mock_cases(count: int = 10) -> List[Dict]:
    """
    Generate multiple mock legal cases.

    Args:
        count: Number of cases to generate

    Returns:
        List of case dictionaries
    """
    cases = []
    for i in range(count):
        case = mock_legal_case(
            id=i + 1,
            case_url=f'https://indiankanoon.org/doc/{10000 + i}/',
            title=f'Test Case {i + 1} v. State',
            citation=f'2024 SCC {i + 1}',
            year=2024 - (i % 5)  # Vary years
        )
        cases.append(case)
    return cases


def generate_mock_urls(count: int = 10) -> List[Dict]:
    """
    Generate multiple mock URL tracker records.

    Args:
        count: Number of URLs to generate

    Returns:
        List of URL dictionaries
    """
    urls = []
    for i in range(count):
        url = mock_url_tracker(
            id=i + 1,
            doc_url=f'https://indiankanoon.org/doc/{10000 + i}/',
            doc_id=f'{10000 + i}',
            title=f'Test Case {i + 1} v. State',
            citation=f'2024 SCC {i + 1}'
        )
        urls.append(url)
    return urls


# =============================================================================
# Mock HTTP Responses
# =============================================================================

def mock_search_page_html() -> str:
    """
    Generate mock IndianKanoon search results HTML.

    Returns:
        HTML string
    """
    return """
    <html>
    <body>
        <div class="result">
            <div class="result_title">
                <a href="/doc/12345/">Test Case 1 v. State</a>
            </div>
            <div class="cite">2024 SCC 1</div>
            <div class="result_snippet">This is a test snippet...</div>
        </div>
        <div class="result">
            <div class="result_title">
                <a href="/doc/12346/">Test Case 2 v. State</a>
            </div>
            <div class="cite">2024 SCC 2</div>
            <div class="result_snippet">Another test snippet...</div>
        </div>
    </body>
    </html>
    """


def mock_case_detail_html() -> str:
    """
    Generate mock case detail page HTML.

    Returns:
        HTML string
    """
    return """
    <html>
    <head><title>Test Case v. State</title></head>
    <body>
        <h1 class="doc_title">Test Case v. State of Testing</h1>
        <pre>2024 SCC 1</pre>
        <div class="judgments">
            <p>This is the full judgment text...</p>
            <p>It contains multiple paragraphs.</p>
        </div>
        <form method="POST" action="/doc/12345/">
            <input type="hidden" name="type" value="pdf"/>
            <button type="submit">Download PDF</button>
        </form>
        <a href="#">Supreme Court of India</a>
    </body>
    </html>
    """


def mock_http_response(status_code: int = 200, content: str = "",
                       headers: Dict = None) -> Mock:
    """
    Create a mock HTTP response object.

    Args:
        status_code: HTTP status code
        content: Response content
        headers: Response headers

    Returns:
        Mock response object
    """
    response = Mock()
    response.status_code = status_code
    response.content = content.encode('utf-8') if isinstance(content, str) else content
    response.text = content if isinstance(content, str) else content.decode('utf-8')
    response.headers = headers or {'content-type': 'text/html'}

    # Mock methods
    response.raise_for_status = Mock()
    if status_code >= 400:
        import requests
        response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    response.iter_content = Mock(return_value=[content.encode('utf-8')]) if isinstance(content, str) else Mock(return_value=[content])

    return response


def mock_pdf_response(size_bytes: int = 10240) -> Mock:
    """
    Create a mock PDF response.

    Args:
        size_bytes: Size of PDF in bytes

    Returns:
        Mock response object with PDF content
    """
    pdf_header = b'%PDF-1.4\n'
    pdf_content = pdf_header + b'X' * (size_bytes - len(pdf_header))

    response = mock_http_response(
        status_code=200,
        content=pdf_content,
        headers={'content-type': 'application/pdf'}
    )

    # Override iter_content for streaming
    def iter_chunks(chunk_size=8192):
        for i in range(0, len(pdf_content), chunk_size):
            yield pdf_content[i:i+chunk_size]

    response.iter_content = iter_chunks

    return response


# =============================================================================
# Mock Database Objects
# =============================================================================

class MockSession:
    """Mock SQLAlchemy session for testing."""

    def __init__(self):
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self._query_results = {}

    def add(self, obj):
        """Add an object to session."""
        self.added.append(obj)

    def commit(self):
        """Commit transaction."""
        self.committed = True

    def rollback(self):
        """Rollback transaction."""
        self.rolled_back = True

    def close(self):
        """Close session."""
        self.closed = True

    def query(self, *args, **kwargs):
        """Create a mock query."""
        return MockQuery(self._query_results.get(args[0].__name__, []))


class MockQuery:
    """Mock SQLAlchemy query for testing."""

    def __init__(self, results=None):
        self.results = results or []
        self._filters = []
        self._limit = None
        self._order = None

    def filter(self, *args, **kwargs):
        """Add filter to query."""
        self._filters.append((args, kwargs))
        return self

    def filter_by(self, **kwargs):
        """Add filter_by to query."""
        self._filters.append(kwargs)
        return self

    def limit(self, n):
        """Limit query results."""
        self._limit = n
        return self

    def order_by(self, *args):
        """Order query results."""
        self._order = args
        return self

    def first(self):
        """Get first result."""
        return self.results[0] if self.results else None

    def all(self):
        """Get all results."""
        if self._limit:
            return self.results[:self._limit]
        return self.results

    def count(self):
        """Count results."""
        return len(self.results)

    def distinct(self):
        """Get distinct results."""
        return self


# =============================================================================
# Mock WebDriver Objects
# =============================================================================

def mock_webdriver() -> Mock:
    """
    Create a mock Selenium WebDriver.

    Returns:
        Mock WebDriver object
    """
    driver = Mock()
    driver.quit = Mock()
    driver.get = Mock()
    driver.find_element = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.execute_script = Mock()
    driver.page_source = mock_case_detail_html()
    driver.current_url = 'https://indiankanoon.org/doc/12345/'

    return driver


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def sample_case() -> Dict:
    """Fixture providing a sample legal case."""
    return mock_legal_case()


@pytest.fixture
def sample_cases() -> List[Dict]:
    """Fixture providing multiple sample cases."""
    return generate_mock_cases(10)


@pytest.fixture
def sample_url() -> Dict:
    """Fixture providing a sample URL tracker record."""
    return mock_url_tracker()


@pytest.fixture
def sample_urls() -> List[Dict]:
    """Fixture providing multiple URL tracker records."""
    return generate_mock_urls(10)


@pytest.fixture
def mock_search_response() -> Mock:
    """Fixture providing a mock search response."""
    return mock_http_response(
        status_code=200,
        content=mock_search_page_html()
    )


@pytest.fixture
def mock_case_response() -> Mock:
    """Fixture providing a mock case detail response."""
    return mock_http_response(
        status_code=200,
        content=mock_case_detail_html()
    )


@pytest.fixture
def mock_pdf() -> Mock:
    """Fixture providing a mock PDF response."""
    return mock_pdf_response(10240)


@pytest.fixture
def mock_db_session() -> MockSession:
    """Fixture providing a mock database session."""
    return MockSession()


@pytest.fixture
def temp_pdf_path(tmp_path):
    """Fixture providing a temporary PDF file path."""
    pdf_file = tmp_path / "test.pdf"
    return str(pdf_file)


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture providing a temporary directory."""
    return str(tmp_path)


# =============================================================================
# Test Data Generators
# =============================================================================

class TestDataGenerator:
    """Generate various test data patterns."""

    @staticmethod
    def generate_urls_for_download(count: int = 100,
                                   failed_count: int = 0) -> List[Dict]:
        """
        Generate URLs for download testing.

        Args:
            count: Number of successful URLs
            failed_count: Number of URLs that should fail

        Returns:
            List of URL dictionaries
        """
        urls = []

        # Successful URLs
        for i in range(count):
            urls.append({
                'url': f'https://indiankanoon.org/doc/{10000 + i}/',
                'doc_id': f'{10000 + i}',
                'metadata': {'page': i // 10}
            })

        # Failed URLs (invalid format)
        for i in range(failed_count):
            urls.append({
                'url': f'https://invalid-url-{i}',
                'doc_id': f'invalid-{i}',
                'metadata': {'should_fail': True}
            })

        return urls

    @staticmethod
    def generate_database_records(table: str, count: int = 10) -> List:
        """
        Generate mock database records.

        Args:
            table: Table name ('legal_cases' or 'url_tracker')
            count: Number of records

        Returns:
            List of mock records
        """
        if table == 'legal_cases':
            return generate_mock_cases(count)
        elif table == 'url_tracker':
            return generate_mock_urls(count)
        else:
            raise ValueError(f"Unknown table: {table}")


# =============================================================================
# Assertion Helpers
# =============================================================================

def assert_valid_case_data(case: Dict):
    """
    Assert that a case dictionary has valid structure.

    Args:
        case: Case dictionary to validate

    Raises:
        AssertionError: If case data is invalid
    """
    required_fields = ['url', 'title', 'citation']
    for field in required_fields:
        assert field in case, f"Missing required field: {field}"
        assert case[field], f"Field {field} should not be empty"


def assert_valid_url_data(url: Dict):
    """
    Assert that a URL dictionary has valid structure.

    Args:
        url: URL dictionary to validate

    Raises:
        AssertionError: If URL data is invalid
    """
    required_fields = ['url', 'doc_id']
    for field in required_fields:
        assert field in url, f"Missing required field: {field}"
        assert url[field], f"Field {field} should not be empty"
