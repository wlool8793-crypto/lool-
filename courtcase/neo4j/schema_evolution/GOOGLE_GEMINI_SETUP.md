# Google Gemini API Setup Guide

Complete guide for setting up the Schema Evolution System with Google's Gemini API.

---

## Quick Start (5 Minutes)

```bash
# 1. Install dependencies
pip install langchain-google-genai>=2.1.0

# 2. Set your API key
export GOOGLE_API_KEY="your_api_key_here"

# 3. Run the system
cd /workspaces/lool-/neo4j/schema_evolution
python main.py --iterations 2
```

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Your API Key](#getting-your-api-key)
3. [Environment Setup](#environment-setup)
4. [Available Models](#available-models)
5. [Configuration Options](#configuration-options)
6. [Testing Your Setup](#testing-your-setup)
7. [Cost Estimation](#cost-estimation)
8. [Troubleshooting](#troubleshooting)
9. [Comparison: Gemini vs Azure OpenAI vs Claude](#comparison)

---

## Overview

The system has been migrated from Azure OpenAI to **Google Gemini API** using the `langchain-google-genai` package.

### Why Gemini 2.5 Pro?

- **1 Million Token Context** - Massive context window for complex schemas
- **Advanced Reasoning** - Excellent for multi-step schema design
- **Latest Technology** - Gemini 2.5 is cutting-edge (2025)
- **Simple Setup** - Just an API key, no complex cloud configuration
- **Cost-Effective** - Competitive pricing with good performance

---

## Getting Your API Key

### Option 1: Google AI Studio (Recommended - Simplest)

1. **Visit Google AI Studio**:
   - Go to: https://ai.google.dev/
   - Or: https://aistudio.google.com/

2. **Sign In**:
   - Use your Google account
   - Accept terms of service

3. **Get API Key**:
   - Click "Get API Key" button
   - Click "Create API Key"
   - Copy your API key (starts with `AI...`)

4. **Add to .env**:
   ```bash
   GOOGLE_API_KEY=AIza...your_key_here
   ```

### Option 2: Vertex AI (More Complex - If You Have Google Cloud)

If you already have Vertex AI credentials:

1. **Get Service Account JSON**:
   - Go to: https://console.cloud.google.com/
   - Navigate to: IAM & Admin → Service Accounts
   - Find your service account
   - Click Actions (⋮) → Manage Keys → Add Key → Create New Key → JSON
   - Download the JSON file

2. **Set Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1
   ```

**Note**: The current system is configured for Gemini API (simpler). To use full Vertex AI, you'd need to modify `schema_designer.py` to use `ChatVertexAI` instead of `ChatGoogleGenerativeAI`.

---

## Environment Setup

### Create .env File

Create or edit `/workspaces/lool-/neo4j/schema_evolution/.env`:

```bash
# Google Gemini API Configuration
GOOGLE_API_KEY=your_api_key_here
GOOGLE_MODEL_NAME=gemini-2.5-pro

# Neo4j Configuration (Required for --implement mode)
NEO4J_URL=neo4j+s://d0d1fe15.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
```

### Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | **YES** | - | Your Google Gemini API key |
| `GOOGLE_MODEL_NAME` | No | `gemini-2.5-pro` | Model to use |
| `NEO4J_URL` | For `--implement` | - | Neo4j connection URL |
| `NEO4J_USERNAME` | For `--implement` | - | Neo4j username |
| `NEO4J_PASSWORD` | For `--implement` | - | Neo4j password |

---

## Available Models

### Recommended Models (2025)

#### 1. **gemini-2.5-pro** - BEST FOR SCHEMA DESIGN ⭐

**Best choice for this system**

```bash
GOOGLE_MODEL_NAME=gemini-2.5-pro
```

**Strengths:**
- 🧠 Advanced reasoning and problem-solving
- 📚 1 million token context window
- 🎯 Excellent for complex multi-step tasks
- 💻 Strong code generation
- ⚡ Good balance of quality and speed

**Use When:**
- You need the best schema quality
- Complex legal domain modeling
- Multi-agent coordination tasks

**Pricing**: ~$3.50 per 1M input tokens, ~$10.50 per 1M output tokens

---

#### 2. **gemini-2.5-flash** - FAST ALTERNATIVE ⚡

**For faster iterations**

```bash
GOOGLE_MODEL_NAME=gemini-2.5-flash
```

**Strengths:**
- ⚡ Lower latency
- 💰 More cost-effective
- 🎯 Efficient reasoning with dynamic budget
- 📊 Good for high-volume tasks

**Use When:**
- You want faster iteration times
- Running many experiments
- Cost is a primary concern

**Pricing**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens (40x cheaper!)

---

#### 3. **gemini-2.0-pro** - SOLID BASELINE

**Reliable option**

```bash
GOOGLE_MODEL_NAME=gemini-2.0-pro
```

**Strengths:**
- 🔧 Strong coding performance
- 📖 Better world knowledge
- ⚖️ Good balance of capabilities

**Use When:**
- Gemini 2.5 models have issues
- Need stable, proven performance

---

### Model Comparison Table

| Feature | gemini-2.5-pro | gemini-2.5-flash | gemini-2.0-pro |
|---------|----------------|------------------|----------------|
| Context Window | 1M tokens | 1M tokens | 1M tokens |
| Reasoning | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cost | $$$$ | $ | $$$ |
| Best For | Complex schemas | Fast iterations | Balanced use |
| **Recommended** | ✅ Yes | ⚡ For speed | 🔧 Fallback |

---

## Configuration Options

### Basic Configuration

```bash
# Minimal setup
GOOGLE_API_KEY=your_key
```

### Advanced Configuration

```bash
# Full configuration with all options
GOOGLE_API_KEY=your_key
GOOGLE_MODEL_NAME=gemini-2.5-pro

# Optional: Timeout settings (seconds)
GOOGLE_API_TIMEOUT=120

# Optional: Retry settings
GOOGLE_API_MAX_RETRIES=3

# Neo4j for deployment
NEO4J_URL=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

---

## Testing Your Setup

### Step 1: Verify API Key

```bash
# Test authentication
python -c "
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
print(f'API Key found: {api_key[:10]}...' if api_key else 'No API key found')

try:
    llm = ChatGoogleGenerativeAI(google_api_key=api_key, model='gemini-2.5-pro')
    response = llm.invoke('Say hello!')
    print(f'✅ Connection successful: {response.content}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Step 2: Quick Test Run (1 Iteration)

```bash
cd /workspaces/lool-/neo4j/schema_evolution
python main.py --iterations 1 --output ./test_run
```

**Expected Output:**
```
================================================================================
🧠 LEGAL KNOWLEDGE GRAPH SCHEMA EVOLUTION SYSTEM
================================================================================
Target Score: 9.0/10.0
Max Iterations: 1
...
✅ SCHEMA EVOLUTION COMPLETE
```

### Step 3: Full Test Run (5 Iterations)

```bash
python main.py --iterations 5 --target 9.0 --output ./gemini_schema
```

### Step 4: Test with Neo4j (Optional)

```bash
python main.py --iterations 3 --implement
```

---

## Cost Estimation

### Cost Calculator

For the schema evolution system with 5 iterations:

#### Estimated Token Usage per Iteration:
- **Input**: ~50,000 tokens (prompts + context)
- **Output**: ~10,000 tokens (schema JSON)
- **Total per iteration**: 60,000 tokens

#### Cost for 5 Iterations:

**gemini-2.5-pro:**
- Input: 250K tokens × $3.50/1M = **$0.875**
- Output: 50K tokens × $10.50/1M = **$0.525**
- **Total**: **~$1.40** for full run

**gemini-2.5-flash:**
- Input: 250K tokens × $0.075/1M = **$0.019**
- Output: 50K tokens × $0.30/1M = **$0.015**
- **Total**: **~$0.034** for full run **(40x cheaper!)**

### Comparison with Other Services

| Provider | Model | Cost per 5 Iterations |
|----------|-------|----------------------|
| **Google Gemini** | gemini-2.5-pro | **$1.40** |
| **Google Gemini** | gemini-2.5-flash | **$0.03** ⭐ |
| Azure OpenAI | gpt-4 | ~$3.00 |
| Anthropic | claude-3.5-sonnet | ~$7.50 |

**Winner**: Gemini 2.5 Flash is **40-100x cheaper** than competitors!

---

## Troubleshooting

### Error: "Missing GOOGLE_API_KEY"

**Cause**: Environment variable not set

**Solution**:
```bash
# Check if .env exists
cat /workspaces/lool-/neo4j/schema_evolution/.env

# Verify key is set
echo $GOOGLE_API_KEY

# Set manually if needed
export GOOGLE_API_KEY="your_key_here"
```

---

### Error: "API key not valid"

**Cause**: Invalid or expired API key

**Solutions**:
1. **Regenerate API key**:
   - Visit https://aistudio.google.com/
   - Delete old key
   - Create new key
   - Update `.env`

2. **Check key format**:
   - Should start with `AIza...` (for Gemini API)
   - Should NOT have spaces or line breaks

3. **Try different key type**:
   - If using Vertex AI key, you may need service account JSON

---

### Error: "Rate limit exceeded"

**Cause**: Too many requests to API

**Solutions**:
1. **Wait and retry**:
   ```bash
   # System has built-in retry logic (max_retries=2)
   # Just wait a minute and try again
   ```

2. **Reduce iterations**:
   ```bash
   python main.py --iterations 2  # Start smaller
   ```

3. **Use slower model**:
   ```bash
   # gemini-2.5-flash has higher rate limits
   GOOGLE_MODEL_NAME=gemini-2.5-flash
   ```

---

### Error: "Model not found"

**Cause**: Model name incorrect or not available

**Solution**:
```bash
# Use one of these exact names:
GOOGLE_MODEL_NAME=gemini-2.5-pro      # Latest, best
GOOGLE_MODEL_NAME=gemini-2.5-flash    # Fast
GOOGLE_MODEL_NAME=gemini-2.0-pro      # Stable
GOOGLE_MODEL_NAME=gemini-pro          # Legacy (not recommended)
```

---

### Error: JSON Parsing Failed

**Cause**: Model output format changed

**Solutions**:
1. **Try different model**:
   ```bash
   # gemini-2.5-pro is most reliable
   GOOGLE_MODEL_NAME=gemini-2.5-pro
   ```

2. **Check iteration output**:
   ```bash
   # Look at schema_output/iteration_history.json
   cat schema_output/iteration_history.json
   ```

3. **Adjust temperature** (if needed):
   - Edit `schema_designer.py`
   - Change `temperature=0.7` to `temperature=0.3` (more deterministic)

---

### Connection Timeout

**Cause**: API request taking too long

**Solution**:
```bash
# Increase timeout (default is 120s)
export GOOGLE_API_TIMEOUT=300  # 5 minutes
```

---

## Comparison

### Google Gemini API vs Azure OpenAI vs Anthropic Claude

| Feature | Google Gemini 2.5 Pro | Azure OpenAI GPT-4 | Anthropic Claude 3.5 |
|---------|----------------------|-------------------|---------------------|
| **Context Window** | 1M tokens ⭐ | 128K tokens | 200K tokens |
| **Reasoning Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup Complexity** | Simple ⭐ | Complex | Simple |
| **Authentication** | API key only | Endpoint + Key + Deployment | API key only |
| **Cost (5 iterations)** | $1.40 ⭐ | ~$3.00 | ~$7.50 |
| **Speed** | Fast | Medium | Fast |
| **Code Generation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **JSON Reliability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Latest Features** | 2025 ⭐ | 2024 | 2025 |

### When to Use Each

**Use Gemini 2.5 Pro when:**
- ✅ You want simplest setup (just API key)
- ✅ You need largest context window (1M tokens)
- ✅ Cost is a concern ($1.40 vs $3-7)
- ✅ You want latest technology (2025)

**Use Azure OpenAI when:**
- Enterprise requirements
- Need Azure integration
- Have existing Azure setup

**Use Anthropic Claude when:**
- Best reasoning quality needed
- Have existing Anthropic relationship
- Budget allows higher cost

---

## Best Practices

### 1. Start with Quick Test

```bash
# Always test with 1-2 iterations first
python main.py --iterations 1 --output ./test
```

### 2. Use gemini-2.5-flash for Experiments

```bash
# Cheaper for testing
GOOGLE_MODEL_NAME=gemini-2.5-flash python main.py --iterations 3
```

### 3. Use gemini-2.5-pro for Production

```bash
# Best quality for final schemas
GOOGLE_MODEL_NAME=gemini-2.5-pro python main.py --iterations 5
```

### 4. Monitor API Usage

- Check https://aistudio.google.com/ for quota usage
- Set up billing alerts in Google Cloud Console
- Track token usage in iteration logs

### 5. Cache Results

```bash
# Export schemas for reuse
python main.py --iterations 5 --output ./schemas/v1
# Reuse schemas to avoid re-running
```

---

## Next Steps

1. ✅ **Verify Setup**: Run quick test (1 iteration)
2. ✅ **Full Run**: Execute full evolution (5 iterations)
3. ✅ **Deploy**: Use `--implement` to deploy to Neo4j
4. ✅ **Validate**: Check schema quality and scores
5. ✅ **Optimize**: Adjust model/iterations based on results

---

## Support

### Resources

- **Google AI Documentation**: https://ai.google.dev/docs
- **LangChain Google Integration**: https://python.langchain.com/docs/integrations/platforms/google
- **Gemini API Reference**: https://ai.google.dev/api
- **This Project README**: `README.md`

### Common Issues

- Check `TROUBLESHOOTING` section above
- Review `iteration_history.json` for errors
- Verify API key at https://aistudio.google.com/

### Getting Help

1. Check iteration logs in `schema_output/`
2. Test API connection with verification script
3. Try with gemini-2.5-pro (most reliable)
4. Check Google AI Studio for API status

---

## Changelog

### 2025-11-10 - Initial Google Gemini Migration

- ✅ Migrated from Azure OpenAI to Google Gemini API
- ✅ Using `langchain-google-genai` package
- ✅ Default model: `gemini-2.5-pro`
- ✅ Simplified authentication (API key only)
- ✅ Updated all documentation

---

**Happy Schema Designing with Google Gemini! 🚀**
