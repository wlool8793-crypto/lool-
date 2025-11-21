# Multi-Agent Schema Evolution System

An autonomous multi-agent system that iteratively designs, evaluates, and improves Neo4j graph schemas for legal knowledge graphs until achieving production-ready quality (9.0+/10.0 score).

## Overview

This system uses **3 AI agents** powered by Google Gemini 2.5 Pro to collaboratively evolve a legal knowledge graph schema:

1. **Schema Designer** - Coordinates 4 specialist sub-agents to create/improve schema
   - Legal Domain Specialist (entities & relationships)
   - RAG Architecture Specialist (embeddings & retrieval)
   - Performance Specialist (indexes & optimization)
   - Data Quality Specialist (provenance, versioning, trust)

2. **Schema Evaluator** - Scores schema across 8 dimensions
   - Legal Completeness (20%)
   - RAG Effectiveness (25%)
   - Performance (15%)
   - Data Quality (15%)
   - Cross-Jurisdictional Support (10%)
   - User Experience (5%)
   - Scalability (5%)
   - Extensibility (5%)

3. **Schema Implementer** - Deploys schema to Neo4j
   - Creates indexes (composite, vector, full-text, single)
   - Creates constraints (uniqueness, existence)
   - Validates implementation

## Features

- **Autonomous Iteration**: Runs up to 7 iterations, improving schema based on evaluation feedback
- **Production-Ready Criteria**: Stops when overall score ≥9.0 AND all 8 dimensions ≥8.0
- **Comprehensive Evaluation**: 8-dimensional rubric ensures legal, technical, and performance quality
- **RAG-Optimized**: Multi-granularity embeddings (case/section/chunk level)
- **Bangladesh Legal System**: Designed for CPC, case law, cross-jurisdictional support
- **Export Results**: Generates JSON, Markdown documentation, and Neo4j schema

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  (Iteration Loop, Convergence Detection, State Management)  │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐      ┌─────────────┐
│ AGENT 1 │      │ AGENT 2 │      │   AGENT 3   │
│ Designer│─────▶│Evaluator│─────▶│Implementer  │
└─────────┘      └─────────┘      └─────────────┘
    │                 │                    │
    │                 │                    │
    ▼                 ▼                    ▼
┌─────────┐      ┌─────────┐      ┌─────────────┐
│ Legal   │      │8-Dim    │      │   Neo4j     │
│ RAG     │      │Scoring  │      │ Deployment  │
│ Perf    │      │Feedback │      │ Validation  │
│ Quality │      │         │      │             │
└─────────┘      └─────────┘      └─────────────┘
```

## Installation

1. **Clone repository**:
   ```bash
   cd /workspaces/lool-/neo4j/schema_evolution
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_agents.txt
   ```

3. **Set up environment variables**:
   ```bash
   nano .env
   # Add your Google API key
   ```

   Required variables:
   - `GOOGLE_API_KEY` - Get from https://ai.google.dev/ (see [GOOGLE_GEMINI_SETUP.md](GOOGLE_GEMINI_SETUP.md))
   - `GOOGLE_MODEL_NAME` - Optional, defaults to `gemini-2.5-pro`
   - `NEO4J_URL` - Your Neo4j instance URL (for --implement mode)
   - `NEO4J_USERNAME` - Neo4j username (for --implement mode)
   - `NEO4J_PASSWORD` - Neo4j password (for --implement mode)

## Usage

### Basic Usage

Run with default settings (target score: 9.0, max 7 iterations):

```bash
python main.py
```

### Custom Parameters

```bash
# Custom target score and iterations
python main.py --target 9.5 --iterations 10

# Auto-implement in Neo4j after convergence
python main.py --implement

# Custom output directory
python main.py --output ./my_schema

# Combine options
python main.py --target 9.2 --iterations 5 --implement --output ./production_schema
```

### Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--target` | 9.0 | Target overall score for convergence |
| `--iterations` | 7 | Maximum number of iterations |
| `--implement` | False | Auto-implement schema in Neo4j |
| `--output` | `./schema_output` | Output directory for results |

## Output Files

The system generates the following files in the output directory:

```
schema_output/
├── final_schema.json          # Complete schema definition (JSON)
├── evaluation_results.json    # Detailed evaluation scores (JSON)
├── iteration_history.json     # History of all iterations (JSON)
├── schema_documentation.md    # Human-readable schema docs (Markdown)
└── evolution_summary.md       # Evolution summary report (Markdown)
```

## Example Output

```
================================================================================
🚀 SCHEMA EVOLUTION SYSTEM STARTING
================================================================================
Target Score: 9.0/10.0
Max Iterations: 7
Auto-Implement: False
================================================================================

################################################################################
# ITERATION 1/7
################################################################################

============================================================
Schema Designer - Iteration 1
============================================================

📚 Legal Domain Specialist working...
   ✓ Designed 15 node types, 18 relationship types
🔍 RAG Architecture Specialist working...
   ✓ Added 1 RAG nodes, 3 vector indexes
⚡ Performance Specialist working...
   ✓ Created 10 indexes
✨ Data Quality Specialist working...
   ✓ Added 15 quality properties, 5 constraints

✅ Schema Design Complete
   Total Nodes: 16
   Total Relationships: 21
   Total Indexes: 13
   Total Constraints: 5

============================================================
Schema Evaluator - Version v1.0
============================================================

📊 Evaluating Legal Completeness...
🔍 Evaluating RAG Effectiveness...
⚡ Evaluating Performance...
✨ Evaluating Data Quality...
🌏 Evaluating Cross-Jurisdictional Support...
👤 Evaluating User Experience...
📈 Evaluating Scalability...
🔧 Evaluating Extensibility...

============================================================
EVALUATION RESULTS - v1.0
============================================================

🎯 Overall Score: 8.65/10.0
============================================================

legal_completeness.............. 9.2/10  (weight: 20%)
rag_effectiveness............... 8.5/10  (weight: 25%)
performance..................... 8.8/10  (weight: 15%)
data_quality.................... 8.2/10  (weight: 15%)
cross_jurisdictional............ 9.0/10  (weight: 10%)
user_experience................. 8.5/10  (weight: 5%)
scalability..................... 9.0/10  (weight: 5%)
extensibility................... 9.0/10  (weight: 5%)

============================================================
Production Ready: ❌ NO

Blockers:
  • Overall score 8.7 is below 9.0 threshold
  • data_quality score 8.2 is below 8.5 threshold
============================================================

[... iterations 2-6 ...]

################################################################################
# ITERATION 7/7
################################################################################

[... design and evaluation ...]

============================================================
🎉 CONVERGENCE ACHIEVED!
============================================================
✅ Overall Score: 9.25/10.0
✅ All dimensions >= 8.0
✅ Production-ready schema achieved in 7 iterations
============================================================

================================================================================
📊 FINAL SUMMARY
================================================================================

🎯 Final Score: 9.25/10.0
✅ Production Ready: True
🔄 Total Iterations: 7
⏱️  Total Duration: 245.3s

📈 Dimension Scores:
  ✅ legal_completeness................... 9.5/10
  ✅ rag_effectiveness.................... 9.8/10
  ✅ performance.......................... 9.2/10
  ✅ data_quality......................... 8.9/10
  ✅ cross_jurisdictional................. 9.0/10
  ✅ user_experience...................... 8.5/10
  ✅ scalability.......................... 9.0/10
  ✅ extensibility........................ 9.0/10

💪 Strengths:
  ✓ rag_effectiveness: 9.8/10 - Excellent
  ✓ legal_completeness: 9.5/10 - Excellent
  ✓ All 3 vector indexes present
  ✓ Multi-granularity embeddings implemented
  ✓ Comprehensive indexing (13 indexes)

================================================================================
```

## Evaluation Rubric

### Legal Completeness (20%)

**Required Entities**:
- Core: Case, Statute, Section, Judge, Court, Party
- Advanced: Principle, Doctrine, Holding, Appeal, Motion
- Structural: Part, Order, Definition, Rule
- Temporal: CaseVersion, Amendment, ChangeLog

**Required Relationships**:
- Citation: CITES_PRECEDENT, OVERRULES, AFFIRMS, DISTINGUISHES
- Structural: PART_OF, BELONGS_TO, APPLIES_SECTION, HAS_PART
- Procedural: DECIDED_BY, BEFORE_COURT, PETITIONER, RESPONDENT
- Temporal: AMENDS, SUPERSEDES, VERSION_OF

### RAG Effectiveness (25%)

**Requirements**:
- Multi-granularity embeddings (case, section, chunk level)
- Vector indexes (1536 dimensions, text-embedding-3-large)
- Retrieval relationships (CHUNK_OF, REFERENCES, CITES_IN_CHUNK)
- Metadata properties (relevance_score, rerank_score, context)

### Performance (15%)

**Performance Targets**:
- Simple lookups: <100ms
- Section cases: <200ms
- Precedent chains: <500ms
- Vector search: <200ms
- Complex joins: <500ms
- Chunk retrieval: <150ms

**Index Requirements**:
- Composite indexes on common query patterns
- Vector indexes for embeddings
- Full-text indexes for search
- Single-property indexes for lookups

### Data Quality (15%)

**Requirements**:
- Provenance tracking (source, extracted_at, confidence_score)
- Versioning (version, created_at, updated_at, changelog)
- Trust scoring (trust_score, authority_level, citation_count)
- Constraints (uniqueness, referential integrity)

### Other Dimensions

- **Cross-Jurisdictional** (10%): Support for India, Pakistan, Bangladesh
- **User Experience** (5%): Clear naming, good documentation
- **Scalability** (5%): Indexing strategy, partitioning hints
- **Extensibility** (5%): Versioning support, flexible properties

## Production Readiness Criteria

Schema is considered production-ready when:
- **Overall Score ≥ 9.0**
- **All 8 dimensions ≥ 8.0**

If not achieved within max iterations, system returns best schema with recommendations.

## File Structure

```
schema_evolution/
├── __init__.py                  # Package initialization
├── state.py                     # State definitions (TypedDict)
├── evaluation_rubric.py         # Scoring criteria and rubric
├── schema_designer.py           # Agent 1: Designer (4 sub-agents)
├── schema_evaluator.py          # Agent 2: Evaluator (8-dim scoring)
├── schema_implementer.py        # Agent 3: Implementer (Neo4j)
├── orchestrator.py              # Orchestrator (iteration loop)
├── main.py                      # Main entry point
├── requirements_agents.txt      # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Dependencies

- **LangGraph** (≥0.0.30): Multi-agent coordination
- **LangChain** (≥0.1.0): LLM framework
- **LangChain Google GenAI** (≥2.1.0): Google Gemini 2.5 Pro integration
- **Neo4j Driver** (≥5.14.0): Neo4j database client
- **Python-dotenv** (≥1.0.0): Environment variables
- **Pydantic** (≥2.5.0): Data validation

See `requirements_agents.txt` for complete list.

## Troubleshooting

### "Missing GOOGLE_API_KEY"

Make sure you've set `GOOGLE_API_KEY` in `.env` file or environment. See [GOOGLE_GEMINI_SETUP.md](GOOGLE_GEMINI_SETUP.md) for detailed setup instructions.

### "Neo4j credentials not provided"

For `--implement` mode, set `NEO4J_URL`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` in `.env`.

### "Index creation failed"

Some Neo4j instances (especially Aura Free) may not support all index types. The system will continue with supported indexes.

### "Max iterations reached without convergence"

Try:
- Increase `--iterations` (e.g., `--iterations 10`)
- Lower `--target` slightly (e.g., `--target 8.8`)
- Review evaluation feedback in iteration history

## Advanced Usage

### Running Specific Agents

```python
from schema_designer import SchemaDesigner
from schema_evaluator import SchemaEvaluator

designer = SchemaDesigner()
schema = designer.design_schema(iteration=1)

evaluator = SchemaEvaluator()
evaluation = evaluator.evaluate(schema)

print(f"Score: {evaluation['overall_score']:.2f}/10.0")
```

### Custom Evaluation

```python
from orchestrator import SchemaEvolutionOrchestrator

orchestrator = SchemaEvolutionOrchestrator(
    target_score=9.5,
    max_iterations=10,
    auto_implement=False
)

results = orchestrator.run_evolution()
orchestrator.export_results(output_dir="./custom_output")
```

## Contributing

This system is designed for Bangladesh legal data but can be adapted for other legal systems or domains by modifying:

1. **evaluation_rubric.py**: Update `REQUIRED_LEGAL_ENTITIES`, `REQUIRED_RELATIONSHIPS` for your domain
2. **schema_designer.py**: Adjust specialist prompts for your domain knowledge
3. **DIMENSION_WEIGHTS**: Adjust weights based on your priorities

## License

MIT

## Citation

If you use this system in research, please cite:

```
Multi-Agent Schema Evolution System for Legal Knowledge Graphs
Built for Bangladesh Code of Civil Procedure (CPC) and Case Law
November 2025
```

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review iteration history and evaluation feedback
3. Examine exported schema documentation
4. Adjust parameters (--target, --iterations) as needed
