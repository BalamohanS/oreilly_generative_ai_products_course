from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI()

@app.get("/haiku")
def get_haiku():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a haiku about recursion in programming."
            }
        ]
    )
    return {"haiku": completion.choices[0].message.content}