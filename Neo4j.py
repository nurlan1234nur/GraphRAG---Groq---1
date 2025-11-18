from neo4j import GraphDatabase
from groq import Groq

# -----------------------------
# Neo4j холболт
# -----------------------------
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"  # өөрийн Neo4j password
driver = GraphDatabase.driver(URI, auth=("neo4j", "12345678"), encrypted=False)  # TLS=True

# -----------------------------
# Groq LLM client
# -----------------------------
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# -----------------------------
# Graph context татах функц
# -----------------------------
def get_graph_context(question):
    with driver.session() as session:
        # Simple pattern: question-д байгаа keyword-р connected nodes авах
        result = session.run(
            """
            MATCH (n)-[r]->(m)
            WHERE toLower(n.name) CONTAINS toLower($q) 
               OR toLower(m.name) CONTAINS toLower($q)
            RETURN n.name AS subject, type(r) AS relation, m.name AS object
            """,
            q=question
        )
        triples = [f"{record['subject']} -[{record['relation']}]-> {record['object']}" for record in result]
        context = "\n".join(triples) if triples else "Холбогдох entity олдсонгүй."
        return context

# -----------------------------
# Main loop
# -----------------------------
if __name__ == "__main__":
    while True:
        question = input("🧑‍💻 Асуулт: ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        
        context = get_graph_context(question)
        
        # LLM-д context явуулах
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":"Та өгөгдсөн KG-д үндэслэн асуултад хариулдаг туслах юм."},
                {"role":"user","content":f"Graph context:\n{context}\n\nАсуулт: {question}"}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        print("🤖", response.choices[0].message.content)
