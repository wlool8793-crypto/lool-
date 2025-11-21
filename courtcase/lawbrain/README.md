# LawBrain - AI Law Firm

A full-service AI law firm built with LangGraph, powered by **Google Gemini 2.5 Pro**. Features specialized lawyers across all major legal practice areas.

## Law Firm Structure

LawBrain operates like a real law firm with a **Senior Partner** supervising **9 specialized practice area lawyers**:

### Senior Partner 👔
**Managing Partner** who intakes client matters, routes to specialists, and coordinates complex multi-practice cases.

### Practice Area Specialists

1. **⚖️ Criminal Lawyer** - Criminal defense, white-collar crime, DUI, appeals
2. **📋 Civil Litigation Lawyer** - Lawsuits, torts, contract disputes, personal injury
3. **💼 Corporate Lawyer** - Business formation, M&A, securities, commercial contracts
4. **💡 IP Lawyer** - Patents, trademarks, copyrights, trade secrets, licensing
5. **👨‍👩‍👧‍👦 Family Lawyer** - Divorce, custody, support, adoption, domestic violence
6. **🏠 Real Estate Lawyer** - Transactions, leases, zoning, landlord-tenant
7. **👔 Employment Lawyer** - Discrimination, wage/hour, wrongful termination
8. **📜 Estate Planning Lawyer** - Wills, trusts, probate, tax planning
9. **🌍 Immigration Lawyer** - Visas, green cards, citizenship, deportation defense

## Prerequisites

Before setting up LawBrain, you need:

1. **Google Cloud Project** with Vertex AI enabled (Project ID: `lool-471716`)
2. **Service Account credentials** or `gcloud` authentication
3. **Python 3.9+** installed

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Authentication

**Follow the detailed guide in `SETUP_AUTH.md`** for step-by-step instructions.

Quick summary:
- Create a service account in Google Cloud Console
- Download the JSON key file
- Set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file

Or authenticate with:
```bash
gcloud auth application-default login
```

### 3. Configure Environment

Your `.env` file should have:

```bash
GOOGLE_CLOUD_PROJECT=lool-471716
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
```

### 4. Run with LangGraph CLI

```bash
langgraph dev
```

## Usage

The Senior Partner automatically routes legal matters to the right specialist(s):

### Single Practice Area Examples

**Criminal Matter:**
```
Client: "I was arrested for DUI"
→ Senior Partner routes to Criminal Lawyer
→ Criminal Lawyer analyzes charges, defenses, and strategy
→ Client receives defense counsel
```

**Business Formation:**
```
Client: "I want to start an LLC"
→ Senior Partner routes to Corporate Lawyer
→ Corporate Lawyer advises on entity selection and formation
→ Client receives business formation guidance
```

**Divorce Case:**
```
Client: "I need help with a divorce"
→ Senior Partner routes to Family Lawyer
→ Family Lawyer handles custody, support, property division
→ Client receives divorce counsel
```

### Multi-Practice Matters

Complex legal matters involve multiple specialists working together:

**Startup Formation:**
```
Corporate Lawyer → Forms entity, drafts operating agreement
IP Lawyer → Protects trademarks and patents
Employment Lawyer → Creates employee agreements and policies
→ Comprehensive startup legal package
```

**Business Sale:**
```
Corporate Lawyer → Structures transaction and purchase agreement
IP Lawyer → Handles IP transfers and licenses
Employment Lawyer → Addresses employee transition issues
Real Estate Lawyer → Manages property lease assignments
→ Complete business sale execution
```

**Divorce with Business Assets:**
```
Family Lawyer → Handles divorce and custody matters
Corporate Lawyer → Values and divides business interests
Real Estate Lawyer → Divides real property
→ Integrated divorce settlement
```

## Project Structure

```
lawbrain/
├── agent.py            # Law firm system (exports 'app')
│                       # - Senior Partner (supervisor)
│                       # - 9 Practice area specialists
├── langgraph.json      # LangGraph configuration
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── ARCHITECTURE.md     # Detailed practice area diagrams
├── CLAUDE.md           # LangGraph development principles
└── README.md           # This file
```

## AI Model

**Powered by Google Gemini 2.5 Pro**

- Model: `gemini-2.0-flash-exp` (Gemini 2.5 Pro)
- Provider: Google Generative AI
- Temperature: 0
- All 9 specialist lawyers use the same Gemini 2.5 Pro model

## Practice Area Details

### Criminal Law ⚖️
- **Focus**: Criminal defense, prosecution, appeals
- **Expertise**: Constitutional law, evidence, plea bargaining, trial strategy
- **Handles**: Felonies, misdemeanors, white-collar crime, DUI, expungement

### Civil Litigation 📋
- **Focus**: Lawsuits and civil disputes
- **Expertise**: Civil procedure, discovery, motion practice, damages
- **Handles**: Contract disputes, torts, business litigation, class actions

### Corporate Law 💼
- **Focus**: Business transactions and governance
- **Expertise**: Entity formation, M&A, securities, contracts
- **Handles**: Business formation, corporate governance, commercial deals

### Intellectual Property 💡
- **Focus**: IP protection and enforcement
- **Expertise**: Patents, trademarks, copyrights, licensing
- **Handles**: IP registration, licensing agreements, infringement

### Family Law 👨‍👩‍👧‍👦
- **Focus**: Domestic relations
- **Expertise**: Divorce, custody, support calculations, adoption
- **Handles**: Marital dissolution, custody disputes, domestic violence

### Real Estate Law 🏠
- **Focus**: Real property transactions and disputes
- **Expertise**: Contracts, title, zoning, leasing
- **Handles**: Purchases, sales, leases, landlord-tenant disputes

### Employment Law 👔
- **Focus**: Workplace legal matters
- **Expertise**: Discrimination, wage/hour, employment contracts
- **Handles**: Wrongful termination, harassment, EEOC claims

### Estate Planning 📜
- **Focus**: Wealth transfer and estate administration
- **Expertise**: Wills, trusts, probate, tax planning
- **Handles**: Estate plans, probate, trust administration

### Immigration Law 🌍
- **Focus**: U.S. immigration matters
- **Expertise**: Visas, green cards, citizenship, deportation
- **Handles**: Family/employment immigration, naturalization, asylum

## Development

Built following LangGraph deployment-first principles:
- Uses prebuilt `create_supervisor` and `create_react_agent`
- No checkpointer (stateless by default)
- Powered exclusively by Google Gemini 2.5 Pro
- Exports compiled graph as `app`
- Law firm structure mirrors real legal practice

## Adding Tools to Lawyers

Extend specialist capabilities by adding tools in `agent.py`:

```python
from langchain_core.tools import tool

# Criminal law tools
@tool
def search_criminal_code(state: str, offense: str) -> str:
    """Search state criminal codes and sentencing guidelines."""
    # Implementation
    pass

# Corporate law tools
@tool
def check_business_name(state: str, name: str) -> str:
    """Check business name availability."""
    # Implementation
    pass

# Assign to appropriate specialist
criminal_law_agent = create_react_agent(
    model=model,
    tools=[search_criminal_code, sentencing_calculator],
    name="CriminalLawyer",
    prompt="..."
)
```

## Adding New Practice Areas

Expand the law firm by adding new specialists:

```python
# Example: Add a Tax Law specialist
tax_law_agent = create_react_agent(
    model=model,
    tools=[tax_code_search, tax_calculator],
    name="TaxLawyer",
    prompt="""You are a Tax Law Expert specializing in..."""
)

# Update Senior Partner
senior_partner = create_supervisor(
    agents=[
        criminal_law_agent,
        civil_litigation_agent,
        corporate_law_agent,
        ip_law_agent,
        family_law_agent,
        real_estate_agent,
        employment_law_agent,
        estate_planning_agent,
        immigration_law_agent,
        tax_law_agent  # Add new specialist
    ],
    model=model,
    prompt="""Updated routing with Tax Lawyer..."""
)
```

## Multi-Practice Coordination

The Senior Partner automatically coordinates multiple specialists for complex matters:

| Client Matter | Specialists Involved |
|--------------|---------------------|
| Startup Formation | Corporate + IP + Employment |
| Divorce with Business | Family + Corporate + Real Estate |
| Employment Lawsuit | Employment + Civil Litigation |
| Estate with Business | Estate Planning + Corporate |
| Real Estate Development | Real Estate + Corporate |
| Immigration for Business Owner | Immigration + Corporate |

## Troubleshooting

### "Could not automatically determine credentials"

Make sure you've set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file pointing to your service account JSON key file, or run `gcloud auth application-default login`.

### "Permission Denied" or "403 Forbidden"

1. Verify your service account has the "Vertex AI User" role
2. Enable Vertex AI API: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project=lool-471716

### "Project not found"

Verify your project ID is correct: `lool-471716` and you have access to it.

## See Also

- **ARCHITECTURE.md** - Detailed law firm structure with visual diagrams and workflows
- **CLAUDE.md** - LangGraph development principles and best practices

---

**LawBrain**: Your full-service AI law firm powered by Google Gemini 2.5 Pro.
