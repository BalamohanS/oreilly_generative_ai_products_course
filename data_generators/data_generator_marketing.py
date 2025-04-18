import os
import openai
import json
import random

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

personas = [
    {"id": 1, "name": "Conscious Explorer"},
    {"id": 2, "name": "Thrill Seeker"},
    {"id": 3, "name": "Cultural Curator"},
    {"id": 4, "name": "Wellness Wanderer"},
    {"id": 5, "name": "Nomadic Naturalist"},
    {"id": 6, "name": "Solo Pathfinder"},
    {"id": 7, "name": "Family Trailblazer"}
]

prompt_personas = """
Generate a JSON array of detailed descriptions for the following personas. Each object in the array should include:
- id: the same id as provided
- name: the same name as provided
- description: a detailed explanation covering personality, motivations, interests, and travel preferences
- traits: an array of 3-5 key personality traits (for example, "adventurous", "curious", "sociable")
- interests: an array of 3-5 interests related to this persona (such as "hiking", "local cuisine", "cultural festivals")
- lifestyle: a brief explanation of their typical lifestyle and travel habits

The personas to include are:
1: Conscious Explorer
2: Thrill Seeker
3: Cultural Curator
4: Wellness Wanderer
5: Nomadic Naturalist
6: Solo Pathfinder
7: Family Trailblazer

Output only the JSON array with no additional text, explanations, or markdown formatting.
"""

prompt_tours = """
Generate a JSON array of exactly 50 fictional eco-adventure tour packages. Each tour should include the following fields:

- id: a unique integer starting from 1
- name: the name of the tour
- region: the general region (e.g., Scandinavia, South America, Southeast Asia)
- description: a 5-6 sentence description of the tour
- price: a realistic price in USD (between $1000 and $5000)
- duration_days: number of days (between 3 and 21)
- start_date: a future start date in YYYY-MM-DD format
- features: a list of 3–5 keywords (e.g., "wildlife", "photography", "hiking")

Output only the JSON array, no explanations or text.
"""

def generate_data(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    json_data = response.choices[0].message.content

    try:
        tours = json.loads(json_data)

        with open("data/marketing_dataset.json", "w") as f:
            json.dump(tours, f, indent=2)

    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw output:")
        print(json_data)


def main():
    generate_data(prompt_tours)

if __name__ == "__main__":
    main()
