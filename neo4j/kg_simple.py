from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

load_dotenv()

# Load from environment variables OR use hardcoded values
NEO4J_URL = os.getenv("NEO4J_URL", "neo4j+s://d0d1fe15.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "QR9Xqoy0bdfPVSB77hqO-cHZwaouDYUJW43CU6gYKGA")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
AURA_INSTANCEID = os.getenv("AURA_INSTANCEID", "d0d1fe15")
AURA_INSTANCENAME = os.getenv("AURA_INSTANCENAME", "Instance01")

AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

# Create driver (without database parameter)
driver = GraphDatabase.driver(NEO4J_URL, auth=AUTH)


def connect_and_query():
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (n) RETURN count(n)")
            count = result.single().value()
            print(f"Number of nodes: {count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()


def create_entities(tx):
    # Create Albert Einstein node
    tx.run("MERGE (a:Person {name: 'Albert Einstein'})")

    # Create other nodes
    tx.run("MERGE (p:Subject {name: 'Physics'})")
    tx.run("MERGE (n:NobelPrize {name: 'Nobel Prize in Physics'})")
    tx.run("MERGE (g:Country {name: 'Germany'})")
    tx.run("MERGE (u:Country {name: 'USA'})")


def create_relationships(tx):
    # Create studied relationship
    tx.run(
        """
    MATCH (a:Person {name: 'Albert Einstein'}), (p:Subject {name: 'Physics'})
    MERGE (a)-[:STUDIED]->(p)
    """
    )

    # Create won relationship
    tx.run(
        """
    MATCH (a:Person {name: 'Albert Einstein'}), (n:NobelPrize {name: 'Nobel Prize in Physics'})
    MERGE (a)-[:WON]->(n)
    """
    )

    # Create born in relationship
    tx.run(
        """
    MATCH (a:Person {name: 'Albert Einstein'}), (g:Country {name: 'Germany'})
    MERGE (a)-[:BORN_IN]->(g)
    """
    )

    # Create died in relationship
    tx.run(
        """
    MATCH (a:Person {name: 'Albert Einstein'}), (u:Country {name: 'USA'})
    MERGE (a)-[:DIED_IN]->(u)
    """
    )


# Function to connect and run a simple Cypher query
def query_graph_simple(cypher_query):
    local_driver = GraphDatabase.driver(NEO4J_URL, auth=AUTH)
    try:
        with local_driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher_query)
            for record in result:
                print(record["name"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        local_driver.close()


# Function to connect and run a Cypher query
def query_graph(cypher_query):
    local_driver = GraphDatabase.driver(NEO4J_URL, auth=AUTH)
    try:
        with local_driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher_query)
            for record in result:
                print(record["path"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        local_driver.close()


def build_knowledge_graph():
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Create entities
            session.execute_write(create_entities)
            # Create relationships
            session.execute_write(create_relationships)
            print("Knowledge graph built successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()


# Main execution
if __name__ == "__main__":
    print("Building knowledge graph...")
    build_knowledge_graph()