# Exercise 1 solution

```
python -m venv venv
source venv/bin/activate
```

```
pip install fastapi uvicorn openai
```

```
pip freeze > requirements.txt
```

```python
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
```

Note: This would work if OPENAI_API_KEY is already set in your environment. If not, you can set it in the terminal using:

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

```Dockerfile
# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```
docker build -t fastapi-openai .
docker run -e OPENAI_API_KEY=your-key-here -p 8000:8000 fastapi-openai
```
