"""
Schema Implementer Agent - Applies schema changes to Neo4j database

Responsibilities:
- Create/update node types with properties
- Create/update relationship types
- Create indexes (composite, vector, full-text, single)
- Create constraints (uniqueness, existence)
- Validate implementation
- Support rollback
"""

from typing import Dict, List, Optional
from neo4j import GraphDatabase
from datetime import datetime
import time
import os
import uuid

from state import SchemaDefinition, ImplementationReport, ImplementationChange


class SchemaImplementer:
    """
    Implements schema changes in Neo4j database
    """

    def __init__(self, uri: str = None, username: str = None, password: str = None):
        """
        Initialize Neo4j connection

        Args:
            uri: Neo4j URI (or from env NEO4J_URL)
            username: Neo4j username (or from env NEO4J_USERNAME)
            password: Neo4j password (or from env NEO4J_PASSWORD)
        """
        self.uri = uri or os.getenv("NEO4J_URL")
        self.username = username or os.getenv("NEO4J_USERNAME")
        self.password = password or os.getenv("NEO4J_PASSWORD")

        if not all([self.uri, self.username, self.password]):
            raise ValueError("Neo4j credentials not provided. Set NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    def implement_schema(
        self,
        schema: SchemaDefinition,
        previous_schema: Optional[SchemaDefinition] = None,
        dry_run: bool = False
    ) -> ImplementationReport:
        """
        Implement schema in Neo4j

        Args:
            schema: SchemaDefinition to implement
            previous_schema: Previous schema version (for migrations)
            dry_run: If True, don't actually execute changes

        Returns:
            ImplementationReport with execution details
        """

        print(f"\n{'='*60}")
        print(f"Schema Implementer - {schema['version']}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        print(f"{'='*60}\n")

        changes_applied = []
        validation_results = {}

        # Step 1: Create indexes
        print("📊 Creating indexes...")
        index_changes = self._create_indexes(schema, dry_run)
        changes_applied.extend(index_changes)
        print(f"   ✓ {len(index_changes)} index operations completed")

        # Step 2: Create constraints
        print("🔒 Creating constraints...")
        constraint_changes = self._create_constraints(schema, dry_run)
        changes_applied.extend(constraint_changes)
        print(f"   ✓ {len(constraint_changes)} constraint operations completed")

        # Step 3: Validate schema structure
        print("✅ Validating schema...")
        validation_results = self._validate_schema(schema)

        success_count = sum(1 for c in changes_applied if c["status"] == "success")
        failed_count = len(changes_applied) - success_count

        print(f"\n{'='*60}")
        print(f"IMPLEMENTATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Changes: {len(changes_applied)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"{'='*60}\n")

        # Create implementation report
        report = ImplementationReport(
            implementation_id=str(uuid.uuid4()),
            source_version=previous_schema["version"] if previous_schema else "none",
            target_version=schema["version"],
            timestamp=datetime.utcnow().isoformat(),
            changes_applied=changes_applied,
            validation_results=validation_results,
            rollback_available=not dry_run and failed_count == 0
        )

        return report

    def _create_indexes(self, schema: SchemaDefinition, dry_run: bool) -> List[ImplementationChange]:
        """Create all indexes from schema"""

        changes = []

        for index_def in schema.get("indexes", []):
            change = self._create_single_index(index_def, dry_run)
            changes.append(change)

        return changes

    def _create_single_index(self, index_def: Dict, dry_run: bool) -> ImplementationChange:
        """Create a single index"""

        index_type = index_def.get("type", "single")
        node_label = index_def.get("node_label")
        index_name = index_def.get("name", f"idx_{node_label}_{index_type}")

        start_time = time.time()

        # Build Cypher based on index type
        if index_type == "composite":
            properties = index_def.get("properties", [])
            props_str = ", ".join([f"n.{prop}" for prop in properties])
            cypher = f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{node_label}) ON ({props_str})"

        elif index_type == "vector":
            property_name = index_def.get("property", "embedding")
            dimensions = index_def.get("dimensions", 1536)
            similarity = index_def.get("similarity", "cosine")
            cypher = f"""
            CALL db.index.vector.createNodeIndex(
                '{index_name}',
                '{node_label}',
                '{property_name}',
                {dimensions},
                '{similarity}'
            )
            """

        elif index_type == "fulltext":
            properties = index_def.get("properties", [])
            props_str = ", ".join([f"'{prop}'" for prop in properties])
            cypher = f"""
            CALL db.index.fulltext.createNodeIndex(
                '{index_name}',
                ['{node_label}'],
                [{props_str}]
            )
            """

        elif index_type == "single":
            property_name = index_def.get("property")
            cypher = f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{node_label}) ON (n.{property_name})"

        else:
            return ImplementationChange(
                change_id=str(uuid.uuid4()),
                type="create_index",
                description=f"Unknown index type: {index_type}",
                cypher="",
                status="failed",
                execution_time_ms=0
            )

        # Execute
        status = "success"
        if not dry_run:
            try:
                with self.driver.session() as session:
                    # Vector and fulltext indexes use CALL, others use CREATE
                    if index_type in ["vector", "fulltext"]:
                        # Check if index exists first
                        check_query = "SHOW INDEXES YIELD name WHERE name = $name RETURN count(*) as count"
                        result = session.run(check_query, name=index_name)
                        exists = result.single()["count"] > 0

                        if not exists:
                            session.run(cypher)
                    else:
                        session.run(cypher)

            except Exception as e:
                status = "failed"
                print(f"   ❌ Failed to create index {index_name}: {str(e)}")

        execution_time_ms = int((time.time() - start_time) * 1000)

        return ImplementationChange(
            change_id=str(uuid.uuid4()),
            type="create_index",
            description=f"Create {index_type} index on {node_label}",
            cypher=cypher.strip(),
            status=status,
            execution_time_ms=execution_time_ms
        )

    def _create_constraints(self, schema: SchemaDefinition, dry_run: bool) -> List[ImplementationChange]:
        """Create all constraints from schema"""

        changes = []

        for constraint_def in schema.get("constraints", []):
            change = self._create_single_constraint(constraint_def, dry_run)
            changes.append(change)

        return changes

    def _create_single_constraint(self, constraint_def: Dict, dry_run: bool) -> ImplementationChange:
        """Create a single constraint"""

        constraint_type = constraint_def.get("type", "uniqueness")
        node_label = constraint_def.get("node_label")
        property_name = constraint_def.get("property")
        constraint_name = constraint_def.get("name", f"constraint_{node_label}_{property_name}")

        start_time = time.time()

        # Build Cypher based on constraint type
        if constraint_type == "uniqueness":
            cypher = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{node_label})
            REQUIRE n.{property_name} IS UNIQUE
            """

        elif constraint_type == "existence":
            cypher = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{node_label})
            REQUIRE n.{property_name} IS NOT NULL
            """

        elif constraint_type == "node_key":
            # Node key requires multiple properties
            properties = constraint_def.get("properties", [property_name])
            props_str = ", ".join([f"n.{prop}" for prop in properties])
            cypher = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
            FOR (n:{node_label})
            REQUIRE ({props_str}) IS NODE KEY
            """

        else:
            return ImplementationChange(
                change_id=str(uuid.uuid4()),
                type="create_constraint",
                description=f"Unknown constraint type: {constraint_type}",
                cypher="",
                status="failed",
                execution_time_ms=0
            )

        # Execute
        status = "success"
        if not dry_run:
            try:
                with self.driver.session() as session:
                    session.run(cypher)
            except Exception as e:
                status = "failed"
                print(f"   ❌ Failed to create constraint {constraint_name}: {str(e)}")

        execution_time_ms = int((time.time() - start_time) * 1000)

        return ImplementationChange(
            change_id=str(uuid.uuid4()),
            type="create_constraint",
            description=f"Create {constraint_type} constraint on {node_label}.{property_name}",
            cypher=cypher.strip(),
            status=status,
            execution_time_ms=execution_time_ms
        )

    def _validate_schema(self, schema: SchemaDefinition) -> Dict:
        """Validate schema implementation"""

        validation = {
            "indexes_created": 0,
            "constraints_created": 0,
            "errors": []
        }

        try:
            with self.driver.session() as session:
                # Count indexes
                result = session.run("SHOW INDEXES")
                validation["indexes_created"] = len(list(result))

                # Count constraints
                result = session.run("SHOW CONSTRAINTS")
                validation["constraints_created"] = len(list(result))

        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")

        return validation

    def get_current_schema_stats(self) -> Dict:
        """Get current database statistics"""

        stats = {}

        try:
            with self.driver.session() as session:
                # Node counts by label
                result = session.run("""
                    CALL db.labels() YIELD label
                    CALL apoc.cypher.run(
                        'MATCH (n:' + label + ') RETURN count(n) as count',
                        {}
                    ) YIELD value
                    RETURN label, value.count as count
                """)

                stats["node_counts"] = {record["label"]: record["count"] for record in result}

                # Relationship counts by type
                result = session.run("""
                    CALL db.relationshipTypes() YIELD relationshipType
                    CALL apoc.cypher.run(
                        'MATCH ()-[r:' + relationshipType + ']->() RETURN count(r) as count',
                        {}
                    ) YIELD value
                    RETURN relationshipType, value.count as count
                """)

                stats["relationship_counts"] = {record["relationshipType"]: record["count"] for record in result}

                # Total counts
                result = session.run("MATCH (n) RETURN count(n) as count")
                stats["total_nodes"] = result.single()["count"]

                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                stats["total_relationships"] = result.single()["count"]

        except Exception as e:
            # If APOC not available, use simpler queries
            try:
                with self.driver.session() as session:
                    result = session.run("MATCH (n) RETURN count(n) as count")
                    stats["total_nodes"] = result.single()["count"]

                    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                    stats["total_relationships"] = result.single()["count"]

                    stats["error"] = "APOC not available, limited stats"
            except Exception as e2:
                stats["error"] = str(e2)

        return stats

    def export_schema_documentation(self, schema: SchemaDefinition, output_file: str):
        """Export schema as documentation"""

        with open(output_file, "w") as f:
            f.write(f"# Legal Knowledge Graph Schema - {schema['version']}\n\n")
            f.write(f"**Iteration**: {schema['iteration']}\n\n")

            f.write("## Node Types\n\n")
            for node in schema["nodes"]:
                f.write(f"### {node['label']}\n\n")
                if "description" in node:
                    f.write(f"{node['description']}\n\n")
                f.write("**Properties**:\n")
                for prop_name, prop_def in node.get("properties", {}).items():
                    prop_type = prop_def if isinstance(prop_def, str) else prop_def.get("type", "string")
                    f.write(f"- `{prop_name}`: {prop_type}\n")
                f.write("\n")

            f.write("## Relationships\n\n")
            for rel in schema["relationships"]:
                f.write(f"### {rel['type']}\n\n")
                f.write(f"**From**: {rel['from']} **To**: {rel['to']}\n\n")
                if "description" in rel:
                    f.write(f"{rel['description']}\n\n")
                if "properties" in rel:
                    f.write("**Properties**:\n")
                    for prop_name, prop_def in rel["properties"].items():
                        prop_type = prop_def if isinstance(prop_def, str) else prop_def.get("type", "string")
                        f.write(f"- `{prop_name}`: {prop_type}\n")
                    f.write("\n")

            f.write("## Indexes\n\n")
            for index in schema.get("indexes", []):
                f.write(f"- **{index.get('name')}**: {index.get('type')} on {index.get('node_label')}\n")

            f.write("\n## Constraints\n\n")
            for constraint in schema.get("constraints", []):
                f.write(f"- **{constraint.get('name')}**: {constraint.get('type')} on {constraint.get('node_label')}.{constraint.get('property')}\n")

            f.write(f"\n## RAG Configuration\n\n")
            rag_config = schema.get("rag_configuration", {})
            for key, value in rag_config.items():
                f.write(f"- **{key}**: {value}\n")

        print(f"✅ Schema documentation exported to {output_file}")


def create_schema_implementer() -> SchemaImplementer:
    """Factory function to create SchemaImplementer instance"""
    return SchemaImplementer()
