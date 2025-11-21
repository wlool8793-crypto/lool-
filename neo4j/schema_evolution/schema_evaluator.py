"""
Schema Evaluator Agent - Evaluates schema across 8 dimensions

Evaluates:
1. Legal Completeness (20%)
2. RAG Effectiveness (25%)
3. Performance (15%)
4. Data Quality (15%)
5. Cross-Jurisdictional Support (10%)
6. User Experience (5%)
7. Scalability (5%)
8. Extensibility (5%)
"""

from typing import Dict, List
from datetime import datetime
import uuid

from state import SchemaDefinition, EvaluationResult, DimensionScore, ImprovementSuggestion
from evaluation_rubric import (
    REQUIRED_LEGAL_ENTITIES,
    REQUIRED_RELATIONSHIPS,
    RAG_REQUIREMENTS,
    PERFORMANCE_TARGETS,
    REQUIRED_INDEXES,
    DATA_QUALITY_REQUIREMENTS,
    DIMENSION_WEIGHTS,
    calculate_overall_score,
    is_production_ready,
    get_production_blockers
)


class SchemaEvaluator:
    """
    Evaluates schema against comprehensive rubric
    Provides detailed scoring and improvement suggestions
    """

    def __init__(self):
        pass

    def evaluate(self, schema: SchemaDefinition) -> EvaluationResult:
        """
        Evaluate schema across all dimensions

        Args:
            schema: SchemaDefinition to evaluate

        Returns:
            EvaluationResult with scores and suggestions
        """

        print(f"\n{'='*60}")
        print(f"Schema Evaluator - Version {schema['version']}")
        print(f"{'='*60}\n")

        # Evaluate each dimension
        dimension_scores = {}

        print("📊 Evaluating Legal Completeness...")
        dimension_scores["legal_completeness"] = self._evaluate_legal_completeness(schema)

        print("🔍 Evaluating RAG Effectiveness...")
        dimension_scores["rag_effectiveness"] = self._evaluate_rag_effectiveness(schema)

        print("⚡ Evaluating Performance...")
        dimension_scores["performance"] = self._evaluate_performance(schema)

        print("✨ Evaluating Data Quality...")
        dimension_scores["data_quality"] = self._evaluate_data_quality(schema)

        print("🌏 Evaluating Cross-Jurisdictional Support...")
        dimension_scores["cross_jurisdictional"] = self._evaluate_cross_jurisdictional(schema)

        print("👤 Evaluating User Experience...")
        dimension_scores["user_experience"] = self._evaluate_user_experience(schema)

        print("📈 Evaluating Scalability...")
        dimension_scores["scalability"] = self._evaluate_scalability(schema)

        print("🔧 Evaluating Extensibility...")
        dimension_scores["extensibility"] = self._evaluate_extensibility(schema)

        # Calculate overall score
        overall_score = calculate_overall_score(
            {k: v["score"] for k, v in dimension_scores.items()}
        )

        # Check production readiness
        ready = is_production_ready(
            overall_score,
            {k: v["score"] for k, v in dimension_scores.items()}
        )

        blockers = get_production_blockers(
            overall_score,
            {k: v["score"] for k, v in dimension_scores.items()}
        )

        # Generate improvement suggestions
        critical_improvements = self._generate_improvements(dimension_scores)

        # Identify strengths
        strengths = self._identify_strengths(dimension_scores)

        # Print summary
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS - {schema['version']}")
        print(f"{'='*60}")
        print(f"\n🎯 Overall Score: {overall_score:.2f}/10.0")
        print(f"{'='*60}\n")

        for dim_name, dim_score in dimension_scores.items():
            weight = DIMENSION_WEIGHTS[dim_name]
            print(f"{dim_name:.<30} {dim_score['score']:.1f}/10  (weight: {weight*100:.0f}%)")

        print(f"\n{'='*60}")
        print(f"Production Ready: {'✅ YES' if ready else '❌ NO'}")
        if blockers:
            print(f"\nBlockers:")
            for blocker in blockers:
                print(f"  • {blocker}")
        print(f"{'='*60}\n")

        # Create evaluation result
        result = EvaluationResult(
            evaluation_id=str(uuid.uuid4()),
            schema_version=schema["version"],
            timestamp=datetime.utcnow().isoformat(),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            critical_improvements=critical_improvements,
            strengths=strengths,
            ready_for_production=ready,
            production_blockers=blockers
        )

        return result

    def _evaluate_legal_completeness(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate legal entity and relationship completeness"""

        nodes = {node.get("label", "") for node in schema["nodes"] if node.get("label")}
        relationships = {rel.get("type", "") for rel in schema["relationships"] if rel.get("type")}

        # Check required entities
        all_required_entities = (
            REQUIRED_LEGAL_ENTITIES["core"] +
            REQUIRED_LEGAL_ENTITIES["advanced"] +
            REQUIRED_LEGAL_ENTITIES["structural"] +
            REQUIRED_LEGAL_ENTITIES["temporal"]
        )

        missing_entities = [e for e in all_required_entities if e not in nodes]

        # Check required relationships
        all_required_rels = []
        for cat in ["citation", "structural", "procedural", "temporal", "semantic"]:
            all_required_rels.extend(REQUIRED_RELATIONSHIPS.get(cat, []))

        missing_rels = [r for r in all_required_rels if r not in relationships]

        # Scoring
        entity_coverage = (len(all_required_entities) - len(missing_entities)) / len(all_required_entities)
        rel_coverage = (len(all_required_rels) - len(missing_rels)) / len(all_required_rels)

        # Weighted score (entities: 60%, relationships: 40%)
        score = (entity_coverage * 0.6 + rel_coverage * 0.4) * 10

        strengths = []
        if entity_coverage >= 0.8:
            strengths.append(f"Good entity coverage: {entity_coverage*100:.0f}%")
        if rel_coverage >= 0.8:
            strengths.append(f"Good relationship coverage: {rel_coverage*100:.0f}%")

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "entity_coverage": f"{entity_coverage*100:.1f}%",
                "relationship_coverage": f"{rel_coverage*100:.1f}%",
                "present_entities": len(nodes),
                "present_relationships": len(relationships)
            },
            missing_components=missing_entities + [f"REL:{r}" for r in missing_rels],
            strengths=strengths
        )

    def _evaluate_rag_effectiveness(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate RAG architecture quality"""

        nodes = {node.get("label", "") for node in schema["nodes"] if node.get("label")}
        relationships = {rel.get("type", "") for rel in schema["relationships"] if rel.get("type")}
        indexes = schema.get("indexes", [])
        rag_config = schema.get("rag_configuration", {})

        missing = []
        strengths = []

        # Check for Chunk entity
        has_chunk = "Chunk" in nodes
        if not has_chunk:
            missing.append("Chunk entity for text chunking")

        # Check vector indexes
        vector_indexes = [idx for idx in indexes if idx.get("type") == "vector" or "embedding" in idx.get("property", "")]
        required_vector_indexes = RAG_REQUIREMENTS["vector_indexes"]

        if len(vector_indexes) < len(required_vector_indexes):
            missing.append(f"Vector indexes ({len(vector_indexes)}/{len(required_vector_indexes)})")
        else:
            strengths.append(f"All {len(vector_indexes)} vector indexes present")

        # Check retrieval relationships
        rag_rels = [r for r in REQUIRED_RELATIONSHIPS.get("rag", []) if r in relationships]
        if len(rag_rels) < len(REQUIRED_RELATIONSHIPS["rag"]):
            missing.append(f"RAG relationships ({len(rag_rels)}/{len(REQUIRED_RELATIONSHIPS['rag'])})")

        # Check metadata properties
        metadata_present = 0
        for node in schema["nodes"]:
            props = node.get("properties", {})
            if "relevance_score" in props or "context" in props:
                metadata_present += 1

        if metadata_present == 0:
            missing.append("Metadata properties (relevance_score, context)")

        # Check multi-granularity
        has_multi_granularity = (
            any("case" in node.get("label", "").lower() and "embedding" in str(node.get("properties", {})) for node in schema["nodes"]) and
            any("section" in node.get("label", "").lower() and "embedding" in str(node.get("properties", {})) for node in schema["nodes"]) and
            has_chunk
        )

        if not has_multi_granularity:
            missing.append("Multi-granularity embeddings (case/section/chunk)")
        else:
            strengths.append("Multi-granularity embeddings implemented")

        # Scoring
        score = 10.0
        score -= len(missing) * 1.0  # -1 point per missing component
        score = max(0, score)

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "has_chunk_entity": has_chunk,
                "vector_indexes": len(vector_indexes),
                "rag_relationships": len(rag_rels),
                "multi_granularity": has_multi_granularity,
                "rag_config": bool(rag_config)
            },
            missing_components=missing,
            strengths=strengths
        )

    def _evaluate_performance(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate performance optimization (indexes)"""

        indexes = schema.get("indexes", [])

        missing = []
        strengths = []

        # Check for composite indexes
        composite_indexes = [idx for idx in indexes if idx.get("type") == "composite"]
        if len(composite_indexes) < 2:
            missing.append(f"Composite indexes ({len(composite_indexes)}/3 recommended)")
        else:
            strengths.append(f"{len(composite_indexes)} composite indexes for common queries")

        # Check for single-property indexes
        single_indexes = [idx for idx in indexes if idx.get("type") == "single"]
        if len(single_indexes) < 3:
            missing.append(f"Single-property indexes ({len(single_indexes)}/4 recommended)")

        # Check for full-text indexes
        fulltext_indexes = [idx for idx in indexes if idx.get("type") == "fulltext"]
        if len(fulltext_indexes) < 1:
            missing.append("Full-text search indexes")
        else:
            strengths.append(f"{len(fulltext_indexes)} full-text indexes")

        # Check for vector indexes
        vector_indexes = [idx for idx in indexes if idx.get("type") == "vector" or "embedding" in idx.get("property", "")]
        if len(vector_indexes) < 2:
            missing.append(f"Vector indexes ({len(vector_indexes)}/3 recommended)")

        # Check critical indexes
        has_citation_index = any(
            "citation" in idx.get("property", "") or "citation" in idx.get("properties", [])
            for idx in indexes
        )
        if not has_citation_index:
            missing.append("Citation index (critical for lookups)")

        # Scoring
        total_indexes = len(indexes)
        recommended_indexes = 10  # Rough target

        score = min(10.0, (total_indexes / recommended_indexes) * 10)
        score = max(score, 5.0) if total_indexes >= 5 else score  # Minimum 5.0 if have at least 5 indexes

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "total_indexes": total_indexes,
                "composite": len(composite_indexes),
                "single": len(single_indexes),
                "fulltext": len(fulltext_indexes),
                "vector": len(vector_indexes)
            },
            missing_components=missing,
            strengths=strengths
        )

    def _evaluate_data_quality(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate data quality mechanisms"""

        missing = []
        strengths = []

        # Check provenance properties across nodes
        provenance_count = 0
        versioning_count = 0
        trust_count = 0

        for node in schema["nodes"]:
            props = node.get("properties", {})

            # Check provenance
            if "source" in props and "extracted_at" in props:
                provenance_count += 1

            # Check versioning
            if "version" in props and "updated_at" in props:
                versioning_count += 1

            # Check trust
            if "trust_score" in props:
                trust_count += 1

        total_nodes = len(schema["nodes"])

        if provenance_count < total_nodes * 0.5:
            missing.append(f"Provenance tracking (only {provenance_count}/{total_nodes} nodes)")
        else:
            strengths.append(f"Provenance on {provenance_count}/{total_nodes} nodes")

        if versioning_count < total_nodes * 0.3:
            missing.append(f"Versioning (only {versioning_count}/{total_nodes} nodes)")

        if trust_count < total_nodes * 0.3:
            missing.append(f"Trust scoring (only {trust_count}/{total_nodes} nodes)")
        else:
            strengths.append(f"Trust scores on {trust_count}/{total_nodes} nodes")

        # Check constraints
        constraints = schema.get("constraints", [])
        if len(constraints) < 2:
            missing.append(f"Constraints ({len(constraints)}/5 recommended)")
        else:
            strengths.append(f"{len(constraints)} constraints for data integrity")

        # Scoring
        provenance_score = (provenance_count / total_nodes) * 3.0
        versioning_score = (versioning_count / total_nodes) * 2.5
        trust_score = (trust_count / total_nodes) * 2.5
        constraint_score = min(2.0, len(constraints) * 0.4)

        score = provenance_score + versioning_score + trust_score + constraint_score

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "provenance_coverage": f"{provenance_count}/{total_nodes}",
                "versioning_coverage": f"{versioning_count}/{total_nodes}",
                "trust_coverage": f"{trust_count}/{total_nodes}",
                "constraints": len(constraints)
            },
            missing_components=missing,
            strengths=strengths
        )

    def _evaluate_cross_jurisdictional(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate cross-jurisdictional support"""

        nodes = {node.get("label", "") for node in schema["nodes"] if node.get("label")}
        relationships = {rel.get("type", "") for rel in schema["relationships"] if rel.get("type")}

        missing = []
        strengths = []

        # Check for jurisdiction/country support
        has_jurisdiction = any(
            "jurisdiction" in str(node.get("properties", {})).lower() or
            "country" in node.get("label", "").lower()
            for node in schema["nodes"]
        )

        if not has_jurisdiction:
            missing.append("Jurisdiction/Country entities or properties")
        else:
            strengths.append("Jurisdiction tracking present")

        # Check for court hierarchy
        has_court = "Court" in nodes
        if not has_court:
            missing.append("Court entity")

        # Check for cross-reference relationships
        has_cross_ref = any("CROSS_REFERENCE" in r or "COMPARES" in r for r in relationships)
        if not has_cross_ref:
            missing.append("Cross-reference relationships between jurisdictions")

        # Scoring
        score = 7.0  # Base score
        if has_jurisdiction:
            score += 2.0
        if has_court:
            score += 1.0
        if has_cross_ref:
            score += 0.0  # Not critical

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "has_jurisdiction": has_jurisdiction,
                "has_court": has_court,
                "has_cross_ref": has_cross_ref
            },
            missing_components=missing,
            strengths=strengths
        )

    def _evaluate_user_experience(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate user experience (naming, documentation)"""

        # Check node naming clarity
        clear_names = sum(
            1 for node in schema["nodes"]
            if node.get("label") and len(node.get("label", "")) <= 20 and node.get("label", "").replace("_", "").isalnum()
        )

        total_nodes = len(schema["nodes"])
        naming_score = (clear_names / total_nodes) * 5.0

        # Check documentation
        has_descriptions = sum(
            1 for node in schema["nodes"]
            if "description" in node and len(node["description"]) > 10
        )

        doc_score = (has_descriptions / total_nodes) * 5.0

        score = naming_score + doc_score

        strengths = []
        if naming_score >= 4.0:
            strengths.append("Clear, concise entity naming")
        if doc_score >= 3.0:
            strengths.append("Good documentation coverage")

        missing = []
        if doc_score < 2.0:
            missing.append(f"Entity descriptions ({has_descriptions}/{total_nodes})")

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "clear_names": f"{clear_names}/{total_nodes}",
                "has_descriptions": f"{has_descriptions}/{total_nodes}"
            },
            missing_components=missing,
            strengths=strengths
        )

    def _evaluate_scalability(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate scalability considerations"""

        indexes = schema.get("indexes", [])

        # Score based on indexing strategy
        score = 7.0  # Base score for reasonable schema

        if len(indexes) >= 8:
            score += 2.0  # Good indexing

        # Check for partitioning hints
        has_partitioning = any(
            "jurisdiction" in str(idx.get("properties", [])) or
            "year" in str(idx.get("properties", []))
            for idx in indexes
        )

        if has_partitioning:
            score += 1.0

        strengths = []
        if len(indexes) >= 8:
            strengths.append(f"Comprehensive indexing ({len(indexes)} indexes)")

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "indexes": len(indexes),
                "has_partitioning_hints": has_partitioning
            },
            missing_components=[],
            strengths=strengths
        )

    def _evaluate_extensibility(self, schema: SchemaDefinition) -> DimensionScore:
        """Evaluate extensibility (versioning, flexibility)"""

        # Check for versioning support
        has_versioning = any(
            "version" in str(node.get("properties", {}))
            for node in schema["nodes"]
        )

        # Check for flexible properties (JSON, metadata)
        has_metadata = any(
            "metadata" in str(node.get("properties", {})) or
            "properties" in str(node.get("properties", {}))
            for node in schema["nodes"]
        )

        score = 7.0  # Base score

        if has_versioning:
            score += 2.0

        if has_metadata:
            score += 1.0

        strengths = []
        if has_versioning:
            strengths.append("Versioning support for schema evolution")

        return DimensionScore(
            score=round(score, 1),
            max_score=10.0,
            details={
                "has_versioning": has_versioning,
                "has_metadata": has_metadata
            },
            missing_components=[],
            strengths=strengths
        )

    def _generate_improvements(self, dimension_scores: Dict[str, DimensionScore]) -> List[ImprovementSuggestion]:
        """Generate prioritized improvement suggestions"""

        suggestions = []

        for dimension, score_info in dimension_scores.items():
            score = score_info["score"]
            missing = score_info["missing_components"]

            if score < 8.0 and missing:
                # High priority if score < 7.0
                priority = "HIGH" if score < 7.0 else "MEDIUM"

                for component in missing[:2]:  # Top 2 missing components
                    suggestions.append(ImprovementSuggestion(
                        priority=priority,
                        dimension=dimension,
                        issue=f"Missing: {component}",
                        impact=f"Current score: {score:.1f}/10, blocking production readiness",
                        suggestion=f"Add {component} to improve {dimension}"
                    ))

        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        suggestions.sort(key=lambda x: (priority_order[x["priority"]], -dimension_scores[x["dimension"]]["score"]))

        return suggestions[:5]  # Top 5 suggestions

    def _identify_strengths(self, dimension_scores: Dict[str, DimensionScore]) -> List[str]:
        """Identify schema strengths"""

        strengths = []

        for dimension, score_info in dimension_scores.items():
            if score_info["score"] >= 8.5:
                strengths.append(f"{dimension}: {score_info['score']:.1f}/10 - Excellent")

            # Add specific strengths
            strengths.extend(score_info.get("strengths", []))

        return strengths[:10]  # Top 10 strengths


def create_schema_evaluator() -> SchemaEvaluator:
    """Factory function to create SchemaEvaluator instance"""
    return SchemaEvaluator()
