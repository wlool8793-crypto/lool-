"""
Main entry point for Schema Evolution System

Usage:
    python main.py                    # Run with defaults
    python main.py --iterations 10    # Custom max iterations
    python main.py --target 9.5       # Custom target score
    python main.py --implement        # Auto-implement in Neo4j
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from orchestrator import run_schema_evolution


def main():
    """Main entry point"""

    # Load environment variables
    load_dotenv()

    # Check for required env vars (Google Vertex AI Express with API Key)
    required_vars = ["VERTEX_AI_EXPRESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Error: Missing required environment variable for Google Vertex AI Express:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set VERTEX_AI_EXPRESS_KEY in .env file")
        print("Example: VERTEX_AI_EXPRESS_KEY=your_api_key_here")
        sys.exit(1)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Multi-Agent Schema Evolution System for Legal Knowledge Graphs"
    )

    parser.add_argument(
        "--target",
        type=float,
        default=9.0,
        help="Target overall score for convergence (default: 9.0)"
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=7,
        help="Maximum number of iterations (default: 7)"
    )

    parser.add_argument(
        "--implement",
        action="store_true",
        help="Auto-implement schema in Neo4j after convergence"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./schema_output",
        help="Output directory for results (default: ./schema_output)"
    )

    args = parser.parse_args()

    # Check Neo4j credentials if implementing
    if args.implement:
        neo4j_vars = ["NEO4J_URL", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
        missing_neo4j = [var for var in neo4j_vars if not os.getenv(var)]

        if missing_neo4j:
            print("⚠️  Warning: --implement requires Neo4j credentials:")
            for var in missing_neo4j:
                print(f"   - {var}")
            print("\nRunning without auto-implementation...")
            args.implement = False

    # Run evolution
    print("\n" + "="*80)
    print("🧠 LEGAL KNOWLEDGE GRAPH SCHEMA EVOLUTION SYSTEM")
    print("="*80)
    print(f"Target Score: {args.target}/10.0")
    print(f"Max Iterations: {args.iterations}")
    print(f"Auto-Implement: {args.implement}")
    print(f"Output Directory: {args.output}")
    print("="*80 + "\n")

    try:
        results = run_schema_evolution(
            target_score=args.target,
            max_iterations=args.iterations,
            auto_implement=args.implement,
            export_dir=args.output
        )

        print("\n" + "="*80)
        print("✅ SCHEMA EVOLUTION COMPLETE")
        print("="*80)
        print(f"Final Score: {results['final_evaluation']['overall_score']:.2f}/10.0")
        print(f"Iterations: {results['total_iterations']}")
        print(f"Duration: {results['total_duration_seconds']:.1f}s")
        print(f"Production Ready: {results['final_evaluation']['ready_for_production']}")
        print(f"\nResults exported to: {args.output}")
        print("="*80 + "\n")

        # Exit code based on production readiness
        if results['final_evaluation']['ready_for_production']:
            sys.exit(0)
        else:
            print("⚠️  Schema did not reach production readiness")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Evolution interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
