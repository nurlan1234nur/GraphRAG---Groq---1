from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("💬 Simple Groq Chat — 'exit' гэж бичиж гарах боломжтой")

while True:
    q = input("\n🧑‍💻 Асуулт: ").strip()
    if q.lower() in ["exit", "quit"]:
        break

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": q}],
        temperature=1,
        max_completion_tokens=512,
        top_p=1,
        reasoning_effort="medium",
    )

    print("\n🤖 Хариулт:", completion.choices[0].message.content)
