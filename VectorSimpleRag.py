from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 🔑 Groq API key
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# 🔹 1. Мэдээлэл ачаалах
with open("data.txt", "r", encoding="utf-8", errors="ignore") as f:
    texts = f.read().split("\n")

# 🔹 2. Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts)

# 🔹 3. FAISS индекс үүсгэх
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

# 🔹 4. Хэрэглэгчийн асуулт
question = input("🧑‍💻 Асуулт: ")
q_emb = model.encode([question])
_, I = index.search(q_emb, k=3)  # top-3 холбоотой өгүүлбэр

# 🔹 5. Холбогдох өгүүлбэрүүдийг татах
context = "\n".join([texts[i] for i in I[0]])

# 🔹 6. LLM рүү илгээх
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "Та өгөгдсөн мэдлэг дээр үндэслэн асуултад хариулдаг туслах юм."},
        {"role": "user", "content": f"Контекст:\n{context}\n\nАсуулт: {question}"}
    ],
    temperature=0.7,
    max_tokens=800,
)

print("\n🤖:", response.choices[0].message.content)
