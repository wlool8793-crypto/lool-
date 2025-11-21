"""
Clear Neo4j Database Completely
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def clear_database():
    """Clear all nodes and relationships from Neo4j"""
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session(database=NEO4J_DATABASE) as session:
        print("Clearing all nodes and relationships...")

        # Delete all relationships first
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()['count']
        print(f"Found {rel_count} relationships to delete")

        session.run("MATCH ()-[r]->() DELETE r")
        print("✓ All relationships deleted")

        # Delete all nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()['count']
        print(f"Found {node_count} nodes to delete")

        session.run("MATCH (n) DETACH DELETE n")
        print("✓ All nodes deleted")

        # Drop all constraints
        print("Dropping all constraints...")
        constraints = session.run("SHOW CONSTRAINTS")
        for constraint in constraints:
            constraint_name = constraint.get('name')
            if constraint_name:
                try:
                    session.run(f"DROP CONSTRAINT {constraint_name} IF EXISTS")
                    print(f"  Dropped constraint: {constraint_name}")
                except Exception as e:
                    print(f"  Could not drop constraint {constraint_name}: {e}")

        # Drop all indexes
        print("Dropping all indexes...")
        indexes = session.run("SHOW INDEXES")
        for index in indexes:
            index_name = index.get('name')
            if index_name and not index_name.startswith('constraint_'):
                try:
                    session.run(f"DROP INDEX {index_name} IF EXISTS")
                    print(f"  Dropped index: {index_name}")
                except Exception as e:
                    print(f"  Could not drop index {index_name}: {e}")

        # Verify clean database
        result = session.run("MATCH (n) RETURN count(n) as nodes")
        nodes = result.single()['nodes']
        result = session.run("MATCH ()-[r]->() RETURN count(r) as rels")
        rels = result.single()['rels']

        print("\n" + "="*60)
        print("DATABASE CLEARED")
        print("="*60)
        print(f"Nodes remaining: {nodes}")
        print(f"Relationships remaining: {rels}")
        print("="*60)
        print("\nDatabase is now clean and ready for fresh data!")

    driver.close()

if __name__ == "__main__":
    clear_database()
