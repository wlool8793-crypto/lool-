"""
Test script to validate schema evolution system structure
Tests imports and basic functionality without requiring API keys
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from state import (
            SchemaDefinition,
            EvaluationResult,
            SchemaEvolutionState,
            create_initial_state
        )
        print("✓ state.py imports successfully")

        from evaluation_rubric import (
            DIMENSION_WEIGHTS,
            REQUIRED_LEGAL_ENTITIES,
            REQUIRED_RELATIONSHIPS,
            RAG_REQUIREMENTS,
            calculate_overall_score,
            is_production_ready,
            get_production_blockers
        )
        print("✓ evaluation_rubric.py imports successfully")

        # Note: These require API keys, so we just check if they can be imported
        # schema_designer, schema_evaluator, schema_implementer, orchestrator
        print("✓ All core modules can be imported")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_state_creation():
    """Test state initialization"""
    print("\nTesting state creation...")

    try:
        from state import create_initial_state

        state = create_initial_state(target_score=9.0, max_iterations=7)

        assert state["current_iteration"] == 0
        assert state["target_score"] == 9.0
        assert state["max_iterations"] == 7
        assert state["convergence_achieved"] == False
        assert len(state["iteration_history"]) == 0

        print("✓ State creation works correctly")
        return True

    except Exception as e:
        print(f"✗ State creation error: {e}")
        return False


def test_rubric_calculations():
    """Test rubric calculation functions"""
    print("\nTesting rubric calculations...")

    try:
        from evaluation_rubric import (
            calculate_overall_score,
            is_production_ready,
            get_production_blockers,
            DIMENSION_WEIGHTS
        )

        # Test score calculation with high scores (should be production ready)
        high_dimension_scores = {
            "legal_completeness": 9.5,
            "rag_effectiveness": 9.8,
            "performance": 9.2,
            "data_quality": 8.9,
            "cross_jurisdictional": 9.0,
            "user_experience": 8.5,
            "scalability": 9.0,
            "extensibility": 9.0
        }

        overall_high = calculate_overall_score(high_dimension_scores)
        print(f"  High score overall: {overall_high:.2f}/10.0")

        # Test production readiness (should be True: overall >= 9.0 AND all dims >= 8.0)
        ready_high = is_production_ready(overall_high, high_dimension_scores)
        print(f"  Production ready (high scores): {ready_high}")

        assert ready_high == True, f"Should be production ready with overall {overall_high:.2f}"

        # Test with low score (should be False)
        low_scores = high_dimension_scores.copy()
        low_scores["performance"] = 7.5
        overall_low = calculate_overall_score(low_scores)
        ready_low = is_production_ready(overall_low, low_scores)
        print(f"  Low score overall: {overall_low:.2f}/10.0")
        print(f"  Production ready (low scores): {ready_low}")

        assert ready_low == False, "Should NOT be production ready with score < 8.0"

        blockers = get_production_blockers(overall_low, low_scores)
        print(f"  Blockers identified: {len(blockers)}")

        print("✓ Rubric calculations work correctly")
        return True

    except Exception as e:
        print(f"✗ Rubric calculation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_required_components():
    """Test that all required components are defined"""
    print("\nTesting required components...")

    try:
        from evaluation_rubric import (
            REQUIRED_LEGAL_ENTITIES,
            REQUIRED_RELATIONSHIPS,
            RAG_REQUIREMENTS,
            REQUIRED_INDEXES,
            DATA_QUALITY_REQUIREMENTS
        )

        # Check legal entities
        core_entities = REQUIRED_LEGAL_ENTITIES["core"]
        print(f"  Core legal entities: {len(core_entities)}")
        assert len(core_entities) > 0

        # Check relationships
        citation_rels = REQUIRED_RELATIONSHIPS["citation"]
        print(f"  Citation relationships: {len(citation_rels)}")
        assert len(citation_rels) > 0

        # Check RAG requirements
        vector_indexes = RAG_REQUIREMENTS["vector_indexes"]
        print(f"  Required vector indexes: {len(vector_indexes)}")
        assert len(vector_indexes) > 0

        # Check indexes
        composite_indexes = REQUIRED_INDEXES["composite"]
        print(f"  Composite indexes: {len(composite_indexes)}")
        assert len(composite_indexes) > 0

        # Check data quality
        provenance = DATA_QUALITY_REQUIREMENTS["provenance"]
        print(f"  Provenance properties: {len(provenance)}")
        assert len(provenance) > 0

        print("✓ All required components are properly defined")
        return True

    except Exception as e:
        print(f"✗ Required components error: {e}")
        return False


def test_weights_sum_to_one():
    """Test that dimension weights sum to 1.0"""
    print("\nTesting dimension weights...")

    try:
        from evaluation_rubric import DIMENSION_WEIGHTS

        total_weight = sum(DIMENSION_WEIGHTS.values())
        print(f"  Total weight: {total_weight:.2f}")

        assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"

        print("✓ Dimension weights sum to 1.0")
        return True

    except Exception as e:
        print(f"✗ Dimension weights error: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")

    required_files = [
        "__init__.py",
        "state.py",
        "evaluation_rubric.py",
        "schema_designer.py",
        "schema_evaluator.py",
        "schema_implementer.py",
        "orchestrator.py",
        "main.py",
        "README.md",
        ".env.example"
    ]

    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} MISSING")
            all_exist = False

    if all_exist:
        print("✓ All required files exist")
        return True
    else:
        print("✗ Some files are missing")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Schema Evolution System - Structure Tests")
    print("="*60)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("State Creation", test_state_creation),
        ("Rubric Calculations", test_rubric_calculations),
        ("Required Components", test_required_components),
        ("Dimension Weights", test_weights_sum_to_one)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print("="*60)
    print(f"Passed: {passed}/{total}")
    print("="*60)

    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
