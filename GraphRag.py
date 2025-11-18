import networkx as nx
from groq import Groq
import re
import os

client = Groq(api_key= os.getenv("GROQ_API_KEY"))  # <-- энд өөрийн түлхүүрээ оруул

# 🔹 1. Файлаас текст унших
with open("ddata.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 🔹 2. Энгийн triple extraction (жишээний байдлаар)
pattern = r"(\b[A-Z][a-zA-Z0-9\s]*)\s+(founded|created|launched|produces|developed|is|owns|friend)\s+(\b[A-Z][a-zA-Z0-9\s]*)"
triples = re.findall(pattern, text)

# 🔹 3. Graph үүсгэх
G = nx.DiGraph()
for subj, rel, obj in triples:
    G.add_edge(subj.strip(), obj.strip(), relation=rel)

print(f"🧩 {len(triples)} холбоо илэрлээ.")
for t in triples:
    print("   ", t)

# 🔹 4. Хэрэглэгчийн асуулт
question = input("\n🧑‍💻 Асуулт: ")

# 🔹 5. Graph reasoning — хялбар хувилбар
neighbors = []
for node in G.nodes():
    if question.lower() in node.lower():
        for nbr in G.neighbors(node):
            rel = G[node][nbr]['relation']
            neighbors.append(f"{node} —[{rel}]→ {nbr}")

context = "\n".join(neighbors) if neighbors else "Холбогдсон entity олдсонгүй."

# 🔹 6. LLM рүү илгээх
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Та мэдлэгийн граф дээр тулгуурлан reasoning хийдэг туслах юм."},
        {"role": "user", "content": f"Graph мэдээлэл:\n{context}\n\nАсуулт: {question}"}
    ],
    temperature=0.6,
    max_tokens=800,
)

print("\n🤖:", response.choices[0].message.content)
