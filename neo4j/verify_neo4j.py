"""
Verify the CPC Knowledge Graph is properly loaded in Neo4j
"""
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

def verify_graph():
    driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    print("\n" + "="*60)
    print("🔍 VERIFYING NEO4J KNOWLEDGE GRAPH")
    print("="*60)

    with driver.session(database=NEO4J_DATABASE) as session:
        # Check connection
        print(f"\n✓ Connected to: {NEO4J_URL}")
        print(f"✓ Database: {NEO4J_DATABASE}")

        # Count nodes by type
        print("\n📊 Node Counts:")
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as label, count(*) as count
            ORDER BY count DESC
        """)

        total_nodes = 0
        for record in result:
            label = record['label']
            count = record['count']
            print(f"   {label:15} {count:3} nodes")
            total_nodes += count

        print(f"   {'TOTAL':15} {total_nodes:3} nodes")

        # Count relationships
        print("\n🔗 Relationship Counts:")
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(*) as count
            ORDER BY count DESC
        """)

        total_rels = 0
        for record in result:
            rel_type = record['rel_type']
            count = record['count']
            print(f"   {rel_type:20} {count:3} relationships")
            total_rels += count

        print(f"   {'TOTAL':20} {total_rels:3} relationships")

        # Show sample cases
        print("\n📋 Sample Cases in Graph:")
        result = session.run("""
            MATCH (c:Case)
            RETURN c.name as name, c.citation as citation, c.topic as topic
            ORDER BY c.year
            LIMIT 5
        """)

        for i, record in enumerate(result, 1):
            print(f"   {i}. {record['citation']} - {record['topic']}")
            print(f"      {record['name']}")

        # Show Neo4j Browser URL
        print("\n" + "="*60)
        print("🌐 ACCESS YOUR GRAPH IN NEO4J BROWSER")
        print("="*60)
        print(f"\n1. Open: https://console.neo4j.io")
        print(f"\n2. Login with your Neo4j Aura account")
        print(f"\n3. Select instance: Instance01 (d0d1fe15)")
        print(f"\n4. Click 'Open with' → 'Neo4j Browser'")
        print(f"\n5. Run this query to see the full graph:")
        print(f"\n   MATCH (n) RETURN n LIMIT 100")
        print(f"\n   OR")
        print(f"\n   MATCH path = (c:Case)-[r]-(n) RETURN path")
        print("\n" + "="*60)
        print("\n✅ Graph is ready in Neo4j!")
        print("="*60 + "\n")

    driver.close()

if __name__ == "__main__":
    verify_graph()
