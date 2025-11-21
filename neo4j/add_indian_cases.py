"""
Extract Indian Kanoon cases from SQLite and load into Neo4j knowledge graph
"""
import sqlite3
import re
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import json

load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")


class IndianCaseExtractor:
    def __init__(self):
        self.db_path = "/workspaces/lool-/data-collection/data/indiankanoon.db"
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def extract_cases_from_db(self, limit=30):
        """Extract top cases with substantial full text"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT id, title, court, bench, author, full_text, case_date,
                   citation, snippet, court_name, court_type, year
            FROM legal_cases
            WHERE full_text IS NOT NULL
            AND LENGTH(full_text) > 10000
            ORDER BY LENGTH(full_text) DESC
            LIMIT ?
        """

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

        cases = []
        for row in rows:
            case_data = dict(row)
            # Parse additional info from full text
            parsed = self.parse_case_text(case_data['full_text'], case_data['title'])
            case_data.update(parsed)
            cases.append(case_data)

        conn.close()
        print(f"\n✓ Extracted {len(cases)} cases from database")
        return cases

    def parse_case_text(self, full_text, title):
        """Extract structured information from case full text"""
        parsed = {
            'court_name': None,
            'judges': [],
            'parties': {'petitioner': [], 'respondent': []},
            'sections_cited': [],
            'case_type': None
        }

        # Extract court name
        court_match = re.search(r'(Supreme Court of India|High Court|District Court)', full_text[:2000], re.IGNORECASE)
        if court_match:
            parsed['court_name'] = court_match.group(1)

        # Extract judge names from Bench line
        bench_match = re.search(r'Bench:\s*([^\n]+)', full_text[:3000])
        if bench_match:
            bench_text = bench_match.group(1)
            # Split by comma and clean
            judges = [j.strip() for j in bench_text.split(',') if j.strip()]
            parsed['judges'] = judges[:3]  # Limit to 3 judges

        # Extract case type
        type_match = re.search(r'(CRIMINAL|CIVIL|WRIT PETITION|SPECIAL LEAVE PETITION|APPEAL)', full_text[:2000], re.IGNORECASE)
        if type_match:
            parsed['case_type'] = type_match.group(1).upper()

        # Extract parties from title
        parties_match = re.match(r'(.+?)\s+vs\s+(.+?)\s+on\s+', title, re.IGNORECASE)
        if parties_match:
            parsed['parties']['petitioner'] = [parties_match.group(1).strip()]
            parsed['parties']['respondent'] = [parties_match.group(2).strip()]

        # Extract section references (e.g., Section 170, Section 10 CPC)
        section_matches = re.findall(r'Section\s+(\d+[A-Z]?)\s*(?:of\s+(?:the\s+)?(.+?))?(?:\s|,|\.|$)', full_text[:50000])
        sections_found = set()
        for section_num, statute in section_matches[:20]:  # Limit to 20 sections
            if statute and 'civil procedure' in statute.lower():
                sections_found.add(f"Section {section_num}")
            elif not statute:
                sections_found.add(f"Section {section_num}")

        parsed['sections_cited'] = list(sections_found)

        return parsed

    def load_cases_to_neo4j(self, cases):
        """Load Indian cases into Neo4j"""
        with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:

            # Create India Country node
            session.run("""
                MERGE (c:Country {name: 'India'})
            """)

            loaded_count = 0
            for i, case in enumerate(cases):
                try:
                    # Create case node
                    case_id = f"indian_case_{case['id']}"

                    # Extract date from title if not in case_date
                    date_match = re.search(r'on\s+(\d+\s+\w+,?\s+\d{4})', case['title'])
                    case_date = date_match.group(1) if date_match else case.get('case_date', 'Unknown')

                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', case_date if case_date else case['title'])
                    year = int(year_match.group(0)) if year_match else None

                    session.run("""
                        MERGE (c:Case {id: $case_id})
                        SET c.name = $title,
                            c.citation = $citation,
                            c.date = $date,
                            c.year = $year,
                            c.case_type = $case_type,
                            c.source = 'IndianKanoon',
                            c.country = 'India',
                            c.snippet = $snippet
                    """, case_id=case_id,
                         title=case['title'][:200],
                         citation=case.get('citation', f"IK-{case['id']}"),
                         date=case_date,
                         year=year,
                         case_type=case.get('case_type', 'Unknown'),
                         snippet=case.get('snippet', '')[:500])

                    # Link to India
                    session.run("""
                        MATCH (c:Case {id: $case_id})
                        MATCH (country:Country {name: 'India'})
                        MERGE (c)-[:FROM_COUNTRY]->(country)
                    """, case_id=case_id)

                    # Create Court node if available
                    if case.get('court_name'):
                        court_id = case['court_name'].replace(' ', '_').lower()
                        session.run("""
                            MERGE (court:Court {id: $court_id})
                            SET court.name = $court_name,
                                court.country = 'India'
                            WITH court
                            MATCH (c:Case {id: $case_id})
                            MERGE (c)-[:BEFORE_COURT]->(court)
                        """, court_id=court_id,
                             court_name=case['court_name'],
                             case_id=case_id)

                    # Create Judge nodes
                    for judge_name in case.get('judges', [])[:3]:
                        if judge_name and len(judge_name) > 2:
                            judge_id = judge_name.replace(' ', '_').replace('.', '').lower()
                            session.run("""
                                MERGE (j:Judge {id: $judge_id})
                                SET j.name = $judge_name
                                WITH j
                                MATCH (c:Case {id: $case_id})
                                MERGE (c)-[:DECIDED_BY]->(j)
                            """, judge_id=judge_id,
                                 judge_name=judge_name,
                                 case_id=case_id)

                    # Create Party nodes
                    for petitioner in case.get('parties', {}).get('petitioner', [])[:2]:
                        if petitioner and len(petitioner) > 2:
                            party_id = petitioner[:50].replace(' ', '_').lower()
                            session.run("""
                                MERGE (p:Party {id: $party_id})
                                SET p.name = $party_name,
                                    p.role = 'Petitioner'
                                WITH p
                                MATCH (c:Case {id: $case_id})
                                MERGE (c)-[:PETITIONER]->(p)
                            """, party_id=party_id,
                                 party_name=petitioner[:100],
                                 case_id=case_id)

                    for respondent in case.get('parties', {}).get('respondent', [])[:2]:
                        if respondent and len(respondent) > 2:
                            party_id = respondent[:50].replace(' ', '_').lower()
                            session.run("""
                                MERGE (p:Party {id: $party_id})
                                SET p.name = $party_name,
                                    p.role = 'Respondent'
                                WITH p
                                MATCH (c:Case {id: $case_id})
                                MERGE (c)-[:RESPONDENT]->(p)
                            """, party_id=party_id,
                                 party_name=respondent[:100],
                                 case_id=case_id)

                    # Link to CPC Sections if they exist in graph
                    for section_id in case.get('sections_cited', [])[:10]:
                        # Try to find existing section in graph
                        result = session.run("""
                            MATCH (s:Section)
                            WHERE s.section_id = $section_id
                            RETURN s.section_id as id
                            LIMIT 1
                        """, section_id=section_id)

                        if result.single():
                            session.run("""
                                MATCH (c:Case {id: $case_id})
                                MATCH (s:Section {section_id: $section_id})
                                MERGE (c)-[:APPLIES_SECTION]->(s)
                            """, case_id=case_id, section_id=section_id)

                    # Create Topic node for case type
                    if case.get('case_type'):
                        session.run("""
                            MERGE (t:Topic {name: $topic})
                            WITH t
                            MATCH (c:Case {id: $case_id})
                            MERGE (c)-[:BELONGS_TO_TOPIC]->(t)
                        """, topic=case['case_type'], case_id=case_id)

                    loaded_count += 1
                    if (i + 1) % 5 == 0:
                        print(f"  Loaded {i + 1}/{len(cases)} cases...")

                except Exception as e:
                    print(f"  Error loading case {case['id']}: {str(e)}")
                    continue

            print(f"\n✓ Successfully loaded {loaded_count}/{len(cases)} Indian cases")
            return loaded_count

    def get_statistics(self):
        """Get updated graph statistics"""
        with self.neo4j_driver.session(database=NEO4J_DATABASE) as session:
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
                if label:
                    print(f"  {label:20} {count:4} nodes")
                    total_nodes += count

            # Count Indian cases specifically
            indian_cases = session.run("""
                MATCH (c:Case {source: 'IndianKanoon'})
                RETURN count(c) as count
            """).single()['count']

            bangladesh_cases = session.run("""
                MATCH (c:Case)
                WHERE c.source IS NULL OR c.source <> 'IndianKanoon'
                RETURN count(c) as count
            """).single()['count']

            print(f"\n  {'Indian Cases':20} {indian_cases:4}")
            print(f"  {'Bangladesh Cases':20} {bangladesh_cases:4}")

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

            total_rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
            total_rels = total_rel_result.single()['total']

            print(f"\n{'TOTAL':20} {total_nodes:4} nodes")
            print(f"{'TOTAL':20} {total_rels:4} relationships")
            print("="*60 + "\n")

    def close(self):
        self.neo4j_driver.close()


def main():
    print("\n🇮🇳 Adding Indian Kanoon Cases to Neo4j Knowledge Graph...\n")

    extractor = IndianCaseExtractor()

    try:
        # Extract top 30 cases with best data
        cases = extractor.extract_cases_from_db(limit=30)

        # Show sample
        print("\nSample cases to be loaded:")
        for i, case in enumerate(cases[:5], 1):
            print(f"\n{i}. {case['title'][:80]}")
            print(f"   Court: {case.get('court_name', 'Unknown')}")
            print(f"   Judges: {', '.join(case.get('judges', [])[:2])}")
            print(f"   Sections cited: {', '.join(case.get('sections_cited', [])[:5])}")

        # Load into Neo4j
        print(f"\n\n🔨 Loading {len(cases)} Indian cases into Neo4j...\n")
        extractor.load_cases_to_neo4j(cases)

        # Show updated statistics
        extractor.get_statistics()

        print("✅ Indian cases successfully added to knowledge graph!")
        print("\n💡 View in Neo4j Browser:")
        print("   MATCH path = (c:Case {source: 'IndianKanoon'})-[r]-(n)")
        print("   RETURN path LIMIT 100")

    finally:
        extractor.close()


if __name__ == "__main__":
    main()
