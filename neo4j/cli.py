#!/usr/bin/env python3
"""
Command Line Interface for Neo4j Legal Knowledge Graph

Usage:
    python cli.py extract-pdf --input cpc2.pdf --output cpc_data_auto.json
    python cli.py build-graph --data cpc_data.json
    python cli.py add-indian-cases --limit 30
    python cli.py visualize
    python cli.py stats
    python cli.py run-tests
"""
import argparse
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def command_extract_pdf(args):
    """Extract cases from PDF"""
    from utils.pdf_extractor import extract_pdf_to_json

    logger.info(f"Extracting cases from PDF: {args.input}")

    try:
        extract_pdf_to_json(args.input, args.output)
        logger.info(f"✓ Extraction complete: {args.output}")
        return 0
    except Exception as e:
        logger.error(f"✗ Extraction failed: {str(e)}")
        return 1


def command_build_graph(args):
    """Build Neo4j knowledge graph"""
    from build_graph import CPCGraphBuilder

    logger.info("Building Neo4j knowledge graph...")

    try:
        builder = CPCGraphBuilder()

        if args.clear:
            logger.warning("Clearing existing database...")
            builder.clear_database()

        builder.build_complete_graph()
        logger.info("✓ Graph building complete")
        return 0
    except Exception as e:
        logger.error(f"✗ Graph building failed: {str(e)}")
        return 1
    finally:
        if 'builder' in locals():
            builder.close()


def command_add_indian_cases(args):
    """Add Indian cases to graph"""
    from add_indian_cases import IndianCaseExtractor

    logger.info(f"Adding {args.limit} Indian cases to graph...")

    try:
        extractor = IndianCaseExtractor()
        cases = extractor.extract_cases_from_db(limit=args.limit)
        extractor.load_cases_to_neo4j(cases)
        extractor.get_statistics()
        logger.info("✓ Indian cases added successfully")
        return 0
    except Exception as e:
        logger.error(f"✗ Failed to add Indian cases: {str(e)}")
        return 1
    finally:
        if 'extractor' in locals():
            extractor.close()


def command_visualize(args):
    """Generate visualizations"""
    from visualize_graph import CPCGraphVisualizer

    logger.info("Generating graph visualizations...")

    try:
        visualizer = CPCGraphVisualizer()
        visualizer.visualize()
        logger.info("✓ Visualizations generated")
        return 0
    except Exception as e:
        logger.error(f"✗ Visualization failed: {str(e)}")
        return 1
    finally:
        if 'visualizer' in locals():
            visualizer.close()


def command_stats(args):
    """Show graph statistics"""
    from neo4j import GraphDatabase
    from dotenv import load_dotenv
    import os

    load_dotenv()

    NEO4J_URL = os.getenv("NEO4J_URL")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    if not all([NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD]):
        logger.error("Missing Neo4j credentials in environment")
        return 1

    logger.info("Fetching graph statistics...")

    try:
        driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

        with driver.session(database=NEO4J_DATABASE) as session:
            # Node counts by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)

            print("\n" + "="*60)
            print("KNOWLEDGE GRAPH STATISTICS")
            print("="*60)

            total_nodes = 0
            for record in result:
                label = record['label']
                count = record['count']
                if label:
                    print(f"  {label:20} {count:4} nodes")
                    total_nodes += count

            # Relationship counts
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(*) as count
                ORDER BY count DESC
                LIMIT 15
            """)

            print("\nTop Relationships:")
            total_rels = 0
            for record in result:
                rel_type = record['rel_type']
                count = record['count']
                print(f"  {rel_type:25} {count:4} relationships")
                total_rels += count

            total_rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
            total_rels = total_rel_result.single()['total']

            print(f"\n{'TOTAL':20} {total_nodes:4} nodes")
            print(f"{'TOTAL':20} {total_rels:4} relationships")
            print("="*60 + "\n")

        driver.close()
        return 0

    except Exception as e:
        logger.error(f"✗ Failed to fetch statistics: {str(e)}")
        return 1


def command_run_tests(args):
    """Run test suite"""
    import pytest

    logger.info("Running test suite...")

    pytest_args = ['-v']

    if args.coverage:
        pytest_args.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])

    if args.marker:
        pytest_args.extend(['-m', args.marker])

    if args.verbose:
        pytest_args.append('-vv')

    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        logger.info("✓ All tests passed")
    else:
        logger.error("✗ Some tests failed")

    return exit_code


def command_schema_evolution(args):
    """Run schema evolution system"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent / 'schema_evolution'))

    from schema_evolution.orchestrator import run_schema_evolution

    logger.info("Starting schema evolution system...")

    try:
        results = run_schema_evolution(
            target_score=args.target,
            max_iterations=args.iterations,
            auto_implement=args.implement,
            export_dir=args.output
        )

        if results['convergence_achieved']:
            logger.info(f"✓ Convergence achieved! Score: {results['final_evaluation']['overall_score']:.2f}/10")
        else:
            logger.warning(f"⚠ Max iterations reached. Best score: {results['final_evaluation']['overall_score']:.2f}/10")

        return 0

    except Exception as e:
        logger.error(f"✗ Schema evolution failed: {str(e)}")
        return 1


def command_build_llm_graph(args):
    """Build knowledge graph using LLM extraction with RAG"""
    from build_llm_graph import LLMGraphBuilder

    logger.info(f"Building LLM-powered knowledge graph with {args.model}...")

    enable_embeddings = not getattr(args, 'no_embeddings', False)
    builder = LLMGraphBuilder(llm_model=args.model, enable_embeddings=enable_embeddings)

    try:
        # Create schema constraints
        builder.create_schema_constraints()

        # Create vector indexes
        if enable_embeddings:
            builder.create_vector_indexes()

        # Process PDFs
        if not args.skip_pdfs and args.pdfs:
            pdf_files = [str(Path(pdf)) for pdf in args.pdfs]
            builder.process_pdfs(pdf_files)

        # Process text files
        if not args.skip_text and args.text_files:
            text_files = {}
            for text_file in args.text_files:
                file_path = Path(text_file)
                if file_path.exists():
                    file_type = "statute" if "cpc" in text_file.lower() else "order"
                    text_files[str(file_path)] = file_type

            if text_files:
                builder.process_text_files(text_files)

        # Process database
        if not args.skip_db and args.db_path:
            db_path = Path(args.db_path)
            if db_path.exists():
                builder.process_database(str(db_path), limit=args.db_limit)
            else:
                logger.warning(f"Database not found: {db_path}")

        # Generate embeddings for cases
        if enable_embeddings:
            builder.generate_case_embeddings()

        # Generate chunks
        if enable_embeddings and not getattr(args, 'skip_chunks', False):
            builder.generate_chunks()

        # Get statistics
        builder.get_statistics()

        logger.info("✓ LLM-powered knowledge graph built successfully!")
        return 0

    except Exception as e:
        logger.error(f"✗ LLM graph building failed: {str(e)}")
        return 1
    finally:
        builder.close()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Neo4j Legal Knowledge Graph CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract cases from PDF
  python cli.py extract-pdf --input cpc2.pdf --output cpc_data_auto.json

  # Build graph
  python cli.py build-graph

  # Add Indian cases
  python cli.py add-indian-cases --limit 50

  # Generate visualizations
  python cli.py visualize

  # Show statistics
  python cli.py stats

  # Run tests
  python cli.py run-tests --coverage

  # Schema evolution
  python cli.py schema-evolution --target 9.0 --iterations 7 --implement
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Extract PDF command
    extract_parser = subparsers.add_parser('extract-pdf', help='Extract cases from PDF')
    extract_parser.add_argument('--input', '-i', required=True, help='Input PDF file')
    extract_parser.add_argument('--output', '-o', default='cpc_data_auto.json', help='Output JSON file')
    extract_parser.set_defaults(func=command_extract_pdf)

    # Build graph command
    build_parser = subparsers.add_parser('build-graph', help='Build Neo4j knowledge graph')
    build_parser.add_argument('--clear', action='store_true', help='Clear existing database')
    build_parser.set_defaults(func=command_build_graph)

    # Add Indian cases command
    indian_parser = subparsers.add_parser('add-indian-cases', help='Add Indian cases to graph')
    indian_parser.add_argument('--limit', '-l', type=int, default=30, help='Number of cases to add')
    indian_parser.set_defaults(func=command_add_indian_cases)

    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate graph visualizations')
    viz_parser.set_defaults(func=command_visualize)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show graph statistics')
    stats_parser.set_defaults(func=command_stats)

    # Run tests command
    test_parser = subparsers.add_parser('run-tests', help='Run test suite')
    test_parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    test_parser.add_argument('--marker', '-m', help='Run tests with specific marker')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    test_parser.set_defaults(func=command_run_tests)

    # Schema evolution command
    schema_parser = subparsers.add_parser('schema-evolution', help='Run schema evolution system')
    schema_parser.add_argument('--target', type=float, default=9.0, help='Target score (default: 9.0)')
    schema_parser.add_argument('--iterations', type=int, default=7, help='Max iterations (default: 7)')
    schema_parser.add_argument('--implement', action='store_true', help='Auto-implement in Neo4j')
    schema_parser.add_argument('--output', default='./schema_output', help='Output directory')
    schema_parser.set_defaults(func=command_schema_evolution)

    # Build LLM graph command (NEW!)
    llm_parser = subparsers.add_parser('build-llm-graph', help='Build knowledge graph using LLM extraction with RAG')
    llm_parser.add_argument('--model', default='gpt-4-turbo', help='LLM model (gpt-4, gpt-4-turbo, gemini-2.5-pro)')
    llm_parser.add_argument('--pdfs', nargs='+', default=['cpc2.pdf'], help='PDF files to process')
    llm_parser.add_argument('--text-files', nargs='+', default=['cpc.txt', 'act.txt'], help='Text files to process')
    llm_parser.add_argument('--db-path', default='../data-collection/data/indiankanoon.db', help='SQLite database path')
    llm_parser.add_argument('--db-limit', type=int, default=50, help='Max database cases (default: 50)')
    llm_parser.add_argument('--skip-pdfs', action='store_true', help='Skip PDF processing')
    llm_parser.add_argument('--skip-text', action='store_true', help='Skip text file processing')
    llm_parser.add_argument('--skip-db', action='store_true', help='Skip database processing')
    llm_parser.add_argument('--no-embeddings', action='store_true', help='Disable embeddings generation')
    llm_parser.add_argument('--skip-chunks', action='store_true', help='Skip chunk generation for RAG')
    llm_parser.set_defaults(func=command_build_llm_graph)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
