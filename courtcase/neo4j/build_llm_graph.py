"""
Build LLM-Powered Knowledge Graph from Multiple Data Sources

Processes PDFs, text files, and SQLite database using LLM extraction
and populates Neo4j following the optimized schema v3.0.
"""
import json
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
from tqdm import tqdm

from llm_extractor import LLMExtractor
from utils.error_handling import neo4j_retry, Neo4jTransactionContext
from utils.monitoring import init_monitoring, global_monitor
from utils.embeddings_generator import (
    EmbeddingsGenerator,
    Neo4jEmbeddingsLoader,
    create_chunks_with_embeddings
)

# Initialize logging
init_monitoring(log_level="INFO", log_file="logs/llm_graph_build.log")
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Neo4j Configuration
NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Validate environment
if not all([NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("Missing Neo4j credentials in .env")


class LLMGraphBuilder:
    """
    Build knowledge graph using LLM extraction

    Features:
    - Multi-source data processing (PDFs, text files, SQLite)
    - LLM-powered entity extraction
    - Optimized schema v3.0 compliance
    - RAG components (embeddings, chunks)
    - Cross-jurisdictional linking
    """

    def __init__(self, llm_model: str = "gpt-4-turbo", enable_embeddings: bool = True):
        """
        Initialize graph builder

        Args:
            llm_model: LLM model for extraction ('gpt-4', 'gpt-4-turbo', 'gemini-2.5-pro')
            enable_embeddings: Whether to generate embeddings for RAG
        """
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.extractor = LLMExtractor(model=llm_model)
        self.schema = self._load_schema()
        self.enable_embeddings = enable_embeddings

        # Initialize embeddings components
        if enable_embeddings:
            try:
                self.embeddings_gen = EmbeddingsGenerator()
                self.embeddings_loader = Neo4jEmbeddingsLoader(self.driver)
                logger.info("✓ Embeddings generator initialized")
            except Exception as e:
                logger.warning(f"Embeddings disabled: {str(e)}")
                self.enable_embeddings = False

        logger.info(f"Initialized LLM Graph Builder with {llm_model}")

    def _load_schema(self) -> Dict:
        """Load optimized schema v3.0"""
        schema_path = Path(__file__).parent / "schema_evolution" / "optimized_schema_v3.json"

        with open(schema_path) as f:
            schema = json.load(f)

        logger.info(f"Loaded schema {schema['version']}")
        return schema

    @neo4j_retry(max_attempts=3)
    def create_schema_constraints(self):
        """Create uniqueness constraints from schema"""
        logger.info("Creating schema constraints...")

        constraints = [
            ("case_id", "CREATE CONSTRAINT case_id_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE"),
            ("citation", "CREATE CONSTRAINT case_citation_unique IF NOT EXISTS FOR (c:Case) REQUIRE c.citation IS UNIQUE"),
            ("section_id", "CREATE CONSTRAINT section_id_unique IF NOT EXISTS FOR (s:Section) REQUIRE s.section_id IS UNIQUE"),
            ("statute_id", "CREATE CONSTRAINT statute_id_unique IF NOT EXISTS FOR (st:Statute) REQUIRE st.statute_id IS UNIQUE"),
            ("judge_id", "CREATE CONSTRAINT judge_id_unique IF NOT EXISTS FOR (j:Judge) REQUIRE j.judge_id IS UNIQUE"),
            ("court_id", "CREATE CONSTRAINT court_id_unique IF NOT EXISTS FOR (c:Court) REQUIRE c.court_id IS UNIQUE"),
        ]

        with self.driver.session(database=NEO4J_DATABASE) as session:
            for name, cypher in constraints:
                try:
                    session.run(cypher)
                    logger.debug(f"Created constraint: {name}")
                except Exception as e:
                    logger.debug(f"Constraint {name} may already exist: {str(e)}")

        logger.info("✓ Schema constraints created")

    def process_pdfs(self, pdf_files: List[str]):
        """
        Process PDF files with LLM extraction

        Args:
            pdf_files: List of PDF file paths
        """
        logger.info(f"Processing {len(pdf_files)} PDF files...")

        all_cases = []

        for pdf_file in tqdm(pdf_files, desc="Extracting PDFs"):
            with global_monitor.track(f"pdf_extraction_{Path(pdf_file).name}"):
                cases = self.extractor.extract_from_pdf(pdf_file)
                all_cases.extend(cases)

        logger.info(f"Extracted {len(all_cases)} cases from PDFs")

        # Load into Neo4j
        self._load_cases_to_neo4j(all_cases, source_type="pdf")

    def process_text_files(self, text_files: Dict[str, str]):
        """
        Process text files (statutes, acts)

        Args:
            text_files: Dict of {file_path: file_type}
        """
        logger.info(f"Processing {len(text_files)} text files...")

        for text_file, file_type in text_files.items():
            with global_monitor.track(f"text_extraction_{Path(text_file).name}"):
                result = self.extractor.extract_from_text_file(text_file, file_type=file_type)

                if file_type == "statute":
                    self._load_statute_to_neo4j(result)
                elif file_type == "order":
                    self._load_orders_to_neo4j(result)

        logger.info("✓ Text files processed")

    def process_database(self, db_path: str, limit: Optional[int] = None):
        """
        Process Indian Kanoon SQLite database

        Args:
            db_path: Path to SQLite database
            limit: Maximum number of cases to process
        """
        logger.info(f"Processing database: {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        query = """
            SELECT id, title, court, full_text, citation, snippet, court_name, year, case_date
            FROM legal_cases
            WHERE full_text IS NOT NULL AND LENGTH(full_text) > 5000
            ORDER BY LENGTH(full_text) DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        cursor = conn.cursor()
        cursor.execute(query)

        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} cases in database")

        enhanced_cases = []

        for row in tqdm(rows, desc="Enhancing DB cases with LLM"):
            case_record = dict(row)

            with global_monitor.track("db_case_llm_enhancement"):
                enhanced = self.extractor.extract_from_database_case(case_record)
                enhanced_cases.append(enhanced)

        conn.close()

        # Load into Neo4j
        self._load_cases_to_neo4j(enhanced_cases, source_type="database")

    def _load_cases_to_neo4j(self, cases: List[Dict], source_type: str):
        """Load cases into Neo4j following schema v3.0"""
        logger.info(f"Loading {len(cases)} cases to Neo4j (source: {source_type})...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            for case in tqdm(cases, desc="Loading cases"):
                with Neo4jTransactionContext(session, "load_case") as tx:
                    # Create Case node
                    case_props = self._prepare_case_properties(case)

                    tx.run("""
                        MERGE (c:Case {case_id: $case_id})
                        SET c += $properties
                    """, case_id=case_props["case_id"], properties=case_props)

                    # Create Judges
                    for judge in case.get("judges", case.get("llm_judges", [])):
                        if isinstance(judge, dict):
                            judge_name = judge.get("name")
                        else:
                            judge_name = str(judge)

                        if judge_name:
                            judge_id = self._generate_id(judge_name)
                            tx.run("""
                                MERGE (j:Judge {judge_id: $judge_id})
                                SET j.name = $name,
                                    j.title = $title
                                WITH j
                                MATCH (c:Case {case_id: $case_id})
                                MERGE (c)-[:DECIDED_BY]->(j)
                            """, judge_id=judge_id, name=judge_name,
                                 title=judge.get("title", "Justice") if isinstance(judge, dict) else "Justice",
                                 case_id=case_props["case_id"])

                    # Create Court
                    court_name = case.get("court")
                    if court_name:
                        court_id = self._generate_id(court_name)
                        tx.run("""
                            MERGE (court:Court {court_id: $court_id})
                            SET court.name = $name
                            WITH court
                            MATCH (c:Case {case_id: $case_id})
                            MERGE (c)-[:BEFORE_COURT]->(court)
                        """, court_id=court_id, name=court_name, case_id=case_props["case_id"])

                    # Create Parties
                    parties = case.get("parties", {})
                    for petitioner in parties.get("petitioners", []):
                        party_id = self._generate_id(petitioner)
                        tx.run("""
                            MERGE (p:Party {party_id: $party_id})
                            SET p.name = $name, p.role = 'Petitioner'
                            WITH p
                            MATCH (c:Case {case_id: $case_id})
                            MERGE (c)-[:PETITIONER]->(p)
                        """, party_id=party_id, name=petitioner, case_id=case_props["case_id"])

                    for respondent in parties.get("respondents", []):
                        party_id = self._generate_id(respondent)
                        tx.run("""
                            MERGE (p:Party {party_id: $party_id})
                            SET p.name = $name, p.role = 'Respondent'
                            WITH p
                            MATCH (c:Case {case_id: $case_id})
                            MERGE (c)-[:RESPONDENT]->(p)
                        """, party_id=party_id, name=respondent, case_id=case_props["case_id"])

                    # Create Sections
                    for section in case.get("sections", case.get("llm_sections", [])):
                        if isinstance(section, dict):
                            section_id_str = section.get("section_id")
                            statute = section.get("statute", "Unknown")
                            description = section.get("description", "")
                        else:
                            section_id_str = str(section)
                            statute = "Unknown"
                            description = ""

                        if section_id_str:
                            section_id = self._generate_id(section_id_str)
                            tx.run("""
                                MERGE (s:Section {section_id: $section_id})
                                SET s.section_number = $section_number,
                                    s.statute = $statute,
                                    s.description = $description
                                WITH s
                                MATCH (c:Case {case_id: $case_id})
                                MERGE (c)-[:APPLIES_SECTION]->(s)
                            """, section_id=section_id, section_number=section_id_str,
                                 statute=statute, description=description, case_id=case_props["case_id"])

                    # Create Principles
                    for principle in case.get("principles", case.get("llm_principles", [])):
                        if isinstance(principle, dict):
                            principle_name = principle.get("name")
                            description = principle.get("description", "")
                            category = principle.get("category", "Legal Principle")
                        else:
                            principle_name = str(principle)
                            description = ""
                            category = "Legal Principle"

                        if principle_name:
                            principle_id = self._generate_id(principle_name)
                            tx.run("""
                                MERGE (p:Principle {principle_id: $principle_id})
                                SET p.name = $name,
                                    p.description = $description,
                                    p.category = $category
                                WITH p
                                MATCH (c:Case {case_id: $case_id})
                                MERGE (c)-[:ESTABLISHES]->(p)
                            """, principle_id=principle_id, name=principle_name,
                                 description=description, category=category, case_id=case_props["case_id"])

        logger.info(f"✓ Loaded {len(cases)} cases to Neo4j")

    def _prepare_case_properties(self, case: Dict) -> Dict:
        """Prepare case properties following schema v3.0"""
        case_id = case.get("case_id", self._generate_id(case.get("title", case.get("citation", "unknown"))))

        return {
            "case_id": case_id,
            "citation": case.get("citation", ""),
            "title": case.get("title", case.get("name", "")),
            "date": case.get("date", case.get("case_date", "")),
            "year": case.get("year"),
            "jurisdiction": case.get("jurisdiction", "Bangladesh"),
            "case_type": case.get("case_type", "Unknown"),
            "full_text": case.get("full_text", "")[:10000],  # Limit to 10k chars
            "summary": case.get("summary", case.get("llm_summary", case.get("snippet", ""))),
            "holding": case.get("holding", case.get("llm_holding", "")),
            "facts": case.get("facts", case.get("llm_facts", "")),
            "reasoning": case.get("reasoning", case.get("llm_reasoning", "")),
            "outcome": case.get("outcome", ""),
            "trust_score": case.get("trust_score", case.get("confidence_score", 0.75)),
            "authority_level": case.get("authority_level", case.get("court_type", "Unknown")),
            "source": case.get("source", ""),
            "extracted_at": case.get("extracted_at", datetime.now().isoformat()),
            "extracted_by": case.get("extracted_by", "llm_extractor"),
            "confidence_score": case.get("confidence_score", 0.75),
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _load_statute_to_neo4j(self, statute_data: Dict):
        """Load statute and sections to Neo4j"""
        logger.info("Loading statute to Neo4j...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            with Neo4jTransactionContext(session, "load_statute") as tx:
                # Create Statute node
                statute = statute_data.get("statute", {})
                statute_id = self._generate_id(statute.get("name", "Unknown"))

                tx.run("""
                    MERGE (st:Statute {statute_id: $statute_id})
                    SET st.name = $name,
                        st.short_name = $short_name,
                        st.country = $country,
                        st.year = $year
                """, statute_id=statute_id,
                     name=statute.get("name", ""),
                     short_name=statute.get("short_name", ""),
                     country=statute.get("country", "Bangladesh"),
                     year=statute.get("year"))

                # Create Sections
                for section in statute_data.get("sections", []):
                    section_id = self._generate_id(section.get("section_id", ""))

                    tx.run("""
                        MERGE (s:Section {section_id: $section_id})
                        SET s.section_number = $section_number,
                            s.title = $title,
                            s.description = $description,
                            s.statute = $statute_name
                        WITH s
                        MATCH (st:Statute {statute_id: $statute_id})
                        MERGE (s)-[:PART_OF]->(st)
                    """, section_id=section_id,
                         section_number=section.get("section_id", ""),
                         title=section.get("title", ""),
                         description=section.get("description", ""),
                         statute_name=statute.get("name", ""),
                         statute_id=statute_id)

        logger.info("✓ Statute loaded")

    def _load_orders_to_neo4j(self, orders_data: Dict):
        """Load orders and rules to Neo4j"""
        logger.info("Loading orders to Neo4j...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            for order in orders_data.get("orders", []):
                with Neo4jTransactionContext(session, "load_order") as tx:
                    order_id = self._generate_id(order.get("order_id", ""))

                    tx.run("""
                        MERGE (o:Order {order_id: $order_id})
                        SET o.order_number = $order_number,
                            o.title = $title
                    """, order_id=order_id,
                         order_number=order.get("order_id", ""),
                         title=order.get("title", ""))

                    # Create Rules
                    for rule in order.get("rules", []):
                        rule_id = self._generate_id(f"{order.get('order_id')}_{rule.get('rule_number')}")

                        tx.run("""
                            MERGE (r:Rule {rule_id: $rule_id})
                            SET r.rule_number = $rule_number,
                                r.text = $text,
                                r.description = $description
                            WITH r
                            MATCH (o:Order {order_id: $order_id})
                            MERGE (r)-[:PART_OF]->(o)
                        """, rule_id=rule_id,
                             rule_number=rule.get("rule_number"),
                             text=rule.get("text", ""),
                             description=rule.get("description", ""),
                             order_id=order_id)

        logger.info("✓ Orders loaded")

    def _generate_id(self, text: str) -> str:
        """Generate ID from text"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def create_vector_indexes(self):
        """Create vector indexes for RAG"""
        if not self.enable_embeddings:
            logger.info("Embeddings disabled, skipping vector indexes")
            return

        logger.info("Creating vector indexes for RAG...")
        with global_monitor.track("create_vector_indexes"):
            self.embeddings_loader.create_vector_indexes()
        logger.info("✓ Vector indexes created")

    def generate_case_embeddings(self):
        """Generate embeddings for all cases in Neo4j"""
        if not self.enable_embeddings:
            logger.info("Embeddings disabled, skipping embedding generation")
            return

        logger.info("Generating embeddings for cases...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Get all cases
            result = session.run("""
                MATCH (c:Case)
                WHERE c.embedding IS NULL
                RETURN c.case_id as case_id,
                       c.title as title,
                       c.summary as summary,
                       c.facts as facts,
                       c.holding as holding,
                       c.reasoning as reasoning,
                       c.full_text as full_text
                LIMIT 1000
            """)

            cases = []
            for record in result:
                cases.append(dict(record))

            if not cases:
                logger.info("No cases found without embeddings")
                return

            logger.info(f"Found {len(cases)} cases to embed")

            # Generate embeddings
            for case in tqdm(cases, desc="Generating case embeddings"):
                with global_monitor.track("case_embedding"):
                    embedding = self.embeddings_gen.generate_case_embedding(case)

                    # Update in Neo4j
                    self.embeddings_loader.update_case_embeddings(
                        case['case_id'],
                        embedding
                    )

            logger.info(f"✓ Generated embeddings for {len(cases)} cases")

    def generate_chunks(self):
        """Generate text chunks for all cases"""
        if not self.enable_embeddings:
            logger.info("Embeddings disabled, skipping chunk generation")
            return

        logger.info("Generating text chunks for RAG...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Get cases with full text
            result = session.run("""
                MATCH (c:Case)
                WHERE c.full_text IS NOT NULL
                  AND LENGTH(c.full_text) > 1000
                  AND NOT EXISTS((c)-[:HAS_CHUNK]->())
                RETURN c.case_id as case_id,
                       c.full_text as full_text
                LIMIT 500
            """)

            cases = list(result)

            if not cases:
                logger.info("No cases found for chunking")
                return

            logger.info(f"Creating chunks for {len(cases)} cases")

            all_chunks = []

            for record in tqdm(cases, desc="Creating chunks"):
                with global_monitor.track("chunk_creation"):
                    case_id = record['case_id']
                    full_text = record['full_text']

                    # Create chunks with embeddings
                    chunks = create_chunks_with_embeddings(
                        text=full_text,
                        source_id=case_id,
                        source_type="case"
                    )

                    all_chunks.extend(chunks)

            # Load chunks to Neo4j
            logger.info(f"Loading {len(all_chunks)} chunks to Neo4j...")
            self.embeddings_loader.load_chunks(all_chunks)

            logger.info(f"✓ Created and loaded {len(all_chunks)} chunks")

    def get_statistics(self):
        """Get graph statistics"""
        logger.info("Fetching graph statistics...")

        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)

            print("\n" + "="*60)
            print("LLM-POWERED KNOWLEDGE GRAPH STATISTICS")
            print("="*60)

            total_nodes = 0
            for record in result:
                label = record['label']
                count = record['count']
                if label:
                    print(f"  {label:20} {count:4} nodes")
                    total_nodes += count

            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(*) as count
                ORDER BY count DESC
                LIMIT 15
            """)

            print("\nTop Relationships:")
            total_rels = 0
            for record in rel_result:
                print(f"  {record['rel_type']:25} {record['count']:4} relationships")
                total_rels += record['count']

            total_rel = session.run("MATCH ()-[r]->() RETURN count(r) as total").single()['total']

            print(f"\n{'TOTAL':20} {total_nodes:4} nodes")
            print(f"{'TOTAL':20} {total_rel:4} relationships")
            print("="*60 + "\n")

        # Export metrics
        global_monitor.export_metrics("logs/llm_graph_metrics.json")
        global_monitor.print_summary()

    def close(self):
        """Close connections"""
        self.driver.close()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Build LLM-powered knowledge graph with RAG capabilities")
    parser.add_argument("--model", default="gpt-4-turbo", help="LLM model")
    parser.add_argument("--pdfs", nargs="+", default=["cpc2.pdf"], help="PDF files to process")
    parser.add_argument("--text-files", nargs="+", default=["cpc.txt", "act.txt"], help="Text files")
    parser.add_argument("--db-path", default="../data-collection/data/indiankanoon.db", help="SQLite DB path")
    parser.add_argument("--db-limit", type=int, default=50, help="Max DB cases")
    parser.add_argument("--skip-pdfs", action="store_true", help="Skip PDF processing")
    parser.add_argument("--skip-text", action="store_true", help="Skip text file processing")
    parser.add_argument("--skip-db", action="store_true", help="Skip database processing")
    parser.add_argument("--no-embeddings", action="store_true", help="Disable embeddings generation")
    parser.add_argument("--skip-chunks", action="store_true", help="Skip chunk generation")

    args = parser.parse_args()

    logger.info("="*60)
    logger.info("LLM-POWERED KNOWLEDGE GRAPH BUILDER")
    logger.info("="*60)

    builder = LLMGraphBuilder(llm_model=args.model, enable_embeddings=not args.no_embeddings)

    try:
        # Create schema constraints
        builder.create_schema_constraints()

        # Create vector indexes
        if not args.no_embeddings:
            builder.create_vector_indexes()

        # Process PDFs
        if not args.skip_pdfs:
            pdf_files = [str(Path(__file__).parent / pdf) for pdf in args.pdfs]
            builder.process_pdfs(pdf_files)

        # Process text files
        if not args.skip_text:
            text_files = {}
            for text_file in args.text_files:
                file_path = Path(__file__).parent / text_file
                if file_path.exists():
                    file_type = "statute" if "cpc" in text_file.lower() else "order"
                    text_files[str(file_path)] = file_type

            if text_files:
                builder.process_text_files(text_files)

        # Process database
        if not args.skip_db:
            db_path = Path(__file__).parent / args.db_path
            if db_path.exists():
                builder.process_database(str(db_path), limit=args.db_limit)
            else:
                logger.warning(f"Database not found: {db_path}")

        # Generate embeddings for cases
        if not args.no_embeddings:
            builder.generate_case_embeddings()

        # Generate chunks
        if not args.no_embeddings and not args.skip_chunks:
            builder.generate_chunks()

        # Get statistics
        builder.get_statistics()

        logger.info("✅ LLM-powered knowledge graph built successfully!")

    finally:
        builder.close()


if __name__ == "__main__":
    main()
