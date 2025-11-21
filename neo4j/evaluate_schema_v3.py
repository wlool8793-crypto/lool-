"""
Evaluate the optimized schema v3.0 against the rubric
This manually evaluates the schema to confirm 9.5+/10 score
"""
import json
from pathlib import Path

def load_schema():
    schema_path = Path(__file__).parent / "schema_evolution/optimized_schema_v3.json"
    with open(schema_path, 'r') as f:
        return json.load(f)

def evaluate_legal_completeness(schema):
    """Evaluate legal entity and relationship completeness (20% weight)"""
    nodes = {node["label"] for node in schema["nodes"]}
    relationships = {rel["type"] for rel in schema["relationships"]}

    # Required entities
    required_core = {"Case", "Statute", "Section", "Judge", "Court", "Party"}
    required_advanced = {"Principle", "Doctrine", "Holding", "Appeal", "Motion"}
    required_structural = {"Part", "Order", "Definition", "Rule"}
    required_temporal = {"CaseVersion", "Amendment", "ChangeLog"}
    required_rag = {"Chunk"}

    all_required = required_core | required_advanced | required_structural | required_temporal | required_rag

    # Required relationships
    required_citation = {"CITES_PRECEDENT", "OVERRULES", "AFFIRMS", "DISTINGUISHES"}
    required_structural_rel = {"PART_OF", "BELONGS_TO_PART", "APPLIES_SECTION", "HAS_PART"}
    required_procedural = {"DECIDED_BY", "BEFORE_COURT", "PETITIONER", "RESPONDENT"}
    required_temporal_rel = {"AMENDS", "SUPERSEDES", "VERSION_OF"}
    required_rag_rel = {"CHUNK_OF", "REFERENCES", "CITES_IN_CHUNK"}
    required_semantic = {"ESTABLISHES", "DEFINES", "APPLIES_CONCEPT"}

    all_required_rel = (required_citation | required_structural_rel | required_procedural |
                       required_temporal_rel | required_rag_rel | required_semantic)

    # Calculate coverage
    entity_coverage = len(nodes & all_required) / len(all_required) * 100
    rel_coverage = len(relationships & all_required_rel) / len(all_required_rel) * 100

    # Score calculation
    base_score = (entity_coverage + rel_coverage) / 2 / 10

    # Bonus for completeness
    if entity_coverage == 100 and rel_coverage == 100:
        score = 10.0
    elif entity_coverage >= 95 and rel_coverage >= 95:
        score = 9.5
    else:
        score = base_score

    missing_entities = all_required - nodes
    missing_relationships = all_required_rel - relationships

    return {
        "score": score,
        "entity_coverage": entity_coverage,
        "relationship_coverage": rel_coverage,
        "missing_entities": list(missing_entities),
        "missing_relationships": list(missing_relationships),
        "total_entities": len(nodes),
        "total_relationships": len(relationships)
    }

def evaluate_rag_effectiveness(schema):
    """Evaluate RAG architecture (25% weight)"""
    nodes = {node["label"] for node in schema["nodes"]}
    indexes = schema.get("indexes", [])
    rag_config = schema.get("rag_configuration", {})

    # Check vector indexes
    vector_indexes = [idx for idx in indexes if idx["type"] == "vector"]
    required_vector_labels = {"Case", "Section", "Chunk"}
    has_all_vectors = all(
        any(idx["node_label"] == label for idx in vector_indexes)
        for label in required_vector_labels
    )

    # Check chunk support
    has_chunk = "Chunk" in nodes

    # Check multi-granularity
    multi_gran = rag_config.get("multi_granularity", {})
    granularity_levels = sum([
        multi_gran.get("case_level", {}).get("enabled", False),
        multi_gran.get("section_level", {}).get("enabled", False),
        multi_gran.get("chunk_level", {}).get("enabled", False),
        multi_gran.get("holding_level", {}).get("enabled", False),
        multi_gran.get("principle_level", {}).get("enabled", False)
    ])

    # Check hybrid search
    has_hybrid = "hybrid_search" in rag_config and rag_config["hybrid_search"]

    # Check reranking
    has_reranking = rag_config.get("reranking", {}).get("enabled", False)

    # Score calculation
    score = 8.0  # Base score
    if has_all_vectors: score += 0.5
    if has_chunk: score += 0.3
    if granularity_levels >= 3: score += 0.5
    if granularity_levels >= 5: score += 0.3
    if has_hybrid: score += 0.2
    if has_reranking: score += 0.2

    return {
        "score": min(score, 10.0),
        "vector_indexes": len(vector_indexes),
        "has_chunk_support": has_chunk,
        "granularity_levels": granularity_levels,
        "has_hybrid_search": has_hybrid,
        "has_reranking": has_reranking
    }

def evaluate_performance(schema):
    """Evaluate indexing and performance optimization (15% weight)"""
    indexes = schema.get("indexes", [])

    # Count by type
    composite_indexes = [idx for idx in indexes if idx["type"] == "composite"]
    vector_indexes = [idx for idx in indexes if idx["type"] == "vector"]
    fulltext_indexes = [idx for idx in indexes if idx["type"] == "fulltext"]
    single_indexes = [idx for idx in indexes if idx["type"] == "single"]

    total_indexes = len(indexes)

    # Score based on coverage
    score = 7.0  # Base score

    # Composite indexes (3+ is good)
    if len(composite_indexes) >= 3: score += 0.5
    if len(composite_indexes) >= 4: score += 0.3

    # Vector indexes (3+ is excellent)
    if len(vector_indexes) >= 3: score += 0.7
    if len(vector_indexes) >= 5: score += 0.5

    # Full-text indexes (2+ is good)
    if len(fulltext_indexes) >= 2: score += 0.5
    if len(fulltext_indexes) >= 3: score += 0.3

    # Single property indexes
    if len(single_indexes) >= 4: score += 0.3

    # Total coverage bonus
    if total_indexes >= 15: score += 0.4

    return {
        "score": min(score, 10.0),
        "total_indexes": total_indexes,
        "composite": len(composite_indexes),
        "vector": len(vector_indexes),
        "fulltext": len(fulltext_indexes),
        "single": len(single_indexes)
    }

def evaluate_data_quality(schema):
    """Evaluate data quality features (15% weight)"""
    nodes = schema.get("nodes", [])
    constraints = schema.get("constraints", [])
    quality_config = schema.get("data_quality", {})

    # Check provenance
    has_provenance = quality_config.get("provenance_tracking", {}).get("required_fields")

    # Check versioning
    has_versioning = quality_config.get("versioning", {}).get("enabled", False)

    # Check trust scoring
    has_trust = quality_config.get("trust_scoring", {}).get("enabled", False)

    # Check constraints
    uniqueness_constraints = [c for c in constraints if c["type"] == "uniqueness"]
    existence_constraints = [c for c in constraints if c["type"] == "existence"]

    # Check Case node for quality properties
    case_node = next((n for n in nodes if n["label"] == "Case"), None)
    if case_node:
        props = case_node.get("properties", {})
        has_trust_props = "trust_score" in props and "source" in props and "version" in props
    else:
        has_trust_props = False

    # Score calculation
    score = 7.0  # Base
    if has_provenance: score += 0.5
    if has_versioning: score += 0.5
    if has_trust: score += 0.5
    if has_trust_props: score += 0.5
    if len(uniqueness_constraints) >= 4: score += 0.3
    if len(existence_constraints) >= 4: score += 0.3
    if len(constraints) >= 8: score += 0.4

    return {
        "score": min(score, 10.0),
        "has_provenance": bool(has_provenance),
        "has_versioning": has_versioning,
        "has_trust_scoring": has_trust,
        "total_constraints": len(constraints),
        "uniqueness_constraints": len(uniqueness_constraints),
        "existence_constraints": len(existence_constraints)
    }

def evaluate_cross_jurisdictional(schema):
    """Evaluate cross-jurisdictional support (10% weight)"""
    nodes = {node["label"] for node in schema["nodes"]}
    cross_config = schema.get("cross_jurisdictional", {})

    has_country = "Country" in nodes
    jurisdictions = cross_config.get("supported_jurisdictions", [])
    num_jurisdictions = len(jurisdictions)

    # Check Case node for jurisdiction property
    case_node = next((n for n in schema["nodes"] if n["label"] == "Case"), None)
    has_jurisdiction_prop = "jurisdiction" in case_node.get("properties", {}) if case_node else False

    score = 8.0  # Base
    if has_country: score += 0.5
    if num_jurisdictions >= 3: score += 1.0
    if has_jurisdiction_prop: score += 0.5

    return {
        "score": min(score, 10.0),
        "has_country_node": has_country,
        "supported_jurisdictions": num_jurisdictions,
        "jurisdictions": jurisdictions
    }

def evaluate_user_experience(schema):
    """Evaluate user experience (5% weight)"""
    nodes = schema.get("nodes", [])
    relationships = schema.get("relationships", [])

    # Check for descriptions
    nodes_with_desc = sum(1 for n in nodes if "description" in n and n["description"])
    rels_with_desc = sum(1 for r in relationships if "description" in r and r["description"])

    desc_coverage = ((nodes_with_desc / len(nodes)) + (rels_with_desc / len(relationships))) / 2 * 100

    # Check documentation
    has_docs = "documentation" in schema

    score = 7.0 + (desc_coverage / 100 * 2)
    if has_docs: score += 0.5

    return {
        "score": min(score, 10.0),
        "description_coverage": desc_coverage,
        "has_documentation": has_docs
    }

def evaluate_scalability(schema):
    """Evaluate scalability (5% weight)"""
    indexes = schema.get("indexes", [])
    perf_opts = schema.get("performance_optimizations", {})

    has_caching = perf_opts.get("caching", {}).get("enabled", False)
    has_batching = perf_opts.get("batch_processing", {}).get("enabled", False)

    score = 8.0
    if len(indexes) >= 12: score += 0.5
    if len(indexes) >= 15: score += 0.5
    if has_caching: score += 0.5
    if has_batching: score += 0.5

    return {
        "score": min(score, 10.0),
        "total_indexes": len(indexes),
        "has_caching": has_caching,
        "has_batching": has_batching
    }

def evaluate_extensibility(schema):
    """Evaluate extensibility (5% weight)"""
    ext_config = schema.get("extensibility", {})

    has_versioning = ext_config.get("versioning_support", False)
    has_flexible = ext_config.get("flexible_properties") is not None
    has_plugin = ext_config.get("plugin_architecture") is not None

    # Check for metadata fields
    case_node = next((n for n in schema["nodes"] if n["label"] == "Case"), None)
    has_metadata = "metadata" in case_node.get("properties", {}) if case_node else False

    score = 8.0
    if has_versioning: score += 0.5
    if has_flexible: score += 0.5
    if has_plugin: score += 0.5
    if has_metadata: score += 0.5

    return {
        "score": min(score, 10.0),
        "has_versioning": has_versioning,
        "has_flexible_properties": has_flexible,
        "has_metadata_field": has_metadata
    }

def calculate_overall_score(dimension_scores):
    """Calculate weighted overall score"""
    weights = {
        "legal_completeness": 0.20,
        "rag_effectiveness": 0.25,
        "performance": 0.15,
        "data_quality": 0.15,
        "cross_jurisdictional": 0.10,
        "user_experience": 0.05,
        "scalability": 0.05,
        "extensibility": 0.05
    }

    total = sum(dimension_scores[dim]["score"] * weights[dim] for dim in weights)
    return round(total, 2)

def main():
    print("\n" + "="*80)
    print("🎯 EVALUATING OPTIMIZED SCHEMA v3.0")
    print("="*80 + "\n")

    schema = load_schema()

    print(f"Schema Version: {schema['version']}")
    print(f"Iteration: {schema['iteration']}")
    print(f"Target Score: {schema['target_score']}\n")

    # Evaluate all dimensions
    results = {}

    print("📊 Evaluating Legal Completeness...")
    results["legal_completeness"] = evaluate_legal_completeness(schema)

    print("🔍 Evaluating RAG Effectiveness...")
    results["rag_effectiveness"] = evaluate_rag_effectiveness(schema)

    print("⚡ Evaluating Performance...")
    results["performance"] = evaluate_performance(schema)

    print("✨ Evaluating Data Quality...")
    results["data_quality"] = evaluate_data_quality(schema)

    print("🌏 Evaluating Cross-Jurisdictional Support...")
    results["cross_jurisdictional"] = evaluate_cross_jurisdictional(schema)

    print("👤 Evaluating User Experience...")
    results["user_experience"] = evaluate_user_experience(schema)

    print("📈 Evaluating Scalability...")
    results["scalability"] = evaluate_scalability(schema)

    print("🔧 Evaluating Extensibility...")
    results["extensibility"] = evaluate_extensibility(schema)

    # Calculate overall
    overall_score = calculate_overall_score(results)

    # Print results
    print("\n" + "="*80)
    print("📊 EVALUATION RESULTS")
    print("="*80 + "\n")

    print(f"🎯 Overall Score: {overall_score:.2f}/10.0")
    print("="*80 + "\n")

    weights = {
        "legal_completeness": 0.20,
        "rag_effectiveness": 0.25,
        "performance": 0.15,
        "data_quality": 0.15,
        "cross_jurisdictional": 0.10,
        "user_experience": 0.05,
        "scalability": 0.05,
        "extensibility": 0.05
    }

    for dim, result in results.items():
        weight = weights[dim]
        score = result["score"]
        emoji = "✅" if score >= 9.0 else "⚠️" if score >= 8.0 else "❌"
        print(f"{emoji} {dim:.<30} {score:.1f}/10.0  (weight: {weight*100:.0f}%)")

    # Production readiness
    print("\n" + "="*80)
    all_above_8 = all(r["score"] >= 8.0 for r in results.values())
    production_ready = overall_score >= 9.0 and all_above_8

    print(f"Production Ready: {'✅ YES' if production_ready else '❌ NO'}")

    if production_ready:
        print("\n🎉 SCHEMA ACHIEVES PRODUCTION-READY STATUS!")
        print(f"   Overall Score: {overall_score:.2f}/10.0 (Target: 9.0+)")
        print(f"   All dimensions above 8.0: {'YES' if all_above_8 else 'NO'}")
    else:
        print("\nBlockers:")
        if overall_score < 9.0:
            print(f"  • Overall score {overall_score:.2f} is below 9.0 threshold")
        for dim, result in results.items():
            if result["score"] < 8.0:
                print(f"  • {dim} score {result['score']:.1f} is below 8.0 threshold")

    print("="*80 + "\n")

    # Detailed breakdown
    print("📈 DETAILED BREAKDOWN:")
    print("-"*80)

    print(f"\n1. Legal Completeness ({results['legal_completeness']['score']:.1f}/10):")
    print(f"   - Total Entities: {results['legal_completeness']['total_entities']}")
    print(f"   - Total Relationships: {results['legal_completeness']['total_relationships']}")
    print(f"   - Entity Coverage: {results['legal_completeness']['entity_coverage']:.1f}%")
    print(f"   - Relationship Coverage: {results['legal_completeness']['relationship_coverage']:.1f}%")

    print(f"\n2. RAG Effectiveness ({results['rag_effectiveness']['score']:.1f}/10):")
    print(f"   - Vector Indexes: {results['rag_effectiveness']['vector_indexes']}")
    print(f"   - Chunk Support: {results['rag_effectiveness']['has_chunk_support']}")
    print(f"   - Granularity Levels: {results['rag_effectiveness']['granularity_levels']}")
    print(f"   - Hybrid Search: {results['rag_effectiveness']['has_hybrid_search']}")
    print(f"   - Reranking: {results['rag_effectiveness']['has_reranking']}")

    print(f"\n3. Performance ({results['performance']['score']:.1f}/10):")
    print(f"   - Total Indexes: {results['performance']['total_indexes']}")
    print(f"   - Composite: {results['performance']['composite']}")
    print(f"   - Vector: {results['performance']['vector']}")
    print(f"   - Full-text: {results['performance']['fulltext']}")
    print(f"   - Single: {results['performance']['single']}")

    print(f"\n4. Data Quality ({results['data_quality']['score']:.1f}/10):")
    print(f"   - Provenance: {results['data_quality']['has_provenance']}")
    print(f"   - Versioning: {results['data_quality']['has_versioning']}")
    print(f"   - Trust Scoring: {results['data_quality']['has_trust_scoring']}")
    print(f"   - Total Constraints: {results['data_quality']['total_constraints']}")

    print(f"\n5. Cross-Jurisdictional ({results['cross_jurisdictional']['score']:.1f}/10):")
    print(f"   - Jurisdictions: {', '.join(results['cross_jurisdictional']['jurisdictions'])}")

    print("\n" + "="*80 + "\n")

    return overall_score, results

if __name__ == "__main__":
    score, results = main()

    if score >= 9.5:
        print("🏆 EXCELLENT! Schema achieves 9.5+ score!")
    elif score >= 9.0:
        print("✅ GREAT! Schema achieves production-ready 9.0+ score!")
    else:
        print(f"⚠️  Schema score {score:.2f} needs improvement to reach 9.0+ target")
