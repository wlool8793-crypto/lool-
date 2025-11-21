"""
Evaluation rubric for schema scoring
Defines criteria for 10/10 score in each dimension
"""

from typing import Dict, List


DIMENSION_WEIGHTS = {
    "legal_completeness": 0.20,
    "rag_effectiveness": 0.25,
    "performance": 0.15,
    "data_quality": 0.15,
    "cross_jurisdictional": 0.10,
    "user_experience": 0.05,
    "scalability": 0.05,
    "extensibility": 0.05
}


REQUIRED_LEGAL_ENTITIES = {
    "core": [
        "Case", "Statute", "Section", "Judge", "Court", "Party"
    ],
    "advanced": [
        "Principle", "Doctrine", "Holding", "Appeal", "Motion"
    ],
    "structural": [
        "Part", "Order", "Definition", "Rule"
    ],
    "temporal": [
        "CaseVersion", "Amendment", "ChangeLog"
    ],
    "rag": [
        "Chunk"  # For text chunking and embeddings
    ]
}


REQUIRED_RELATIONSHIPS = {
    "citation": [
        "CITES_PRECEDENT", "OVERRULES", "AFFIRMS", "DISTINGUISHES"
    ],
    "structural": [
        "PART_OF", "BELONGS_TO", "APPLIES_SECTION", "HAS_PART"
    ],
    "procedural": [
        "DECIDED_BY", "BEFORE_COURT", "PETITIONER", "RESPONDENT"
    ],
    "temporal": [
        "AMENDS", "SUPERSEDES", "VERSION_OF"
    ],
    "rag": [
        "CHUNK_OF", "REFERENCES", "CITES_IN_CHUNK"
    ],
    "semantic": [
        "ESTABLISHES", "DEFINES", "APPLIES_CONCEPT"
    ]
}


RAG_REQUIREMENTS = {
    "vector_indexes": {
        "case_embedding": {"required": True, "dimensions": 1536},
        "section_embedding": {"required": True, "dimensions": 1536},
        "chunk_embedding": {"required": True, "dimensions": 1536}
    },
    "retrieval_relationships": {
        "CHUNK_OF": {"from": "Chunk", "to": ["Case", "Section"]},
        "CITES": {"from": "Chunk", "to": "Section"},
        "REFERENCES": {"from": "Chunk", "to": "Case"}
    },
    "metadata_properties": {
        "relevance_score": True,
        "rerank_score": True,
        "context": True,
        "source_attribution": True
    },
    "multi_granularity": {
        "case_level": True,  # Full case embedding
        "section_level": True,  # Individual section embeddings
        "chunk_level": True  # Fine-grained chunk embeddings
    }
}


PERFORMANCE_TARGETS = {
    "simple_lookup_ms": 100,
    "section_cases_ms": 200,
    "precedent_chain_ms": 500,
    "vector_search_ms": 200,
    "complex_join_ms": 500,
    "chunk_retrieval_ms": 150
}


REQUIRED_INDEXES = {
    "composite": [
        "Case(jurisdiction, date, case_type)",
        "Case(jurisdiction, year)",
        "Section(statute, part, section_number)"
    ],
    "vector": [
        "Case.embedding",
        "Section.embedding",
        "Chunk.embedding"
    ],
    "fulltext": [
        "Case(title, summary, full_text)",
        "Section(title, full_text)"
    ],
    "single": [
        "Case.citation",
        "Section.section_id",
        "Case.trust_score",
        "Case.year"
    ]
}


DATA_QUALITY_REQUIREMENTS = {
    "provenance": {
        "source": {"type": "string", "required": True},
        "extracted_at": {"type": "datetime", "required": True},
        "extracted_by": {"type": "string", "required": False},
        "confidence_score": {"type": "float", "required": False}
    },
    "versioning": {
        "version": {"type": "integer", "required": True},
        "created_at": {"type": "datetime", "required": True},
        "updated_at": {"type": "datetime", "required": True},
        "changelog": {"type": "list", "required": False}
    },
    "trust": {
        "trust_score": {"type": "float", "range": [0, 1], "required": True},
        "authority_level": {"type": "string", "required": False},
        "citation_count": {"type": "integer", "required": False},
        "verification_status": {"type": "string", "required": False}
    },
    "constraints": {
        "uniqueness": ["citation", "id"],
        "referential_integrity": True,
        "data_validation": True
    }
}


def calculate_overall_score(dimension_scores: Dict[str, float]) -> float:
    """Calculate weighted overall score from dimension scores"""
    total = 0.0
    for dimension, weight in DIMENSION_WEIGHTS.items():
        if dimension in dimension_scores:
            total += dimension_scores[dimension] * weight
    return round(total, 2)


def is_production_ready(overall_score: float, dimension_scores: Dict[str, float], min_dimension_score: float = 8.0) -> bool:
    """
    Check if schema is production ready

    Criteria:
    - Overall score >= 9.0
    - All dimensions >= 8.0
    """
    if overall_score < 9.0:
        return False

    for score in dimension_scores.values():
        if score < min_dimension_score:
            return False

    return True


def get_production_blockers(overall_score: float, dimension_scores: Dict[str, float]) -> List[str]:
    """Identify what's blocking production readiness"""
    blockers = []

    if overall_score < 9.0:
        blockers.append(f"Overall score {overall_score:.1f} is below 9.0 threshold")

    for dimension, score in dimension_scores.items():
        if score < 8.0:
            blockers.append(f"{dimension} score {score:.1f} is below 8.0 threshold")

    return blockers


# Scoring guidelines for reference
SCORING_GUIDELINES = {
    "legal_completeness": {
        "10": "All required entities + relationships + procedural elements + temporal tracking complete",
        "9": "Missing 1-2 minor entities (e.g., Motion, Pleading)",
        "8": "Missing Appeal/Motion or some procedural elements",
        "7": "Missing several advanced entities",
        "6": "Core entities only, missing structural/temporal",
        "<6": "Significant gaps in legal modeling"
    },
    "rag_effectiveness": {
        "10": "Multi-granularity embeddings + hybrid search + full context assembly + provenance",
        "9": "Missing reranking metadata or cross-reference resolution",
        "8": "Missing chunk embeddings OR section-level embeddings",
        "7": "Basic vector search only, limited metadata",
        "6": "Vector search without graph integration",
        "<6": "No or minimal RAG support"
    },
    "performance": {
        "10": "All queries meet targets on 10K+ nodes + optimal indexes",
        "9": "1-2 queries slightly slow (within 20% of target)",
        "8": "3-4 queries slow OR missing 1-2 key indexes",
        "7": "Several slow queries, needs optimization",
        "6": "Performance acceptable but not optimized",
        "<6": "Most queries slow, poor indexing"
    },
    "data_quality": {
        "10": "Complete provenance + versioning + trust + audit trail + constraints",
        "9": "Missing audit trail OR conflict resolution",
        "8": "Missing trust scoring or advanced versioning",
        "7": "Basic provenance only",
        "6": "Minimal metadata",
        "<6": "No quality tracking"
    }
}
