from neo4j import GraphDatabase

# -----------------------------
# Neo4j холболтын тохиргоо
# -----------------------------
URI = "bolt://localhost:7687"  # Windows-н IP
USER = "neo4j"
PASSWORD = "12345678"
ENCRYPTED = False

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD),
    encrypted=ENCRYPTED
)

# -----------------------------
# Шинэ өргөтгөсөн Knowledge Graph өгөгдөл
# -----------------------------
kg_data = [
    # 🚀 Tech & Companies
    {"subject": "Elon Musk", "relation": "FOUNDED", "object": "SpaceX", "sub_type":"Person", "obj_type":"Company"},
    {"subject": "Elon Musk", "relation": "FOUNDED", "object": "Tesla", "sub_type":"Person", "obj_type":"Company"},
    {"subject": "SpaceX", "relation": "LAUNCHED", "object": "Falcon 9", "sub_type":"Company", "obj_type":"Rocket"},
    {"subject": "SpaceX", "relation": "OPERATES", "object": "Starlink", "sub_type":"Company", "obj_type":"Project"},
    {"subject": "Tesla", "relation": "PRODUCES", "object": "Electric Car", "sub_type":"Company", "obj_type":"Product"},
    {"subject": "OpenAI", "relation": "CREATED", "object": "ChatGPT", "sub_type":"Organization", "obj_type":"AI_Model"},
    {"subject": "ChatGPT", "relation": "BASED_ON", "object": "Transformer Architecture", "sub_type":"AI_Model", "obj_type":"Technology"},
    {"subject": "OpenAI", "relation": "COFOUNDED_BY", "object": "Elon Musk", "sub_type":"Organization", "obj_type":"Person"},

    # 🌍 Locations & Projects
    {"subject": "SpaceX", "relation": "HEADQUARTERED_IN", "object": "Hawthorne", "sub_type":"Company", "obj_type":"City"},
    {"subject": "Tesla", "relation": "HEADQUARTERED_IN", "object": "Austin", "sub_type":"Company", "obj_type":"City"},
    {"subject": "Starlink", "relation": "PROVIDES", "object": "Satellite Internet", "sub_type":"Project", "obj_type":"Service"},

    # 📈 Relationships between technologies
    {"subject": "Falcon 9", "relation": "USED_FOR", "object": "Satellite Launch", "sub_type":"Rocket", "obj_type":"Purpose"},
    {"subject": "Electric Car", "relation": "USES", "object": "Lithium-ion Battery", "sub_type":"Product", "obj_type":"Component"},
    {"subject": "ChatGPT", "relation": "USES", "object": "LLM Technology", "sub_type":"AI_Model", "obj_type":"Technology"},
]

# -----------------------------
# Neo4j-д оруулах функц
# -----------------------------
def insert_kg(triples):
    with driver.session() as session:
        for triple in triples:
            session.run(
                f"""
                MERGE (a:{triple['sub_type']} {{name: $sub}})
                MERGE (b:{triple['obj_type']} {{name: $obj}})
                MERGE (a)-[:{triple['relation']}]->(b)
                """,
                sub=triple["subject"],
                obj=triple["object"]
            )
    print("✅ Knowledge Graph амжилттай Neo4j-д орууллаа.")

# -----------------------------
# Script ажиллуулах
# -----------------------------
if __name__ == "__main__":
    insert_kg(kg_data)
    driver.close()
