from neo4j import GraphDatabase
from groq import Groq
import re

# -----------------------------
# Neo4j холболт
# -----------------------------
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"  # өөрийн Neo4j password
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD), encrypted=False)

# -----------------------------
# Groq LLM client
# -----------------------------
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# -----------------------------
# Multi-hop Graph context татах функц
# -----------------------------
# def extract_entity(question):
#     # Жишээ: first 2 words as entity
#     words = question.split()
#     return " ".join(words[:2])

def extract_entity(question):
    # District code (жишээ: C6, D14 гэх мэт) хайна
    match = re.search(r"\b[A-Z]\d+\b", question.upper())
    if match:
        return match.group(0)
    # Хэрвээ олдохгүй бол хамгийн сүүлчийн үгийг буцаана
    return question.split()[-1]


def get_graph_context(question, db="test"):
    entity = extract_entity(question)
    with driver.session(database=db) as session:
        result = session.run(
            """
            MATCH (d:District {name:$entity})<-[:OCCURRED_IN]-(i:Incident)
            RETURN d.name AS district,
                   i.id AS incident_id,
                   i.зөрчлийн_бүлэг AS offense_group,
                   i.зөрчлийн_тайлбар AS description,
                   i.долоо_хоногийн_өдөр AS day,
                   i.сар AS month,
                   i.он AS year,
                   i.цаг AS hour,
                   i.Гудамж AS street,
                   i.байршил AS location
            LIMIT 20
            """,
            entity=entity
        )

        rows = []
        for record in result:
            rows.append(
                f"District {record.get('district')} - Incident {record.get('incident_id')}: "
                f"{record.get('offense_group')} ({record.get('description')}), "
                f"{record.get('day')} {record.get('month')}/{record.get('year')} @ {record.get('hour')} цаг, "
                f"Гудамж: {record.get('street')}, Байршил: {record.get('location')}"
            )

        context = "\n".join(rows) if rows else "Холбогдох incident олдсонгүй."
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

        # KG-д тулгуурласан multi-hop context татах
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
