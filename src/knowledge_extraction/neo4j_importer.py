import os
import json
from neo4j import GraphDatabase, exceptions

# It's recommended to use environment variables for credentials in production
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

class Neo4jImporter:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connection
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j.")
        except exceptions.AuthError:
            print(f"Authentication failed for user '{user}'. Please check credentials.")
            self.driver = None
        except exceptions.ServiceUnavailable:
            print(f"Could not connect to Neo4j at {uri}. Please ensure the database is running.")
            self.driver = None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def _execute_query(self, query, parameters=None):
        if not self.driver:
            return None
        with self.driver.session() as session:
            try:
                result = session.run(query, parameters)
                return [record for record in result]
            except Exception as e:
                print(f"Error executing query: {e}")
                return None

    def import_entities(self, entities):
        """Imports a list of entities into Neo4j."""
        print(f"Importing {len(entities)} entities...")
        for entity in entities:
            node_type = entity.get("type")
            properties = entity.get("properties", {})
            node_id = properties.get("id")

            if not node_type or not node_id:
                print(f"Skipping entity with missing type or id: {entity}")
                continue

            query = f"""
            MERGE (n:{node_type} {{id: $id}})
            SET n += $props
            """
            self._execute_query(query, parameters={"id": node_id, "props": properties})
        print("Entity import complete.")

    def import_relationships(self, relationships):
        """Imports a list of relationships into Neo4j."""
        print(f"Importing {len(relationships)} relationships...")
        for rel in relationships:
            rel_type = rel.get("type")
            source_id = rel.get("source")
            target_id = rel.get("target")

            if not all([rel_type, source_id, target_id]):
                print(f"Skipping relationship with missing data: {rel}")
                continue

            query = f"""
            MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
            MERGE (a)-[r:{rel_type}]->(b)
            """
            self._execute_query(query, parameters={"source_id": source_id, "target_id": target_id})
        print("Relationship import complete.")

    def import_from_json(self, json_path):
        """Reads a JSON file and imports its entities and relationships."""
        if not self.driver:
            return
        if not os.path.exists(json_path):
            print(f"Error: JSON file not found at {json_path}")
            return

        print(f"Reading from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entities = data.get("entities", [])
        relationships = data.get("relationships", [])

        if entities:
            self.import_entities(entities)
        if relationships:
            self.import_relationships(relationships)

    def clear_database(self):
        """Clears all nodes and relationships from the database."""
        if not self.driver:
            return
        print("Clearing the Neo4j database...")
        query = "MATCH (n) DETACH DELETE n"
        self._execute_query(query)
        print("Database cleared.")

    def verify_import(self):
        """Counts the nodes in the database to verify the import."""
        if not self.driver:
            return
        print("\nVerifying import...")
        query = "MATCH (n) RETURN count(n) AS node_count"
        result = self._execute_query(query)
        if result:
            count = result[0]["node_count"]
            print(f"Verification complete. Found {count} nodes in the database.")
            return count
        else:
            print("Verification failed.")
            return 0


if __name__ == '__main__':
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    if importer.driver:
        importer.clear_database()

        json_file_path = 'data/extracted_knowledge.json'
        importer.import_from_json(json_file_path)

        importer.verify_import()

        importer.close()
