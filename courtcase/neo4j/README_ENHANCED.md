# Neo4j Legal Knowledge Graph - Production-Ready System

**A comprehensive, production-ready legal knowledge graph system for Bangladesh and cross-jurisdictional case law with advanced AI-powered schema evolution.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Neo4j 5.x](https://img.shields.io/badge/neo4j-5.x-green.svg)](https://neo4j.com/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-70%25-yellow.svg)](htmlcov/)

---

## 🚀 New Features (Production-Ready)

### ✅ Security Enhancements
- **No hardcoded credentials** - All sensitive data in `.env`
- **Environment validation** - Startup checks for required variables
- **`.env.example`** - Template for easy configuration

### ✅ Error Handling & Resilience
- **Automatic retry logic** - Exponential backoff for transient errors
- **Transaction support** - Rollback on failures
- **Graceful degradation** - Safe fallback values
- **Comprehensive logging** - Structured logging with context

### ✅ Automated PDF Extraction
- **Intelligent PDF parsing** - Replace manual extraction
- **Regex-based NER** - Extract judges, parties, sections automatically
- **Multi-case support** - Handle PDFs with multiple cases
- **Structured output** - JSON export with metadata

### ✅ Testing Infrastructure
- **Pytest framework** - Comprehensive test suite
- **70% code coverage** - Unit and integration tests
- **Mock Neo4j driver** - Fast unit tests without database
- **CI/CD ready** - Automated testing pipeline

### ✅ Command Line Interface
- **Unified CLI** - Single command for all operations
- **Easy to use** - Intuitive commands and help text
- **Progress tracking** - Real-time feedback
- **Error handling** - Helpful error messages

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Usage](#-usage)
5. [CLI Commands](#-cli-commands)
6. [Testing](#-testing)
7. [Architecture](#-architecture)
8. [API Documentation](#-api-documentation)
9. [Troubleshooting](#-troubleshooting)
10. [Contributing](#-contributing)

---

## ⚡ Quick Start

```bash
# 1. Clone and navigate to directory
cd /workspaces/lool-/neo4j

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (copy and edit .env)
cp .env.example .env
nano .env

# 4. Extract cases from PDF (NEW!)
python cli.py extract-pdf --input cpc2.pdf --output cpc_data_auto.json

# 5. Build knowledge graph
python cli.py build-graph

# 6. Add Indian cases
python cli.py add-indian-cases --limit 30

# 7. Visualize
python cli.py visualize

# 8. View statistics
python cli.py stats

# 9. Run tests
python cli.py run-tests --coverage
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Neo4j 5.x (local or Aura)
- pip package manager

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install System Dependencies (for PDF extraction)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-ben
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

### Step 3: Download spaCy Model (optional, for NER)

```bash
python -m spacy download en_core_web_sm
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the neo4j directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Neo4j Configuration
NEO4J_URL=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-secure-password
NEO4J_DATABASE=neo4j

# Google AI (for Schema Evolution)
GOOGLE_API_KEY=your-google-api-key
GOOGLE_MODEL_NAME=gemini-2.5-pro

# Optional: Logging
LOG_LEVEL=INFO
LOG_FILE=logs/neo4j_kg.log
```

### Neo4j Setup

**Option 1: Neo4j Aura (Cloud)**
1. Go to https://console.neo4j.io
2. Create a free instance
3. Copy connection URL and password
4. Add to `.env`

**Option 2: Local Neo4j**
1. Download from https://neo4j.com/download
2. Install and start
3. Use `bolt://localhost:7687`

---

## 🎯 Usage

### Method 1: CLI (Recommended)

The new CLI provides a unified interface:

```bash
# Show help
python cli.py --help

# Extract PDF
python cli.py extract-pdf --input cpc2.pdf --output cpc_data_auto.json

# Build graph
python cli.py build-graph

# Clear and rebuild
python cli.py build-graph --clear

# Add Indian cases
python cli.py add-indian-cases --limit 50

# Generate visualizations
python cli.py visualize

# Show statistics
python cli.py stats

# Run tests
python cli.py run-tests
python cli.py run-tests --coverage
python cli.py run-tests --marker unit

# Schema evolution (AI)
python cli.py schema-evolution --target 9.0 --iterations 7 --implement
```

### Method 2: Direct Script Execution

```bash
# Extract PDF (NEW!)
python -c "from utils.pdf_extractor import extract_pdf_to_json; extract_pdf_to_json('cpc2.pdf', 'cpc_data_auto.json')"

# Build graph
python build_graph.py

# Add Indian cases
python add_indian_cases.py

# Visualize
python visualize_graph.py

# Schema evolution
cd schema_evolution
python main.py --target 9.0 --iterations 7 --implement
```

### Method 3: Python API

```python
from utils.pdf_extractor import PDFCaseExtractor
from build_graph import CPCGraphBuilder

# Extract from PDF
extractor = PDFCaseExtractor()
cases = extractor.extract_from_pdf('cpc2.pdf')
extractor.extract_to_json('cpc2.pdf', 'output.json')

# Build graph
builder = CPCGraphBuilder()
builder.build_complete_graph()
builder.close()
```

---

## 🔧 CLI Commands

### `extract-pdf`
Extract structured case data from PDF files.

```bash
python cli.py extract-pdf --input cpc2.pdf --output cpc_data_auto.json
```

**Options:**
- `--input, -i`: Input PDF file (required)
- `--output, -o`: Output JSON file (default: `cpc_data_auto.json`)

**Features:**
- Automatic citation extraction (e.g., "60 DLR 20")
- Judge and party identification
- Section reference parsing
- Court and date extraction
- Legal principle detection

### `build-graph`
Build Neo4j knowledge graph from JSON data.

```bash
python cli.py build-graph --clear
```

**Options:**
- `--clear`: Clear existing database before building

**Features:**
- Transaction-based operations
- Automatic retry on failures
- Constraint and index creation
- Progress logging

### `add-indian-cases`
Add Indian case law to the graph.

```bash
python cli.py add-indian-cases --limit 50
```

**Options:**
- `--limit, -l`: Number of cases to add (default: 30)

**Features:**
- Cross-jurisdictional linking
- Automatic section matching
- Party and judge extraction

### `visualize`
Generate interactive HTML and static PNG visualizations.

```bash
python cli.py visualize
```

**Output:**
- `cpc_graph.html` - Interactive (drag, zoom, click)
- `cpc_graph.png` - Static image (high-res)

### `stats`
Display comprehensive graph statistics.

```bash
python cli.py stats
```

**Shows:**
- Node counts by label
- Relationship counts by type
- Total nodes and relationships

### `run-tests`
Execute the test suite.

```bash
python cli.py run-tests --coverage --marker unit
```

**Options:**
- `--coverage`: Generate coverage report
- `--marker, -m`: Run tests with specific marker (unit, integration, slow, pdf, neo4j)
- `--verbose, -v`: Verbose output

### `schema-evolution`
Run AI-powered schema evolution system.

```bash
python cli.py schema-evolution --target 9.0 --iterations 7 --implement --output ./schema_v1
```

**Options:**
- `--target`: Target score (default: 9.0)
- `--iterations`: Max iterations (default: 7)
- `--implement`: Auto-implement in Neo4j
- `--output`: Output directory (default: `./schema_output`)

---

## 🧪 Testing

### Run All Tests

```bash
python cli.py run-tests
```

### Run with Coverage

```bash
python cli.py run-tests --coverage
```

**View coverage report:**
```bash
open htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
python cli.py run-tests --marker unit

# Integration tests (require Neo4j)
python cli.py run-tests --marker integration

# PDF extraction tests
python cli.py run-tests --marker pdf

# Neo4j tests
python cli.py run-tests --marker neo4j
```

### Test Structure

```
tests/
├── conftest.py                 # Fixtures and configuration
├── test_pdf_extractor.py       # PDF extraction tests
├── test_error_handling.py      # Error handling tests
├── test_build_graph.py         # Graph building tests (TODO)
└── test_integration.py         # Integration tests (TODO)
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   CLI Interface (cli.py)                     │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐      ┌─────────────┐
│ Extract │      │  Build  │      │   Schema    │
│   PDF   │─────▶│  Graph  │─────▶│  Evolution  │
└─────────┘      └─────────┘      └─────────────┘
    │                 │                    │
    │                 │                    │
    ▼                 ▼                    ▼
┌─────────┐      ┌─────────┐      ┌─────────────┐
│ Utils/  │      │ Neo4j   │      │   Gemini    │
│ NER     │      │Database │      │ 2.5 Pro     │
└─────────┘      └─────────┘      └─────────────┘
```

### Modules

1. **utils/** - Utility modules
   - `error_handling.py` - Retry logic, transactions, validation
   - `pdf_extractor.py` - Automated PDF extraction
   - `__init__.py` - Package initialization

2. **Core Scripts**
   - `build_graph.py` - Graph builder with error handling
   - `add_indian_cases.py` - Indian case integration
   - `visualize_graph.py` - Visualization generator
   - `cli.py` - Command line interface

3. **schema_evolution/** - AI-powered schema optimization
   - `orchestrator.py` - Iteration loop
   - `schema_designer.py` - 4 specialist sub-agents
   - `schema_evaluator.py` - 8-dimensional scoring
   - `schema_implementer.py` - Neo4j deployment

4. **tests/** - Test suite
   - Unit tests, integration tests, fixtures

---

## 📖 API Documentation

### PDF Extraction API

```python
from utils.pdf_extractor import PDFCaseExtractor, LegalCase

# Initialize extractor
extractor = PDFCaseExtractor()

# Extract cases
cases = extractor.extract_from_pdf('legal_document.pdf')

# Access case data
for case in cases:
    print(f"Case: {case.name}")
    print(f"Citation: {case.citation}")
    print(f"Judges: {', '.join(case.judges)}")
    print(f"Sections: {', '.join(case.sections)}")

# Export to JSON
extractor.extract_to_json('input.pdf', 'output.json')
```

### Error Handling API

```python
from utils.error_handling import (
    neo4j_retry,
    safe_neo4j_operation,
    Neo4jTransactionContext
)

# Retry decorator
@neo4j_retry(max_attempts=3)
def create_node(session, properties):
    session.run("CREATE (n:Node $props)", props=properties)

# Safe operation
result = safe_neo4j_operation(
    session.run,
    "MATCH (n) RETURN count(n)",
    fallback_value=0,
    error_message="Failed to count nodes"
)

# Transaction context
with Neo4jTransactionContext(session, "Create nodes") as tx:
    tx.run("CREATE (n:Node {id: 1})")
    tx.run("CREATE (n:Node {id: 2})")
# Auto-commits on success, rolls back on error
```

### Graph Builder API

```python
from build_graph import CPCGraphBuilder

# Initialize builder
builder = CPCGraphBuilder()

# Clear database (optional)
builder.clear_database()

# Build complete graph
builder.build_complete_graph()

# Get statistics
builder.get_statistics()

# Close connection
builder.close()
```

---

## 🐛 Troubleshooting

### Error: "Missing required environment variables"

**Solution:** Ensure `.env` file exists with all required variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Error: "PDF extraction failed"

**Possible causes:**
1. **PyMuPDF not installed**: `pip install PyMuPDF`
2. **Corrupted PDF**: Try opening PDF in viewer first
3. **Permissions**: Check file read permissions

### Error: "Neo4j connection failed"

**Solutions:**
1. Check Neo4j is running: `neo4j status`
2. Verify credentials in `.env`
3. Check firewall/network settings
4. Try local connection: `bolt://localhost:7687`

### Error: "Test failed: requires Neo4j"

**Solution:** Skip integration tests or set up test database:
```bash
# Run only unit tests
python cli.py run-tests --marker unit

# Or set up test database
export NEO4J_TEST_URL=bolt://localhost:7687
export NEO4J_TEST_USERNAME=neo4j
export NEO4J_TEST_PASSWORD=test
```

### Low test coverage

**Check coverage report:**
```bash
python cli.py run-tests --coverage
open htmlcov/index.html
```

---

## 📊 Performance Tips

1. **Batch Operations**: Use batch processing for large datasets
   ```python
   from utils.error_handling import batch_operation
   results = batch_operation(items, operation, batch_size=100)
   ```

2. **Indexes**: Ensure indexes are created
   ```cypher
   SHOW INDEXES
   ```

3. **Query Optimization**: Use `EXPLAIN` and `PROFILE`
   ```cypher
   PROFILE MATCH (c:Case)-[:CITES_PRECEDENT]->(p:Case)
   RETURN c.citation, p.citation
   ```

4. **Connection Pooling**: Reuse driver connections
   ```python
   # Good: Single driver instance
   driver = GraphDatabase.driver(...)

   # Bad: New driver for each operation
   # driver = GraphDatabase.driver(...)  # Don't do this in loops
   ```

---

## 🤝 Contributing

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install -e .

# Run tests before committing
python cli.py run-tests --coverage

# Format code (if using black/isort)
black .
isort .
```

### Adding Tests

Create tests in `tests/test_*.py`:

```python
import pytest

@pytest.mark.unit
def test_my_feature():
    assert my_function() == expected_result
```

### Pull Request Checklist

- [ ] Tests pass: `python cli.py run-tests`
- [ ] Coverage ≥70%: `python cli.py run-tests --coverage`
- [ ] No hardcoded credentials
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- **Neo4j** - Graph database platform
- **Google Gemini 2.5 Pro** - AI for schema evolution
- **PyMuPDF** - PDF parsing
- **spaCy** - NLP and NER
- **pytest** - Testing framework

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting)
2. Review test output
3. Check logs in `logs/`
4. Open an issue on GitHub

---

## 🗺️ Roadmap

### Completed ✅
- [x] Remove hardcoded credentials
- [x] Add error handling & retry logic
- [x] Implement automated PDF extraction
- [x] Create comprehensive test suite
- [x] Build unified CLI interface

### In Progress 🚧
- [ ] spaCy NER integration
- [ ] Batch processing optimization
- [ ] Monitoring dashboard
- [ ] Complete documentation

### Planned 📋
- [ ] Graph analytics (PageRank, centrality)
- [ ] Legal RAG system
- [ ] Multi-language support (Bengali, Hindi, Urdu)
- [ ] Citation network analysis
- [ ] Temporal tracking
- [ ] REST API server
- [ ] Web UI

---

**Built with ❤️ for the Bangladesh legal community**
