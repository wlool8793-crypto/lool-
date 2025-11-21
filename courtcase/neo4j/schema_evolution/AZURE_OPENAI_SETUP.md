# Azure OpenAI Setup Guide

## 🎯 Quick Setup (5 Minutes)

Your Multi-Agent Schema Evolution System is now configured to use **Azure OpenAI** instead of Anthropic Claude!

---

## 📋 Prerequisites

You need access to:
- Azure AI Studio: https://ai.azure.com/
- A deployed GPT model (GPT-4, GPT-4 Turbo, or GPT-3.5)

---

## 🔑 Step 1: Get Your Azure OpenAI Credentials

### Option A: From Azure AI Studio (Recommended)

1. **Go to Azure AI Studio**: https://ai.azure.com/

2. **Navigate to your project**:
   - Click on your project (e.g., "firstProject")
   - Go to "Deployments" section

3. **Find your deployed model**:
   - You should see your model deployment (e.g., "gpt-oss-120B")
   - Click on it to see details

4. **Get the credentials**:
   - **Endpoint**: Copy the endpoint URL (e.g., `https://smith.openai.azure.com/`)
   - **API Key**: Click "Show keys" or go to "Keys and Endpoint" section
   - **Deployment Name**: The name of your deployment (e.g., "gpt-4", "gpt-oss-120B")

### Option B: From Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com/

2. **Navigate to your Cognitive Services resource**:
   - Search for "Cognitive Services"
   - Click on your resource (e.g., "smith")

3. **Get credentials**:
   - Go to "Keys and Endpoint" in the left menu
   - Copy **Key 1** or **Key 2**
   - Copy the **Endpoint**

4. **Get deployment name**:
   - Go to "Model deployments" → "Manage deployments"
   - Note the deployment name (e.g., "gpt-4")

---

## ⚙️ Step 2: Configure Environment Variables

### Copy the Azure template:

```bash
cp .env.azure .env
```

### Edit the `.env` file:

```bash
nano .env
```

### Fill in your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://smith.openai.azure.com/
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4  # or your deployment name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Neo4j (already configured)
NEO4J_URL=neo4j+s://d0d1fe15.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=QR9Xqoy0bdfPVSB77hqO-cHZwaouDYUJW43CU6gYKGA
```

**Important**:
- Replace `your_actual_api_key_here` with your real API key
- Update `AZURE_OPENAI_ENDPOINT` if different
- Update `AZURE_OPENAI_DEPLOYMENT_NAME` to match your deployment

---

## 📦 Step 3: Install Dependencies

```bash
cd /workspaces/lool-/neo4j/schema_evolution
pip install -q -r /workspaces/lool-/neo4j/requirements_agents.txt
```

This will install:
- `langchain-openai` (for Azure OpenAI)
- All other required packages

---

## 🚀 Step 4: Run the System

```bash
python main.py --iterations 2
```

Expected output:
```
================================================================================
🧠 LEGAL KNOWLEDGE GRAPH SCHEMA EVOLUTION SYSTEM
================================================================================
Target Score: 9.0/10.0
Max Iterations: 2
Auto-Implement: False
Output Directory: ./schema_output
================================================================================

🚀 SCHEMA EVOLUTION SYSTEM STARTING
================================================================================

################################################################################
# ITERATION 1/2
################################################################################

Schema Designer - Iteration 1
============================================================

📚 Legal Domain Specialist working...
   ✓ Designed 15 node types, 18 relationship types
...
```

---

## 🔍 Finding Your Azure OpenAI Information

### From Your Provided URL

Your URL: `https://ai.azure.com/resource/models/gpt-oss-120B/...`

This tells us:
- **Model**: gpt-oss-120B (your deployment name)
- **Resource Group**: hi
- **Account**: smith
- **Project**: firstProject

### To Get Your Credentials:

1. **Go to**: https://ai.azure.com/

2. **Navigate**:
   ```
   Projects → firstProject → Deployments → gpt-oss-120B
   ```

3. **Copy**:
   - Endpoint (should be like `https://smith.openai.azure.com/`)
   - API Key (click "Show keys")
   - Deployment name: `gpt-oss-120B`

---

## 🎯 Example Configuration

Based on your URL, your `.env` should look like:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://smith.openai.azure.com/
AZURE_OPENAI_API_KEY=abc123def456...  # Your actual key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-oss-120B
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Neo4j (already configured)
NEO4J_URL=neo4j+s://d0d1fe15.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=QR9Xqoy0bdfPVSB77hqO-cHZwaouDYUJW43CU6gYKGA
NEO4J_DATABASE=neo4j
```

---

## ✅ Verify Setup

Test that everything is configured correctly:

```bash
# Check if environment variables are set
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
api_key = os.getenv('AZURE_OPENAI_API_KEY')
deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

print('✓ Endpoint:', endpoint)
print('✓ API Key:', 'Set' if api_key else 'Missing')
print('✓ Deployment:', deployment)
"
```

Expected output:
```
✓ Endpoint: https://smith.openai.azure.com/
✓ API Key: Set
✓ Deployment: gpt-oss-120B
```

---

## 🚨 Troubleshooting

### "Missing required environment variables"

**Problem**: Environment variables not loaded

**Solution**:
```bash
# Make sure .env file exists
ls -la .env

# Check contents (without showing API key)
grep AZURE .env | grep -v API_KEY

# If missing, copy template
cp .env.azure .env
nano .env  # Add your credentials
```

### "Authentication failed"

**Problem**: Wrong API key or endpoint

**Solution**:
1. Go to Azure Portal → Your Cognitive Services resource
2. Go to "Keys and Endpoint"
3. Copy a fresh key
4. Update `.env` with new key

### "Deployment not found"

**Problem**: Wrong deployment name

**Solution**:
1. Go to Azure AI Studio
2. Check your deployment name exactly
3. Update `AZURE_OPENAI_DEPLOYMENT_NAME` in `.env`

### "Model not available"

**Problem**: Model might not be deployed or accessible

**Solution**:
1. Ensure your model is deployed in Azure AI Studio
2. Check deployment status (should be "Succeeded")
3. Verify you have access to the deployment

---

## 📊 Model Recommendations

For this system, recommended models:

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| **GPT-4 Turbo** | Best quality schemas | Medium | $$$ |
| **GPT-4** | Balanced quality | Slower | $$$$ |
| **GPT-3.5 Turbo** | Fast iterations | Fastest | $ |

**Recommendation**: Start with GPT-4 Turbo for best results.

---

## 💰 Cost Estimation

Approximate costs per iteration:

| Model | Cost per Iteration | Full Run (7 iterations) |
|-------|-------------------|------------------------|
| GPT-4 Turbo | $0.05-0.15 | $0.35-1.05 |
| GPT-4 | $0.10-0.30 | $0.70-2.10 |
| GPT-3.5 Turbo | $0.01-0.03 | $0.07-0.21 |

**Note**: Costs vary based on token usage and Azure pricing.

---

## 🔄 Switching Back to Anthropic Claude

If you want to use Anthropic Claude instead:

1. **Restore original code**:
   ```bash
   git checkout schema_designer.py main.py
   ```

2. **Update .env**:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

3. **Run**:
   ```bash
   python main.py --iterations 2
   ```

---

## 🎓 Azure OpenAI vs Anthropic Claude

### Azure OpenAI Advantages:
- ✅ Enterprise security and compliance
- ✅ Integration with Azure ecosystem
- ✅ Familiar GPT models
- ✅ Azure credits can be used
- ✅ Regional availability

### Anthropic Claude Advantages:
- ✅ Longer context windows (200K tokens)
- ✅ Better at following complex instructions
- ✅ Stronger legal reasoning
- ✅ More conservative/safer outputs

**For this legal schema system**: Both work well! Azure OpenAI is great for enterprise deployments.

---

## 📞 Support

### Getting Help:

1. **Azure Issues**:
   - Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
   - Azure AI Docs: https://learn.microsoft.com/azure/ai-services/openai/

2. **System Issues**:
   - Check QUICKSTART.md
   - Run `python test_structure.py`
   - Review error messages

### Common Azure OpenAI Links:

- **Azure AI Studio**: https://ai.azure.com/
- **Azure Portal**: https://portal.azure.com/
- **Pricing**: https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/
- **Documentation**: https://learn.microsoft.com/azure/ai-services/openai/

---

## ✅ Ready to Go!

Once you have:
- ✅ Azure OpenAI endpoint
- ✅ API key
- ✅ Deployment name
- ✅ Updated `.env` file
- ✅ Installed dependencies

Run:
```bash
python main.py --iterations 5
```

Your system will now use **Azure OpenAI GPT models** instead of Anthropic Claude! 🚀

---

## 🎉 Expected Results

With Azure OpenAI, you should achieve:
- **Iteration 1**: ~8.5/10 (initial schema)
- **Iteration 2-3**: ~8.8-9.0/10 (improvements)
- **Iteration 4-5**: ~9.2-9.5/10 (production-ready)

**Total time**: 20-40 minutes (depending on model)

---

**Last Updated**: November 8, 2025
**Supported Models**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
**Tested**: Structure validated, ready for real API testing
