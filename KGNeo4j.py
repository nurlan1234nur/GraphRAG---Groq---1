## ene code bol Neo4j code iin zowhon kg ashiglaj hariuldag huwilbar ni baina, omnoh ni ooriin datasetee ashiglaad nemelt medeelel oruuldag.

from neo4j import GraphDatabase
from groq import Groq

# -----------------------------
# Neo4j холболт
# -----------------------------
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"  # өөрийн Neo4j password
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), encrypted=False)  # TLS=False

# -----------------------------
# Groq LLM client
# -----------------------------
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# -----------------------------
# Graph context татах функц (KG-only)
# -----------------------------
def get_graph_context(question):
    with driver.session() as session:
        # Question-д байгаа keyword-үүдээр filter хийх
        keywords = [word.lower() for word in question.split()]
        result = session.run(
            """
            MATCH (n)-[r]->(m)
            WHERE toLower(n.name) IN $keywords OR toLower(m.name) IN $keywords
            RETURN n.name AS subject, type(r) AS relation, m.name AS object
            """,
            keywords=keywords
        )
        triples = [f"{record['subject']} -[{record['relation']}]-> {record['object']}" for record in result]
        context = "\n".join(triples) if triples else "Холбогдох entity олдсонгүй."
        return context

# -----------------------------
# Main loop
# -----------------------------
if __name__ == "__main__":
    print("💡 'exit' гэж бичвэл програм дуусна.")
    while True:
        question = input("🧑‍💻 Асуулт: ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        
        # KG-д тулгуурласан context татах
        context = get_graph_context(question)
        
        # LLM-д context явуулах (KG-only)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role":"system",
                    "content":"Та зөвхөн өгөгдсөн Knowledge Graph-д байгаа мэдээллийг ашиглаж хариулна. Гадна мэдлэг ашиглахгүй."
                },
                {
                    "role":"user",
                    "content":f"Graph context:\n{context}\n\nАсуулт: {question}"
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        print("🤖", response.choices[0].message.content)
