"""
Load the complete CPC data into Neo4j knowledge graph
"""
import json
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")


class CPCFullLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.data = self.load_parsed_data()

    def load_parsed_data(self):
        """Load parsed CPC data"""
        json_path = Path(__file__).parent / "cpc_full_data.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_parts(self):
        """Load all Parts into Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for part in self.data['parts']:
                session.run("""
                    MERGE (p:Part {id: $part_number})
                    SET p.title = $title,
                        p.part_number = $part_number
                    WITH p
                    MATCH (stat:Statute {id: 'cpc_1908'})
                    MERGE (p)-[:PART_OF]->(stat)
                """, part_number=part['part_number'], title=part['title'])

            print(f"✓ Loaded {len(self.data['parts'])} Parts")

    def load_main_sections(self):
        """Load main sections only (not all subsections to avoid clutter)"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Filter to main sections (Section 1-158 typically)
            main_sections = [s for s in self.data['sections']
                           if s['section_number'] <= 158 and 'Section' in s['section_id']]

            print(f"Loading {len(main_sections)} main sections...")

            for i, section in enumerate(main_sections):
                # Check if section already exists
                existing = session.run("""
                    MATCH (s:Section {section_id: $section_id})
                    RETURN s
                """, section_id=section['section_id']).single()

                if existing:
                    # Update existing section with more details
                    session.run("""
                        MATCH (s:Section {section_id: $section_id})
                        SET s.title = $title,
                            s.section_number = $section_number,
                            s.full_text = $text
                    """, section_id=section['section_id'],
                         title=section['title'],
                         section_number=section['section_number'],
                         text=section.get('text', ''))
                else:
                    # Create new section
                    session.run("""
                        MERGE (s:Section {id: $id})
                        SET s.section_id = $section_id,
                            s.title = $title,
                            s.section_number = $section_number,
                            s.full_text = $text,
                            s.statute = 'Code of Civil Procedure, 1908'
                        WITH s
                        MATCH (stat:Statute {id: 'cpc_1908'})
                        MERGE (s)-[:PART_OF]->(stat)
                    """, id=f"sec_{section['section_number']}",
                         section_id=section['section_id'],
                         title=section['title'],
                         section_number=section['section_number'],
                         text=section.get('text', ''))

                # Link to Part if available
                if section.get('part'):
                    session.run("""
                        MATCH (s:Section {section_id: $section_id})
                        MATCH (p:Part {id: $part_id})
                        MERGE (s)-[:BELONGS_TO_PART]->(p)
                    """, section_id=section['section_id'], part_id=section['part'])

                if (i + 1) % 20 == 0:
                    print(f"  Loaded {i + 1}/{len(main_sections)} sections...")

            print(f"✓ Loaded {len(main_sections)} main sections")

    def load_orders(self):
        """Load all Orders into Neo4j"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Get unique orders (there might be duplicates in parsing)
            unique_orders = {}
            for order in self.data['orders']:
                order_id = order['order_id']
                if order_id not in unique_orders:
                    unique_orders[order_id] = order

            print(f"Loading {len(unique_orders)} unique orders...")

            for i, (order_id, order) in enumerate(unique_orders.items()):
                session.run("""
                    MERGE (o:Order {id: $order_id})
                    SET o.order_id = $order_id,
                        o.title = $title
                    WITH o
                    MATCH (stat:Statute {id: 'cpc_1908'})
                    MERGE (o)-[:PART_OF]->(stat)
                """, order_id=order_id, title=order['title'])

                if (i + 1) % 10 == 0:
                    print(f"  Loaded {i + 1}/{len(unique_orders)} orders...")

            print(f"✓ Loaded {len(unique_orders)} Orders")

    def load_definitions(self):
        """Load key definitions"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            for definition in self.data['definitions']:
                session.run("""
                    MERGE (d:Definition {term: $term})
                    SET d.section = $section,
                        d.defined_in = $defined_in
                    WITH d
                    MATCH (s:Section {section_id: $section})
                    MERGE (d)-[:DEFINED_IN]->(s)
                """, term=definition['term'],
                     section=definition['section'],
                     defined_in=definition['defined_in'])

            print(f"✓ Loaded {len(self.data['definitions'])} Definitions")

    def get_updated_statistics(self):
        """Get updated graph statistics"""
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)

            print("\n" + "="*60)
            print("UPDATED KNOWLEDGE GRAPH STATISTICS")
            print("="*60)

            total_nodes = 0
            for record in result:
                label = record['label']
                count = record['count']
                if label:  # Skip None labels
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
                rel_type = record['rel_type']
                count = record['count']
                print(f"  {rel_type:25} {count:4} relationships")
                total_rels += count

            # Get total relationships
            total_rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
            total_rels = total_rel_result.single()['total']

            print(f"\n{'TOTAL':20} {total_nodes:4} nodes")
            print(f"{'TOTAL':20} {total_rels:4} relationships")
            print("="*60 + "\n")

    def load_all(self):
        """Load all CPC data into Neo4j"""
        print("\n🔨 Loading Complete CPC into Neo4j Knowledge Graph...\n")

        self.load_parts()
        self.load_main_sections()
        self.load_orders()
        self.load_definitions()

        print("\n✅ CPC data loaded successfully!")

        self.get_updated_statistics()

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    loader = CPCFullLoader()
    try:
        loader.load_all()
    finally:
        loader.close()
