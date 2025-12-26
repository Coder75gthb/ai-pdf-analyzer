from groq import Groq
import os

print("Checking GROQ_API_KEY...")
print("KEY:", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Generate 1 simple MCQ on calculus"}
    ],
    max_tokens=100
)

print("Groq response received ✅")
print(response.choices[0].message.content)
