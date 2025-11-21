# CPC Knowledge Graph - Bangladesh Legal Cases

A knowledge graph built from 5 landmark legal cases related to the Code of Civil Procedure (Bangladesh).

## 🎯 What's Inside

### Graph Contents
- **5 Cases** covering Revision, Appeal, and Inherent Power
- **8 Sections** from CPC and Partition Act
- **6 Judges** who decided these cases
- **10 Parties** (petitioners and respondents)
- **6 Legal Principles** (res judicata, doctrine of merger, etc.)
- **3 Courts** (High Court Division, District Judge, Trial Court)
- **3 Statutes** (CPC 1908, Partition Act 1893, Suits Valuation Act 1887)
- **3 Topics** (Revision, Inherent Power, Appeal)

### Total: 46 nodes, 51 relationships

---

## 📁 Files

1. **`cpc_data.json`** - Structured data extracted from PDF
2. **`cpc_graph.html`** - Interactive visualization (open in browser)
3. **`cpc_graph.png`** - Static visualization image
4. **`extract_cpc.py`** - Data extraction script
5. **`build_graph.py`** - Neo4j graph builder
6. **`visualize_graph.py`** - Visualization generator

---

## 🔍 Explore the Graph

### Option 1: Interactive HTML
```bash
# Open in your browser
open cpc_graph.html
```
- Drag nodes to reposition
- Zoom in/out with mouse wheel
- Click nodes to see details
- Hover over relationships

### Option 2: Neo4j Browser
Navigate to: https://console.neo4j.io

Sample queries:

```cypher
// View all cases
MATCH (c:Case)
RETURN c.name, c.citation, c.topic

// Find cases involving Section 115
MATCH (c:Case)-[:APPLIES_SECTION]->(s:Section)
WHERE s.section_id CONTAINS '115'
RETURN c.name, c.citation

// Show case relationships
MATCH path = (c:Case)-[r]->(n)
WHERE c.citation = '60 DLR 20'
RETURN path

// Legal principles and their cases
MATCH (p:Principle)<-[:ESTABLISHES]-(c:Case)
RETURN p.name, collect(c.citation) as cases

// Court hierarchy
MATCH (c:Case)-[:BEFORE_COURT]->(court:Court)
RETURN court.name, count(c) as case_count
ORDER BY case_count DESC

// Cases decided by specific judge
MATCH (c:Case)-[:DECIDED_BY]->(j:Judge)
WHERE j.name CONTAINS 'Sheikh Abdul Awal'
RETURN c.name, c.citation, c.year
```

---

## 🎨 Graph Legend

**Node Colors:**
- 🔴 **Red (Star)** - Cases
- 🟡 **Yellow (Box)** - Sections
- 🟣 **Purple (Database)** - Statutes
- 🟢 **Green (Diamond)** - Legal Principles
- 🔵 **Teal (Dot)** - Judges
- 🟦 **Light Teal (Dot)** - Parties
- 🔺 **Pink (Triangle)** - Courts
- 🟠 **Light Red (Ellipse)** - Topics

**Relationships:**
- `DECIDED_BY` - Case → Judge
- `BEFORE_COURT` - Case → Court
- `APPLIES_SECTION` - Case → Section
- `ESTABLISHES` - Case → Principle
- `BELONGS_TO_TOPIC` - Case → Topic
- `PETITIONER` / `RESPONDENT` - Case → Party
- `PART_OF` - Section → Statute
- `CITES_PRECEDENT` - Case → Case

---

## 📊 Example Insights

### Key Cases:

1. **Siddique Mia vs Md Idris Miah (60 DLR 20)**
   - Topic: Revision
   - Principle: Res judicata between stages
   - Sections: Section 10, 115(4), Order VI rule 17

2. **Syed Mayeenul Huq vs MA Razzaque (60 DLR 704)**
   - Topic: Revision
   - Principle: Stare decisis
   - Sections: Section 115(2)

3. **East West Property vs Md Akrab Ali (74 DLR 101)**
   - Topic: Inherent Power
   - Principle: Inherent power of court
   - Sections: Section 151, Order VI rule 18

4. **Yeamin Nobi vs Moklesur Rahman (67 DLR 281)**
   - Topic: Appeal
   - Principle: No limitation for Partition Act Section 4
   - Sections: Section 4 (Partition Act)

5. **SMA Razzaque vs Artha Rin Adalat (72 DLR 803)**
   - Topic: Appeal
   - Principle: Doctrine of merger
   - Sections: Section 2(2)

---

## 🚀 Rebuild the Graph

```bash
# Extract data from PDF
python3 extract_cpc.py

# Build Neo4j graph
python3 build_graph.py

# Generate visualizations
python3 visualize_graph.py
```

---

## 🔐 Neo4j Connection

The graph is stored in Neo4j Aura:
- **URL**: neo4j+s://d0d1fe15.databases.neo4j.io
- **Database**: neo4j
- **Instance**: Instance01

Credentials are in `.env` file.

---

## 💡 Use Cases

1. **Legal Research**: Find related cases by section or principle
2. **Case Analysis**: Trace precedent citations
3. **Education**: Learn CPC provisions through real cases
4. **Pattern Discovery**: Identify frequently cited sections
5. **Jurisdiction Analysis**: Understand court hierarchies

---

## 📚 Source

All data extracted from: **cpc2.pdf**
- Case summaries from The Code of Civil Procedure, 1908 - Laws of Bangladesh
- Compiled by MD TAREK HOSSAIN (223100010), Department of Law

---

Built with ❤️ using Neo4j, Python, and pyvis
