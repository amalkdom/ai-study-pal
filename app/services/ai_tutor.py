import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_tutor(question):

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are a helpful AI tutor."},
            {"role":"user","content":question}
        ]
    )

    return response.choices[0].message.content
