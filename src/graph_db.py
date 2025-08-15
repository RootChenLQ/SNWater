import os
from neo4j import GraphDatabase, exceptions

NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

class GraphDB:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("GraphDB: Successfully connected to Neo4j.")
        except (exceptions.AuthError, exceptions.ServiceUnavailable) as e:
            print(f"GraphDB: Connection failed: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def search_graph(self, query_term: str):
        """
        Searches for nodes containing the query_term and returns the
        subgraph of all matching nodes and their direct relationships.
        """
        if not self.driver:
            return {"nodes": [], "links": []}

        # This query finds nodes that have a 'name' property containing the query term (case-insensitive).
        # It then returns those nodes, plus any nodes they are connected to, and the relationships between them.
        # This gives us a small subgraph around the search results.
        query = """
        MATCH (n)
        WHERE n.name CONTAINS $term OR n.description CONTAINS $term OR n.id CONTAINS $term
        // Find all relationships connected to the matched nodes
        OPTIONAL MATCH (n)-[r]-(m)
        // Return the distinct nodes and relationships
        WITH COLLECT(DISTINCT n) + COLLECT(DISTINCT m) as all_nodes, COLLECT(DISTINCT r) as all_rels
        UNWIND all_nodes as node
        UNWIND all_rels as rel
        RETURN DISTINCT node, rel
        """

        nodes = []
        links = []
        node_ids = set()

        with self.driver.session() as session:
            result = session.run(query, term=query_term)
            for record in result:
                # Process node
                node_data = record["node"]
                if node_data and node_data.id not in node_ids:
                    nodes.append({
                        "id": node_data.get("id"),
                        "label": list(node_data.labels)[0],
                        "properties": dict(node_data)
                    })
                    node_ids.add(node_data.id)

                # Process relationship
                rel_data = record["rel"]
                if rel_data:
                    links.append({
                        "source": rel_data.start_node.get("id"),
                        "target": rel_data.end_node.get("id"),
                        "type": rel_data.type
                    })

        # Deduplicate links
        unique_links = [dict(t) for t in {tuple(d.items()) for d in links}]

        return {"nodes": nodes, "links": unique_links}

    def update_node_properties(self, node_id: str, properties: dict):
        """
        Updates the properties of a specific node identified by its ID.
        """
        if not self.driver:
            return {"error": "Database not connected"}

        # We must not allow changing the unique ID
        if "id" in properties:
            del properties["id"]

        query = """
        MATCH (n {id: $node_id})
        SET n += $properties
        RETURN n
        """

        result = self._execute_query(query, node_id=node_id, properties=properties)
        if result:
            return {"status": "success", "data": dict(result[0]["n"])}
        else:
            return {"status": "error", "message": "Node not found or update failed"}

    def find_rules_for_station(self, station_name: str):
        """
        Finds all rules and their descriptions associated with a given hydropower station.
        """
        if not self.driver:
            return []

        query = """
        MATCH (s:HydropowerStation)-[:HAS_RULE]->(r:DispatchRule)
        WHERE s.name CONTAINS $station_name
        RETURN r.description AS rule_description
        """

        with self.driver.session() as session:
            result = session.run(query, station_name=station_name)
            return [record["rule_description"] for record in result]

# Example usage (for testing)
if __name__ == '__main__':
    import json
    db = GraphDB(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    if db.driver:
        # Example search using the dummy data we created
        print("--- Searching for node ---")
        search_result = db.search_graph("淋部沟")
        print(json.dumps(search_result, indent=2, ensure_ascii=False))

        # Example update
        print("\n--- Updating node properties ---")
        update_result = db.update_node_properties("station-lbg-1", {"capacity_mw": 150, "river": "大渡河支流"})
        print(json.dumps(update_result, indent=2, ensure_ascii=False))

        db.close()
