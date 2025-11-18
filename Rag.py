from groq import Groq

# API key-г environment variable эсвэл хувьсагчид хадгална
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

# Файлаас мэдээлэл уншина - алдааг засах
try:
    with open("data.txt", "r", encoding="utf-8", errors="ignore") as f:
        context = f.read()
    
    # Surrogate characters-ийг цэвэрлэх
    context = context.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    
except Exception as e:
    print(f"❌ Файл унших алдаа: {e}")
    exit(1)

question = input("🧑‍💻 Асуулт: ")

# Question-ийг мөн цэвэрлэх
question = question.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

# System болон user message-ийг тусад нь ашиглах
try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Илүү найдвартай модель
        messages=[
            {
                "role": "system",
                "content": "Та өгөгдсөн мэдээлэлд үндэслэн асуултад хариулдаг туслах юм."
            },
            {
                "role": "user",
                "content": f"Мэдээлэл:\n\n{context}\n\nАсуулт: {question}\n\nДээрх мэдээлэлд үндэслэн асуултад хариул."
            }
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    
    print("🤖:", response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ API дуудлагын алдаа: {e}")