"""
Schema Designer Agent - Coordinates 4 specialist sub-agents to create/improve schema

Uses LangGraph supervisor pattern to orchestrate:
1. Legal Domain Specialist
2. RAG Architecture Specialist
3. Performance Specialist
4. Data Quality Specialist
"""

from typing import Dict, List, Optional, Annotated
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import json
import os

from vertex_express_client import VertexAIExpressChat
from state import SchemaDefinition, EvaluationResult
from evaluation_rubric import (
    REQUIRED_LEGAL_ENTITIES,
    REQUIRED_RELATIONSHIPS,
    RAG_REQUIREMENTS,
    REQUIRED_INDEXES,
    DATA_QUALITY_REQUIREMENTS
)


# Initialize Google Vertex AI Express with API Key
def get_llm(temperature: float = 0.7):
    """Get Google Vertex AI Express Gemini 2.5 Pro model instance"""
    api_key = os.getenv("VERTEX_AI_EXPRESS_KEY")
    model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-pro")

    if not api_key:
        raise ValueError("VERTEX_AI_EXPRESS_KEY must be set in .env file")

    return VertexAIExpressChat(
        api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=8192
    )


class LegalDomainSpecialist:
    """Designs core legal entities and relationships"""

    def __init__(self):
        self.llm = get_llm(temperature=0.7)

    def design(self, context: Dict) -> Dict:
        """Design legal entities and relationships"""

        current_schema = context.get("current_schema")
        feedback = context.get("evaluation_feedback")
        iteration = context.get("iteration", 0)

        system_prompt = f"""You are a Legal Domain Expert designing a Neo4j graph schema for Bangladesh legal data.

**Your Responsibilities:**
- Design node types for legal entities (Case, Statute, Section, Judge, Court, Party, Principle, Holding, Appeal, etc.)
- Define properties for each entity type
- Create relationships between legal entities
- Ensure schema supports precedent chains, statutory structure, case law

**Required Entities (from rubric):**
Core: {REQUIRED_LEGAL_ENTITIES['core']}
Advanced: {REQUIRED_LEGAL_ENTITIES['advanced']}
Structural: {REQUIRED_LEGAL_ENTITIES['structural']}
Temporal: {REQUIRED_LEGAL_ENTITIES['temporal']}

**Required Relationships:**
Citation: {REQUIRED_RELATIONSHIPS['citation']}
Structural: {REQUIRED_RELATIONSHIPS['structural']}
Procedural: {REQUIRED_RELATIONSHIPS['procedural']}
Temporal: {REQUIRED_RELATIONSHIPS['temporal']}

**Domain Context:**
- Bangladesh Code of Civil Procedure (CPC)
- Supreme Court and High Court Division case law
- Cross-jurisdictional (India, Pakistan) case references
- Existing graph has 372 nodes, 668 relationships

**Current Iteration:** {iteration}

Output your design as JSON with:
{{
    "nodes": [
        {{
            "label": "Case",
            "properties": {{"citation": "string", "title": "string", ...}},
            "description": "..."
        }},
        ...
    ],
    "relationships": [
        {{
            "type": "CITES_PRECEDENT",
            "from": "Case",
            "to": "Case",
            "properties": {{"cited_for": "string", ...}},
            "description": "..."
        }},
        ...
    ]
}}
"""

        user_prompt = "Design the legal domain schema."

        if current_schema:
            user_prompt += f"\n\nCurrent schema version: {current_schema.get('version')}"

        if feedback:
            legal_score = feedback.get("dimension_scores", {}).get("legal_completeness", {})
            missing = legal_score.get("missing_components", [])
            user_prompt += f"\n\nEvaluation Feedback:\n- Legal Completeness Score: {legal_score.get('score', 0)}/10"
            if missing:
                user_prompt += f"\n- Missing Components: {', '.join(missing)}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        # Parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            design = json.loads(content)
            return design
        except Exception as e:
            print(f"Error parsing legal domain design: {e}")
            return {"nodes": [], "relationships": []}


class RAGArchitectureSpecialist:
    """Designs RAG-specific components (embeddings, chunks, retrieval)"""

    def __init__(self):
        self.llm = get_llm(temperature=0.7)

    def design(self, context: Dict, legal_design: Dict) -> Dict:
        """Design RAG architecture components"""

        feedback = context.get("evaluation_feedback")
        iteration = context.get("iteration", 0)

        system_prompt = f"""You are a RAG Architecture Expert designing retrieval-optimized components for a legal knowledge graph.

**Your Responsibilities:**
- Add Chunk entity for text chunking
- Design vector embedding properties (1536 dimensions, text-embedding-3-large)
- Create multi-granularity embeddings (case-level, section-level, chunk-level)
- Define retrieval relationships (CHUNK_OF, REFERENCES, CITES_IN_CHUNK)
- Add metadata for relevance scoring, reranking, context assembly

**Required RAG Components:**
- Vector Indexes: {list(RAG_REQUIREMENTS['vector_indexes'].keys())}
- Retrieval Relationships: {list(RAG_REQUIREMENTS['retrieval_relationships'].keys())}
- Metadata Properties: {list(RAG_REQUIREMENTS['metadata_properties'].keys())}
- Multi-Granularity: {list(RAG_REQUIREMENTS['multi_granularity'].keys())}

**Legal Design Context:**
You're enhancing this legal schema:
{json.dumps(legal_design, indent=2)}

**Current Iteration:** {iteration}

Output your enhancements as JSON with:
{{
    "nodes": [
        {{
            "label": "Chunk",
            "properties": {{"text": "string", "embedding": "vector", ...}},
            "description": "..."
        }}
    ],
    "relationships": [
        {{
            "type": "CHUNK_OF",
            "from": "Chunk",
            "to": "Case",
            "properties": {{"position": "integer", ...}},
            "description": "..."
        }}
    ],
    "vector_indexes": [
        {{
            "name": "case_embedding_index",
            "node_label": "Case",
            "property": "embedding",
            "dimensions": 1536,
            "similarity": "cosine"
        }}
    ],
    "rag_configuration": {{
        "chunk_size": 512,
        "chunk_overlap": 50,
        "embedding_model": "text-embedding-3-large",
        "retrieval_strategy": "hybrid"
    }}
}}
"""

        user_prompt = "Design the RAG architecture enhancements."

        if feedback:
            rag_score = feedback.get("dimension_scores", {}).get("rag_effectiveness", {})
            missing = rag_score.get("missing_components", [])
            user_prompt += f"\n\nEvaluation Feedback:\n- RAG Effectiveness Score: {rag_score.get('score', 0)}/10"
            if missing:
                user_prompt += f"\n- Missing Components: {', '.join(missing)}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            design = json.loads(content)
            return design
        except Exception as e:
            print(f"Error parsing RAG design: {e}")
            return {"nodes": [], "relationships": [], "vector_indexes": [], "rag_configuration": {}}


class PerformanceSpecialist:
    """Designs indexes and optimization strategies"""

    def __init__(self):
        self.llm = get_llm(temperature=0.6)

    def design(self, context: Dict, combined_design: Dict) -> Dict:
        """Design performance optimizations"""

        feedback = context.get("evaluation_feedback")
        iteration = context.get("iteration", 0)

        system_prompt = f"""You are a Performance Optimization Expert for Neo4j graphs.

**Your Responsibilities:**
- Design composite indexes for common query patterns
- Create single-property indexes for lookups
- Define full-text search indexes
- Ensure query performance targets are met

**Performance Targets:**
- Simple lookups: <100ms
- Section cases: <200ms
- Precedent chains: <500ms
- Vector search: <200ms
- Complex joins: <500ms
- Chunk retrieval: <150ms

**Required Index Types:**
Composite: {REQUIRED_INDEXES['composite']}
Vector: {REQUIRED_INDEXES['vector']}
Full-text: {REQUIRED_INDEXES['fulltext']}
Single: {REQUIRED_INDEXES['single']}

**Schema Context:**
{json.dumps(combined_design, indent=2)[:2000]}...

**Current Iteration:** {iteration}

Output your index design as JSON with:
{{
    "indexes": [
        {{
            "type": "composite",
            "node_label": "Case",
            "properties": ["jurisdiction", "date", "case_type"],
            "name": "case_jurisdiction_date_type_idx"
        }},
        {{
            "type": "fulltext",
            "node_label": "Case",
            "properties": ["title", "summary", "full_text"],
            "name": "case_fulltext_idx"
        }},
        {{
            "type": "single",
            "node_label": "Case",
            "property": "citation",
            "unique": true,
            "name": "case_citation_idx"
        }}
    ],
    "query_optimizations": [
        {{
            "query_type": "section_lookup",
            "target_ms": 100,
            "strategy": "Use composite index on (statute, section_number)"
        }}
    ]
}}
"""

        user_prompt = "Design performance optimizations."

        if feedback:
            perf_score = feedback.get("dimension_scores", {}).get("performance", {})
            missing = perf_score.get("missing_components", [])
            user_prompt += f"\n\nEvaluation Feedback:\n- Performance Score: {perf_score.get('score', 0)}/10"
            if missing:
                user_prompt += f"\n- Missing Optimizations: {', '.join(missing)}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            design = json.loads(content)
            return design
        except Exception as e:
            print(f"Error parsing performance design: {e}")
            return {"indexes": [], "query_optimizations": []}


class DataQualitySpecialist:
    """Designs data quality, provenance, versioning, trust components"""

    def __init__(self):
        self.llm = get_llm(temperature=0.6)

    def design(self, context: Dict, combined_design: Dict) -> Dict:
        """Design data quality components"""

        feedback = context.get("evaluation_feedback")
        iteration = context.get("iteration", 0)

        system_prompt = f"""You are a Data Quality Expert designing provenance, versioning, and trust mechanisms.

**Your Responsibilities:**
- Add provenance properties (source, extracted_at, extracted_by, confidence_score)
- Design versioning system (version, created_at, updated_at, changelog)
- Create trust scoring (trust_score, authority_level, citation_count, verification_status)
- Define constraints (uniqueness, referential integrity, validation)

**Required Data Quality Components:**
Provenance: {list(DATA_QUALITY_REQUIREMENTS['provenance'].keys())}
Versioning: {list(DATA_QUALITY_REQUIREMENTS['versioning'].keys())}
Trust: {list(DATA_QUALITY_REQUIREMENTS['trust'].keys())}
Constraints: {DATA_QUALITY_REQUIREMENTS['constraints']}

**Schema Context:**
{json.dumps(combined_design, indent=2)[:2000]}...

**Current Iteration:** {iteration}

Output your quality enhancements as JSON with:
{{
    "property_additions": [
        {{
            "node_label": "Case",
            "properties": {{
                "source": {{"type": "string", "required": true}},
                "extracted_at": {{"type": "datetime", "required": true}},
                "trust_score": {{"type": "float", "range": [0, 1], "required": true}},
                "version": {{"type": "integer", "required": true}}
            }}
        }}
    ],
    "constraints": [
        {{
            "type": "uniqueness",
            "node_label": "Case",
            "property": "citation",
            "name": "case_citation_unique"
        }},
        {{
            "type": "existence",
            "node_label": "Case",
            "property": "trust_score",
            "name": "case_trust_score_required"
        }}
    ],
    "audit_trail": {{
        "enabled": true,
        "track_changes": ["updated_at", "changelog"],
        "versioning_strategy": "incremental"
    }}
}}
"""

        user_prompt = "Design data quality components."

        if feedback:
            quality_score = feedback.get("dimension_scores", {}).get("data_quality", {})
            missing = quality_score.get("missing_components", [])
            user_prompt += f"\n\nEvaluation Feedback:\n- Data Quality Score: {quality_score.get('score', 0)}/10"
            if missing:
                user_prompt += f"\n- Missing Components: {', '.join(missing)}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            design = json.loads(content)
            return design
        except Exception as e:
            print(f"Error parsing data quality design: {e}")
            return {"property_additions": [], "constraints": [], "audit_trail": {}}


class SchemaDesigner:
    """
    Main Schema Designer agent - coordinates 4 specialists

    Workflow:
    1. Legal Domain Specialist designs entities & relationships
    2. RAG Specialist adds embeddings & retrieval components
    3. Performance Specialist adds indexes
    4. Data Quality Specialist adds provenance/versioning/trust
    5. Merge all designs into final SchemaDefinition
    """

    def __init__(self):
        self.legal_specialist = LegalDomainSpecialist()
        self.rag_specialist = RAGArchitectureSpecialist()
        self.performance_specialist = PerformanceSpecialist()
        self.quality_specialist = DataQualitySpecialist()

    def design_schema(
        self,
        iteration: int,
        current_schema: Optional[SchemaDefinition] = None,
        evaluation_feedback: Optional[EvaluationResult] = None
    ) -> SchemaDefinition:
        """
        Orchestrate specialists to design/improve schema

        Args:
            iteration: Current iteration number
            current_schema: Existing schema (if improving)
            evaluation_feedback: Feedback from evaluator

        Returns:
            SchemaDefinition with complete schema design
        """

        print(f"\n{'='*60}")
        print(f"Schema Designer - Iteration {iteration}")
        print(f"{'='*60}\n")

        context = {
            "iteration": iteration,
            "current_schema": current_schema,
            "evaluation_feedback": evaluation_feedback
        }

        # Step 1: Legal Domain Design
        print("📚 Legal Domain Specialist working...")
        legal_design = self.legal_specialist.design(context)
        print(f"   ✓ Designed {len(legal_design.get('nodes', []))} node types, "
              f"{len(legal_design.get('relationships', []))} relationship types")

        # Step 2: RAG Architecture
        print("🔍 RAG Architecture Specialist working...")
        rag_design = self.rag_specialist.design(context, legal_design)
        print(f"   ✓ Added {len(rag_design.get('nodes', []))} RAG nodes, "
              f"{len(rag_design.get('vector_indexes', []))} vector indexes")

        # Merge legal + RAG designs
        combined_design = self._merge_designs(legal_design, rag_design)

        # Step 3: Performance Optimization
        print("⚡ Performance Specialist working...")
        performance_design = self.performance_specialist.design(context, combined_design)
        print(f"   ✓ Created {len(performance_design.get('indexes', []))} indexes")

        # Step 4: Data Quality
        print("✨ Data Quality Specialist working...")
        quality_design = self.quality_specialist.design(context, combined_design)
        print(f"   ✓ Added {len(quality_design.get('property_additions', []))} quality properties, "
              f"{len(quality_design.get('constraints', []))} constraints")

        # Step 5: Final merge
        final_schema = self._create_final_schema(
            iteration,
            legal_design,
            rag_design,
            performance_design,
            quality_design,
            current_schema
        )

        print(f"\n✅ Schema Design Complete")
        print(f"   Total Nodes: {len(final_schema['nodes'])}")
        print(f"   Total Relationships: {len(final_schema['relationships'])}")
        print(f"   Total Indexes: {len(final_schema['indexes'])}")
        print(f"   Total Constraints: {len(final_schema['constraints'])}\n")

        return final_schema

    def _merge_designs(self, design1: Dict, design2: Dict) -> Dict:
        """Merge two design dictionaries"""
        merged = {}
        for key in set(list(design1.keys()) + list(design2.keys())):
            val1 = design1.get(key, [])
            val2 = design2.get(key, [])

            if isinstance(val1, list) and isinstance(val2, list):
                merged[key] = val1 + val2
            elif isinstance(val1, dict) and isinstance(val2, dict):
                merged[key] = {**val1, **val2}
            else:
                merged[key] = val2 if val2 else val1

        return merged

    def _create_final_schema(
        self,
        iteration: int,
        legal_design: Dict,
        rag_design: Dict,
        performance_design: Dict,
        quality_design: Dict,
        current_schema: Optional[SchemaDefinition]
    ) -> SchemaDefinition:
        """Create final SchemaDefinition from all specialist designs"""

        # Merge nodes
        nodes = legal_design.get("nodes", []) + rag_design.get("nodes", [])

        # Apply quality property additions
        for addition in quality_design.get("property_additions", []):
            # Skip malformed additions
            if "node_label" not in addition or "properties" not in addition:
                continue

            for node in nodes:
                if node.get("label") == addition["node_label"]:
                    # Ensure properties dict exists
                    if "properties" not in node:
                        node["properties"] = {}
                    node["properties"].update(addition["properties"])

        # Merge relationships
        relationships = (
            legal_design.get("relationships", []) +
            rag_design.get("relationships", [])
        )

        # Merge indexes
        indexes = performance_design.get("indexes", [])
        if "vector_indexes" in rag_design:
            indexes.extend(rag_design["vector_indexes"])

        # Get constraints
        constraints = quality_design.get("constraints", [])

        # Determine changes from previous
        changes = []
        if current_schema:
            changes.append(f"Improved based on iteration {current_schema.get('iteration', 0)} feedback")
            if evaluation_feedback := current_schema.get("evaluation_feedback"):
                for suggestion in evaluation_feedback.get("critical_improvements", [])[:3]:
                    changes.append(f"Addressed: {suggestion.get('issue', '')}")
        else:
            changes.append("Initial schema design")

        # Create schema definition
        schema = SchemaDefinition(
            version=f"v{iteration}.0",
            iteration=iteration,
            nodes=nodes,
            relationships=relationships,
            indexes=indexes,
            constraints=constraints,
            rag_configuration=rag_design.get("rag_configuration", {}),
            changes_from_previous=changes,
            design_rationale={
                "legal_design": f"{len(legal_design.get('nodes', []))} entities covering Bangladesh legal system",
                "rag_design": f"Multi-granularity embeddings with {len(rag_design.get('vector_indexes', []))} vector indexes",
                "performance": f"{len(indexes)} indexes for query optimization",
                "quality": f"{len(constraints)} constraints ensuring data integrity"
            }
        )

        return schema


# Main entry point
def create_schema_designer() -> SchemaDesigner:
    """Factory function to create SchemaDesigner instance"""
    return SchemaDesigner()
