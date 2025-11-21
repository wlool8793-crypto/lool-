"""
Build Neo4j Knowledge Graph from extracted CPC data
"""
import json
from pathlib import Path
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from dotenv import load_dotenv
import os
import logging
from utils.error_handling import (
    neo4j_retry,
    safe_neo4j_operation,
    Neo4jTransactionContext,
    validate_json_structure
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Validate required environment variables
if not all([NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError(
        "Missing required environment variables. Please set:\n"
        "  - NEO4J_URL\n"
        "  - NEO4J_USERNAME\n"
        "  - NEO4J_PASSWORD\n"
        "in your .env file or environment."
    )


class CPCGraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.data = self.load_data()

    def load_data(self):
        """Load extracted CPC data from JSON with validation"""
        json_path = Path(__file__).parent / "cpc_data.json"

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate data structure
            required_keys = ['cases', 'sections', 'courts', 'principles', 'statutes']
            validate_json_structure(data, required_keys, "CPC data")

            logger.info(f"Loaded CPC data: {len(data['cases'])} cases, "
                       f"{len(data['sections'])} sections, "
                       f"{len(data['courts'])} courts")

            return data

        except FileNotFoundError:
            logger.error(f"Data file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {json_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    @neo4j_retry(max_attempts=3)
    def clear_database(self):
        """Clear existing data (optional - for clean start)"""
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                with Neo4jTransactionContext(session, "Clear database") as tx:
                    result = tx.run("MATCH (n) RETURN count(n) as count")
                    count = result.single()['count']

                    if count > 0:
                        logger.warning(f"Deleting {count} existing nodes")
                        tx.run("MATCH (n) DETACH DELETE n")
                        logger.info("✓ Cleared existing data")
                    else:
                        logger.info("Database already empty")
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            raise

    @neo4j_retry(max_attempts=3)
    def create_constraints_and_indexes(self):
        """Create uniqueness constraints and indexes with error handling"""
        constraints = [
            ("case_id", "CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE"),
            ("court_id", "CREATE CONSTRAINT court_id IF NOT EXISTS FOR (c:Court) REQUIRE c.id IS UNIQUE"),
            ("section_id", "CREATE CONSTRAINT section_id IF NOT EXISTS FOR (s:Section) REQUIRE s.id IS UNIQUE"),
            ("principle_id", "CREATE CONSTRAINT principle_id IF NOT EXISTS FOR (p:Principle) REQUIRE p.id IS UNIQUE"),
            ("statute_id", "CREATE CONSTRAINT statute_id IF NOT EXISTS FOR (s:Statute) REQUIRE s.id IS UNIQUE"),
        ]

        created_count = 0
        skipped_count = 0

        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                for name, constraint_cypher in constraints:
                    result = safe_neo4j_operation(
                        session.run,
                        constraint_cypher,
                        error_message=f"Failed to create constraint {name}"
                    )
                    if result is not None:
                        created_count += 1
                        logger.debug(f"Created constraint: {name}")
                    else:
                        skipped_count += 1
                        logger.debug(f"Skipped constraint (may exist): {name}")

            logger.info(f"✓ Constraints: {created_count} created, {skipped_count} skipped")

        except Exception as e:
            logger.error(f"Error creating constraints: {str(e)}")
            raise

    def create_statutes(self):
        """Create Statute nodes"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for statute in self.data['statutes']:
                params = {
                    'id': statute['id'],
                    'name': statute['name'],
                    'country': statute['country']
                }
                if 'short_name' in statute:
                    params['short_name'] = statute['short_name']

                query = """
                    MERGE (s:Statute {id: $id})
                    SET s.name = $name,
                        s.country = $country
                """
                if 'short_name' in statute:
                    query += ", s.short_name = $short_name"

                session.run(query, params)
            print(f"✓ Created {len(self.data['statutes'])} Statute nodes")

    def create_sections(self):
        """Create Section nodes and link to Statutes"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for section in self.data['sections']:
                session.run("""
                    MERGE (sec:Section {id: $id})
                    SET sec.section_id = $section_id,
                        sec.title = $title,
                        sec.description = $description
                """, section)

                # Link to Statute
                if section['statute'] == "Code of Civil Procedure, 1908":
                    statute_id = "cpc_1908"
                elif section['statute'] == "Partition Act, 1893":
                    statute_id = "partition_act_1893"
                else:
                    statute_id = "cpc_1908"

                session.run("""
                    MATCH (sec:Section {id: $section_id})
                    MATCH (stat:Statute {id: $statute_id})
                    MERGE (sec)-[:PART_OF]->(stat)
                """, section_id=section['id'], statute_id=statute_id)

            print(f"✓ Created {len(self.data['sections'])} Section nodes")

    def create_courts(self):
        """Create Court nodes"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for court in self.data['courts']:
                session.run("""
                    MERGE (c:Court {id: $id})
                    SET c.name = $name,
                        c.type = $type
                """, court)
            print(f"✓ Created {len(self.data['courts'])} Court nodes")

    def create_principles(self):
        """Create Principle nodes"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for principle in self.data['principles']:
                session.run("""
                    MERGE (p:Principle {id: $id})
                    SET p.name = $name,
                        p.description = $description,
                        p.category = $category
                """, principle)
            print(f"✓ Created {len(self.data['principles'])} Principle nodes")

    def create_cases(self):
        """Create Case nodes and all related entities"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for case in self.data['cases']:
                # Create Case node
                session.run("""
                    MERGE (c:Case {id: $id})
                    SET c.name = $name,
                        c.citation = $citation,
                        c.year = $year,
                        c.date = $date,
                        c.topic = $topic,
                        c.abstract = $abstract,
                        c.issue = $issue,
                        c.holding = $holding,
                        c.significance = $significance
                """, case)

                # Create Topic node and link
                session.run("""
                    MERGE (t:Topic {name: $topic})
                    WITH t
                    MATCH (c:Case {id: $case_id})
                    MERGE (c)-[:BELONGS_TO_TOPIC]->(t)
                """, topic=case['topic'], case_id=case['id'])

                # Link to Court
                session.run("""
                    MATCH (c:Case {id: $case_id})
                    MATCH (court:Court {name: $court_name})
                    MERGE (c)-[:BEFORE_COURT]->(court)
                """, case_id=case['id'], court_name=case['court'])

                # Create Judge nodes and link
                for judge_name in case['judges']:
                    session.run("""
                        MERGE (j:Judge {name: $judge_name})
                        WITH j
                        MATCH (c:Case {id: $case_id})
                        MERGE (c)-[:DECIDED_BY]->(j)
                    """, judge_name=judge_name, case_id=case['id'])

                # Create Party nodes (Petitioners)
                for party_name in case['petitioner']:
                    session.run("""
                        MERGE (p:Party {name: $party_name})
                        WITH p
                        MATCH (c:Case {id: $case_id})
                        MERGE (c)-[:PETITIONER]->(p)
                    """, party_name=party_name, case_id=case['id'])

                # Create Party nodes (Respondents)
                for party_name in case['respondent']:
                    session.run("""
                        MERGE (p:Party {name: $party_name})
                        WITH p
                        MATCH (c:Case {id: $case_id})
                        MERGE (c)-[:RESPONDENT]->(p)
                    """, party_name=party_name, case_id=case['id'])

                # Link to Sections
                for section_ref in case['sections']:
                    # Find matching section
                    for section in self.data['sections']:
                        if section['section_id'] == section_ref:
                            session.run("""
                                MATCH (c:Case {id: $case_id})
                                MATCH (s:Section {id: $section_id})
                                MERGE (c)-[:APPLIES_SECTION]->(s)
                            """, case_id=case['id'], section_id=section['id'])
                            break

                # Link to Principles
                for principle_name in case['principles']:
                    # Find matching principle
                    for principle in self.data['principles']:
                        if principle_name.lower() in principle['name'].lower() or principle['name'].lower() in principle_name.lower():
                            session.run("""
                                MATCH (c:Case {id: $case_id})
                                MATCH (p:Principle {id: $principle_id})
                                MERGE (c)-[:ESTABLISHES]->(p)
                            """, case_id=case['id'], principle_id=principle['id'])
                            break

            print(f"✓ Created {len(self.data['cases'])} Case nodes with all relationships")

    def create_precedent_relationships(self):
        """Create citation/precedent relationships between cases"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Case 2 cites Full Bench decision (mentioned in text)
            session.run("""
                MATCH (c1:Case {id: 'case_2'})
                MERGE (precedent:Case {name: 'AHM Khurshed Ali vs Md Hashem Ali', citation: '58 DLR 211'})
                MERGE (c1)-[:CITES_PRECEDENT {context: 'pecuniary jurisdiction'}]->(precedent)
            """)

            # Case 4 cites precedent
            session.run("""
                MATCH (c1:Case {id: 'case_4'})
                MERGE (precedent:Case {name: 'Syesta Bibi vs Juma Sha', citation: '1 BLT AD 34'})
                MERGE (c1)-[:CITES_PRECEDENT {context: 'no limitation for Section 4'}]->(precedent)
            """)

            print("✓ Created precedent citation relationships")

    def get_statistics(self):
        """Get graph statistics"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)

            print("\n" + "="*50)
            print("KNOWLEDGE GRAPH STATISTICS")
            print("="*50)

            total_nodes = 0
            for record in result:
                print(f"  {record['label']}: {record['count']}")
                total_nodes += record['count']

            # Count relationships
            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(*) as count
                ORDER BY count DESC
            """)

            print("\nRelationships:")
            total_rels = 0
            for record in rel_result:
                print(f"  {record['rel_type']}: {record['count']}")
                total_rels += record['count']

            print(f"\nTotal Nodes: {total_nodes}")
            print(f"Total Relationships: {total_rels}")
            print("="*50 + "\n")

    def build_complete_graph(self):
        """Build the complete knowledge graph"""
        print("\n🔨 Building CPC Knowledge Graph...\n")

        # Optional: Clear existing data
        # self.clear_database()

        self.create_constraints_and_indexes()
        self.create_statutes()
        self.create_sections()
        self.create_courts()
        self.create_principles()
        self.create_cases()
        self.create_precedent_relationships()

        print("\n✅ Knowledge graph built successfully!")

        self.get_statistics()

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    builder = CPCGraphBuilder()
    try:
        builder.build_complete_graph()
    finally:
        builder.close()
