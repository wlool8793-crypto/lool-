# Quick Start Guide

Get the Schema Evolution System running in 5 minutes.

## Prerequisites

- Python 3.8+
- Anthropic API key (Claude 3.5 Sonnet access)
- Optional: Neo4j instance for `--implement` mode

## Installation Steps

### 1. Navigate to directory

```bash
cd /workspaces/lool-/neo4j/schema_evolution
```

### 2. Install dependencies

```bash
pip install -r requirements_agents.txt
```

Expected output:
```
Successfully installed langgraph-0.0.30 langchain-0.1.0 langchain-anthropic-0.1.0 neo4j-5.14.0 ...
```

### 3. Configure API keys

Edit the `.env` file and add your Anthropic API key:

```bash
# Open .env file
nano .env
```

Replace `your_anthropic_api_key_here` with your actual API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Save and exit (Ctrl+X, Y, Enter)

### 4. Run the system

```bash
python main.py
```

That's it! The system will:
- Design initial legal schema (Iteration 1)
- Evaluate it across 8 dimensions
- Iteratively improve based on feedback
- Stop when production-ready (9.0+/10) or max iterations reached

## Command Options

### Basic run (default: 9.0 target, 7 iterations)
```bash
python main.py
```

### Custom target and iterations
```bash
python main.py --target 9.5 --iterations 10
```

### Auto-implement in Neo4j
```bash
python main.py --implement
```

### Custom output directory
```bash
python main.py --output ./my_schema
```

## What to Expect

### Console Output

```
================================================================================
🚀 SCHEMA EVOLUTION SYSTEM STARTING
================================================================================
Target Score: 9.0/10.0
Max Iterations: 7
================================================================================

################################################################################
# ITERATION 1/7
################################################################################

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

🎯 Overall Score: 8.45/10.0
============================================================

legal_completeness.............. 8.8/10  (weight: 20%)
rag_effectiveness............... 8.2/10  (weight: 25%)
performance..................... 8.5/10  (weight: 15%)
data_quality.................... 8.1/10  (weight: 15%)
cross_jurisdictional............ 8.0/10  (weight: 10%)
user_experience................. 8.5/10  (weight: 5%)
scalability..................... 9.0/10  (weight: 5%)
extensibility................... 9.0/10  (weight: 5%)

============================================================
Production Ready: ❌ NO

Blockers:
  • Overall score 8.45 is below 9.0 threshold
  • data_quality score 8.1 is below 8.5 threshold

Top Improvements for Next Iteration:
  1. [HIGH] Missing: Chunk entity for text chunking
     → Add Chunk entity to improve rag_effectiveness
  2. [HIGH] Missing: Trust scoring (only 8/16 nodes)
     → Add Trust scoring to improve data_quality
  3. [MEDIUM] Missing: Vector indexes (1/3)
     → Add Vector indexes to improve rag_effectiveness
============================================================

[... iterations continue ...]
```

### Output Files

After completion, check the `schema_output/` directory:

```bash
ls -lh schema_output/

# You should see:
# final_schema.json             - Complete schema in JSON
# evaluation_results.json       - Detailed scores
# iteration_history.json        - All iterations
# schema_documentation.md       - Human-readable docs
# evolution_summary.md          - Summary report
```

## Viewing Results

### Check overall score
```bash
cat schema_output/evolution_summary.md | grep "Overall Score"
```

### View final schema
```bash
cat schema_output/schema_documentation.md
```

### Check production readiness
```bash
cat schema_output/evolution_summary.md | grep "Production Ready"
```

## Troubleshooting

### "Missing ANTHROPIC_API_KEY"

**Problem**: API key not set in `.env` file

**Solution**:
```bash
# Edit .env file
nano .env

# Add your key:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key

# Save and run again
python main.py
```

### "Import Error: No module named 'langgraph'"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements_agents.txt
```

### "Max iterations reached without convergence"

**Problem**: Schema didn't reach 9.0+ in 7 iterations

**Solution**: This is normal! The system returns the best schema achieved. You can:

1. **Increase iterations**:
   ```bash
   python main.py --iterations 10
   ```

2. **Lower target slightly**:
   ```bash
   python main.py --target 8.8
   ```

3. **Review feedback**: Check `schema_output/evolution_summary.md` for improvement suggestions

### Rate Limits

If you hit Anthropic API rate limits:

1. **Wait 60 seconds** and try again
2. **Reduce iterations**: `python main.py --iterations 5`
3. **Check API quota** at https://console.anthropic.com/

## Next Steps

### 1. Review the Schema

```bash
cat schema_output/schema_documentation.md
```

### 2. Check Evaluation Details

```bash
cat schema_output/evaluation_results.json | python -m json.tool
```

### 3. Implement in Neo4j (if ready)

```bash
# Make sure Neo4j credentials are in .env
python main.py --implement
```

### 4. Customize for Your Domain

Edit these files to adapt for other legal systems:

- `evaluation_rubric.py` - Update required entities and relationships
- `schema_designer.py` - Adjust specialist prompts

## Validation

Run the test suite to verify installation:

```bash
python test_structure.py
```

Expected output:
```
============================================================
TEST SUMMARY
============================================================
✓ PASS   File Structure
✓ PASS   Imports
✓ PASS   State Creation
✓ PASS   Rubric Calculations
✓ PASS   Required Components
✓ PASS   Dimension Weights
============================================================
Passed: 6/6
============================================================

✅ All tests passed!
```

## Support

For issues:
1. Check this guide's Troubleshooting section
2. Run `python test_structure.py` to validate installation
3. Review `schema_output/evolution_summary.md` for hints
4. Check API key and quota at https://console.anthropic.com/

## Examples

### Quick test run (2 iterations)
```bash
python main.py --iterations 2 --output ./test_output
```

### Production run with high target
```bash
python main.py --target 9.5 --iterations 10 --output ./production
```

### Full run with Neo4j deployment
```bash
python main.py --target 9.2 --iterations 7 --implement --output ./deployed
```

---

**Time to first results**: ~2-5 minutes per iteration

**Total expected runtime**: 15-30 minutes for 7 iterations

**Cost estimate**: ~$0.50-2.00 per full run (depends on API pricing)
