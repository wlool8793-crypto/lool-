"""
Pytest configuration and fixtures for Neo4j Legal Knowledge Graph tests
"""
import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# Set test environment variables
os.environ['NEO4J_URL'] = 'bolt://localhost:7687'
os.environ['NEO4J_USERNAME'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'test_password'
os.environ['NEO4J_DATABASE'] = 'neo4j'


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for unit tests"""
    driver = Mock()
    session = Mock()
    transaction = Mock()

    # Mock session context manager
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)

    # Mock transaction context manager
    transaction.__enter__ = Mock(return_value=transaction)
    transaction.__exit__ = Mock(return_value=False)

    # Mock run method
    session.run = Mock(return_value=Mock())
    transaction.run = Mock(return_value=Mock())

    # Mock begin_transaction
    session.begin_transaction = Mock(return_value=transaction)

    # Mock driver.session
    driver.session = Mock(return_value=session)

    return driver


@pytest.fixture
def sample_case_data() -> Dict[str, Any]:
    """Sample case data for testing"""
    return {
        "id": "test_case_1",
        "name": "Test Petitioner vs Test Respondent",
        "citation": "123 TEST 456",
        "year": 2023,
        "date": "2023-01-15",
        "topic": "Test Topic",
        "court": "Test Court",
        "judges": ["Judge A", "Judge B"],
        "petitioner": ["Test Petitioner"],
        "respondent": ["Test Respondent"],
        "sections": ["Section 1", "Section 2"],
        "principles": ["Test Principle"],
        "abstract": "This is a test case abstract",
        "issue": "Test issue",
        "holding": "Test holding",
        "significance": "Test significance"
    }


@pytest.fixture
def sample_cpc_data() -> Dict[str, Any]:
    """Sample CPC data structure for testing"""
    return {
        "cases": [
            {
                "id": "case_1",
                "name": "Test Case 1",
                "citation": "100 DLR 100",
                "year": 2020,
                "court": "High Court Division",
                "judges": ["Judge 1"],
                "petitioner": ["Petitioner 1"],
                "respondent": ["Respondent 1"],
                "sections": ["Section 10"],
                "principles": ["Test Principle"]
            }
        ],
        "sections": [
            {
                "id": "sec_10",
                "section_id": "Section 10",
                "statute": "Code of Civil Procedure, 1908",
                "title": "Test Section",
                "description": "Test description"
            }
        ],
        "courts": [
            {
                "id": "high_court",
                "name": "High Court Division",
                "type": "Appellate Court"
            }
        ],
        "principles": [
            {
                "id": "test_principle",
                "name": "Test Principle",
                "description": "Test principle description",
                "category": "Procedural Law"
            }
        ],
        "statutes": [
            {
                "id": "cpc_1908",
                "name": "Code of Civil Procedure, 1908",
                "short_name": "CPC",
                "country": "Bangladesh"
            }
        ]
    }


@pytest.fixture
def temp_json_file(tmp_path, sample_cpc_data):
    """Create temporary JSON file with sample data"""
    json_file = tmp_path / "test_cpc_data.json"
    with open(json_file, 'w') as f:
        json.dump(sample_cpc_data, f)
    return json_file


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Create temporary PDF file for testing"""
    pdf_file = tmp_path / "test_case.pdf"
    # Create a minimal PDF (just for testing file existence)
    pdf_file.write_bytes(b'%PDF-1.4\n%Test PDF\n%%EOF')
    return pdf_file


@pytest.fixture
def sample_pdf_text() -> str:
    """Sample PDF text for extraction testing"""
    return """
    60 DLR 20

    Siddique Mia vs Md Idris Miah and others

    High Court Division
    Justice Siddiqur Rahman Miah, J.
    Justice Md Rezaul Haque, J.

    Case Type: Revision
    Date: January 28, 2007

    Sections Applied: Section 10, Section 115(4), Order VI, rule 17

    Abstract:
    This case addresses the principle of finality in interlocutory matters and the
    limits of judicial discretion in allowing amendments to pleadings.

    Issue:
    Whether a party can file a second application for amendment with the same content
    after the first application was rejected.

    Holding:
    Rule made absolute. Matter decided at one stage cannot be re-agitated at
    subsequent stage (res judicata between stages).

    Significance:
    Reinforces res judicata between stages principle.
    """


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before each test"""
    yield
    # Cleanup after test if needed


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


# Integration test fixtures (require actual Neo4j)
@pytest.fixture(scope="session")
def neo4j_connection():
    """
    Real Neo4j connection for integration tests
    Requires Neo4j to be running locally
    """
    try:
        from neo4j import GraphDatabase

        uri = os.getenv('NEO4J_TEST_URL', 'bolt://localhost:7687')
        username = os.getenv('NEO4J_TEST_USERNAME', 'neo4j')
        password = os.getenv('NEO4J_TEST_PASSWORD', 'test')

        driver = GraphDatabase.driver(uri, auth=(username, password))

        # Test connection
        with driver.session() as session:
            session.run("RETURN 1")

        yield driver

        driver.close()

    except Exception as e:
        pytest.skip(f"Neo4j not available for integration tests: {str(e)}")


# Skip markers for tests that require external services
def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "requires_neo4j: mark test as requiring Neo4j connection"
    )
    config.addinivalue_line(
        "markers", "requires_google_api: mark test as requiring Google API key"
    )
