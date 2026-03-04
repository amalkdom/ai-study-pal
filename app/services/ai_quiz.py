import openai
import json
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_quiz(topic):

    prompt = f"""
Generate 5 multiple choice questions about {topic}.
Return JSON format:

[
{{"question":"...","options":["A","B","C","D"],"answer":"A"}}
]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    content = response.choices[0].message.content

    return json.loads(content)
