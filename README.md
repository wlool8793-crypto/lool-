# LawBrain - Comprehensive Legal AI System

A complete legal AI ecosystem combining AI-powered legal assistance, legal data collection, knowledge graph technology, and hybrid RAG (Retrieval-Augmented Generation) for legal document processing.

## Overview

LawBrain is a multi-component legal AI system designed to provide comprehensive legal services through:

1. **AI Law Firm** - Multi-agent AI system with specialized legal practitioners
2. **Legal Data Collection** - Web scraping systems for Indian and Bangladesh legal databases
3. **Knowledge Graph** - Graph-based legal knowledge representation with Neo4j
4. **Hybrid RAG** - Advanced retrieval system for legal document processing
5. **Court Case Management** - Web application for managing legal cases

## System Architecture

```
lawbrain/
├── lawbrain/                    # AI Law Firm (LangGraph-based)
├── data-collection/             # Legal data scraping systems
├── legal-knowledge-graph/       # Neo4j-based knowledge graph
├── hybrid-rag-for-legal/        # RAG implementation
├── courtcase/                   # Court case management app
└── neo4j/                      # Neo4j database configuration
```

---

## Components

### 1. AI Law Firm (`/lawbrain`)

Full-service AI law firm powered by **Google Gemini 2.5 Pro** with specialized legal practitioners.

**Features:**
- Senior Partner supervisor coordinating 9 specialized lawyers
- Practice areas: Criminal, Civil Litigation, Corporate, IP, Family, Real Estate, Employment, Estate Planning, Immigration
- Multi-practice coordination for complex legal matters
- Built with LangGraph and Google Vertex AI

**Quick Start:**
```bash
cd lawbrain
pip install -r requirements.txt
langgpraph dev
```

**Documentation:** See [lawbrain/README.md](lawbrain/README.md)

---

### 2. Legal Data Collection (`/data-collection`)

Comprehensive web scraping systems for collecting legal case data from multiple jurisdictions.

**Supported Sources:**
- **IndianKanoon.org** - India's premier legal search engine
- **Bangladesh Legal Database** - BD Laws and BDLex
- Multi-level scraping: search results, case details, PDF downloads

**Features:**
- SQLite/PostgreSQL database storage
- Rate limiting and robust error handling
- PDF document management
- Progress tracking and statistics
- Concurrent download support

**Quick Start:**
```bash
cd data-collection
pip install -r requirements.txt
python main.py --query "criminal law" --doc-type supremecourt --max-pages 5
```

**Documentation:** See [data-collection/README.md](data-collection/README.md)

---

### 3. Legal Knowledge Graph (`/legal-knowledge-graph`)

Graph-based legal knowledge representation using Neo4j for relationship mapping and advanced queries.

**Features:**
- Neo4j graph database integration
- Legal entity relationship mapping
- Case law citation networks
- Advanced graph queries for legal research
- Visual relationship exploration

**Quick Start:**
```bash
cd legal-knowledge-graph
# Configure Neo4j connection
python setup_graph.py
```

---

### 4. Hybrid RAG for Legal (`/hybrid-rag-for-legal`)

Advanced Retrieval-Augmented Generation system specifically designed for legal document processing.

**Features:**
- Hybrid search combining vector and keyword search
- Legal document-specific embeddings
- Context-aware retrieval
- Citation extraction and linking
- Multi-document reasoning

**Quick Start:**
```bash
cd hybrid-rag-for-legal
pip install -r requirements.txt
python main.py
```

---

### 5. Court Case Management (`/courtcase`)

React-based web application for managing court cases and legal workflows.

**Features:**
- Case tracking and management
- Document organization
- Client communication
- Deadline tracking
- Matter management

**Quick Start:**
```bash
cd courtcase/court-case-app
npm install
npm run dev
```

---

## Data Sources

### Indian Legal Database
- **Source:** IndianKanoon.org
- **Coverage:** Supreme Court, High Courts, Tribunals, District Courts
- **Format:** HTML + PDF downloads
- **Status:** Active collection

### Bangladesh Legal Database
- **Sources:**
  - BD Laws (bdlaws.minlaw.gov.bd)
  - BDLex (www.bdlex.com)
- **Coverage:** Central Acts, Ordinances, Regulations
- **Format:** PDF documents
- **Location:** `data-collection/Legal_Database/BD/`

---

## Technology Stack

### AI & Machine Learning
- **LangGraph** - Agent orchestration and workflows
- **Google Gemini 2.5 Pro** - Language model
- **LangChain** - LLM application framework

- **RAG** - Retrieval-Augmented Generation

### Databases
- **Neo4j** - Graph database for knowledge representation
- **SQLite/PostgreSQL** - Relational data storage
- **Vector Database** - Embeddings storage for RAG

### Web Technologies
- **React** - Frontend framework
- **Vite** - Build tool
- **BeautifulSoup** - Web scraping
- **Selenium** - JavaScript-heavy page scraping

### DevOps & Infrastructure
- **Docker** - Containerization
- **Python 3.9+** - Primary language
- **Node.js** - Frontend runtime

---

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Neo4j 5.x
- Google Cloud Project with Vertex AI enabled

### Clone Repository
```bash
git clone https://github.com/wlool8793-crypto/lawbrain.git
cd lawbrain
```

### Setup Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Component Dependencies

**AI Law Firm:**
```bash
cd lawbrain
pip install -r requirements.txt
```

**Data Collection:**
```bash
cd data-collection
pip install -r requirements.txt
```

**Court Case App:**
```bash
cd courtcase/court-case-app
npm install
```

---

## Configuration

### Environment Variables

Each component requires its own `.env` file. See `.env.example` files in each directory.

**AI Law Firm (lawbrain/.env):**
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Data Collection (data-collection/.env):**
```bash
DATABASE_URL=sqlite:///data/indiankanoon.db
BASE_URL=https://indiankanoon.org
HEADLESS_MODE=true
REQUEST_DELAY=2
```

**Neo4j (legal-knowledge-graph/.env):**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

---

## Usage Examples

### Scrape Legal Data
```bash
cd data-collection
python main.py --query "constitutional law" --year 2023 --max-pages 10
```

### Run AI Law Firm
```bash
cd lawbrain
langgraph dev
# Visit http://localhost:8000
```

### Query Knowledge Graph
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
# Run Cypher queries
```

### Start Court Case App
```bash
cd courtcase/court-case-app
npm run dev
# Visit http://localhost:5173
```

---

## Project Structure Details

```
lawbrain/
├── lawbrain/                           # AI Law Firm
│   ├── agent.py                        # Main law firm agent
│   ├── langgraph.json                  # LangGraph configuration
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # Law firm documentation
│
├── data-collection/                    # Legal Data Collection
│   ├── src/                           # Source code
│   │   ├── scraper.py                 # Web scraping logic
│   │   └── database.py                # Database operations
│   ├── data/                          # Collected data
│   │   ├── pdfs/                      # Downloaded PDFs
│   │   └── indiankanoon.db            # SQLite database
│   ├── Legal_Database/                # Bangladesh legal PDFs
│   │   └── BD/ACT/CENTRAL/           # Central Acts
│   ├── main.py                        # Main scraper application
│   └── README.md                      # Data collection docs
│
├── legal-knowledge-graph/             # Knowledge Graph
│   ├── data/                          # Graph data
│   ├── models/                        # Data models
│   └── queries/                       # Cypher queries
│
├── hybrid-rag-for-legal/              # RAG System
│   ├── embeddings/                    # Vector embeddings
│   ├── retrievers/                    # Retrieval modules
│   └── main.py                        # RAG application
│
├── courtcase/                         # Court Case Management
│   └── court-case-app/               # React application
│       ├── src/                       # Source code
│       ├── public/                    # Static assets
│       └── package.json               # Node dependencies
│
└── neo4j/                            # Neo4j Configuration
    ├── data/                          # Database files
    └── conf/                          # Configuration
```

---

## Data Statistics

### Indian Legal Database
- **Total Cases Collected:** Varies by scraping configuration
- **Courts Covered:** Supreme Court, High Courts, Tribunals, District Courts
- **Date Range:** Configurable (default: 2020-2024)
- **PDF Downloads:** Automated for available cases

### Bangladesh Legal Database
- **Total Acts:** 200+ Central Acts
- **Format:** PDF documents
- **Languages:** English and Bengali
- **Date Range:** 1818 - Present

---

## Development

### Contributing
Contributions are welcome! Areas for improvement:
- Additional court/jurisdiction support
- Enhanced AI legal reasoning
- Advanced graph queries
- API development
- Frontend enhancements

### Testing
```bash
# Test data collection
cd data-collection
python -m pytest tests/

# Test AI law firm
cd lawbrain
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 src/

# Type checking
mypy src/
```

---

## Legal & Ethical Considerations

- **Data Usage:** For research, education, and legal analysis only
- **Attribution:** Cite data sources (IndianKanoon.org, BD Laws)
- **Rate Limiting:** Respect server resources with appropriate delays
- **Privacy:** Handle sensitive legal data responsibly
- **Copyright:** Comply with copyright laws and terms of service
- **AI Ethics:** Use AI assistance responsibly; human oversight required

---

## Troubleshooting

### AI Law Firm Issues
**"Could not determine credentials"**
- Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env`
- Or run: `gcloud auth application-default login`

**"Permission Denied"**
- Verify service account has "Vertex AI User" role
- Enable Vertex AI API in Google Cloud Console

### Data Collection Issues
**Selenium driver errors:**
```bash
pip install --upgrade selenium webdriver-manager
```

**Database locked:**
- Use PostgreSQL for concurrent access
- Close other database connections

### Neo4j Issues
**Connection refused:**
- Ensure Neo4j is running: `neo4j start`
- Check URI and credentials in `.env`

---

## Performance Optimization

### Data Collection
- Use `--max-pages` to limit scraping
- Adjust `REQUEST_DELAY` for rate limiting
- Use PostgreSQL for large datasets
- Enable concurrent downloads for PDFs

### AI Law Firm
- Use streaming for long responses
- Implement caching for common queries
- Optimize prompts for efficiency

### Knowledge Graph
- Index frequently queried properties
- Optimize Cypher queries
- Use graph projections for analytics

---

## Roadmap

### Short Term
- [ ] API endpoints for all components
- [ ] Enhanced search capabilities
- [ ] Real-time case law updates
- [ ] Advanced analytics dashboard

### Medium Term
- [ ] Multi-language support
- [ ] Additional jurisdictions
- [ ] Mobile applications
- [ ] Cloud deployment guides

### Long Term
- [ ] Automated legal research
- [ ] Predictive case outcomes
- [ ] Contract analysis
- [ ] Compliance monitoring

---

## Resources

### Documentation
- [AI Law Firm](lawbrain/README.md)
- [Data Collection](data-collection/README.md)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Neo4j Docs](https://neo4j.com/docs/)

### Data Sources
- [IndianKanoon](https://indiankanoon.org/)
- [Bangladesh Laws](http://bdlaws.minlaw.gov.bd/)
- [BDLex](http://www.bdlex.com/)

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Share ideas and ask questions

---

## License

MIT License - See LICENSE file for details

---

## Disclaimer

This system is for educational and research purposes. Users must:
- Comply with all applicable laws and regulations
- Obtain appropriate legal advice from licensed attorneys
- Respect data source terms of service
- Use AI assistance responsibly with human oversight

**LawBrain AI does not replace professional legal counsel.**

---

## Contact & Support

For questions, issues, or contributions:
1. Check component-specific documentation
2. Review logs and error messages
3. Search existing GitHub issues
4. Create a new issue with detailed information

---

**LawBrain** - Comprehensive Legal AI System
*Powered by Google Gemini 2.5 Pro, LangGraph, and Neo4j*
