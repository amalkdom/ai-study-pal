from openai import OpenAI
from flask import current_app

def get_client():
    api_key = current_app.config["OPENAI_API_KEY"]
    return OpenAI(api_key=api_key)

def ask_ai(prompt):
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
