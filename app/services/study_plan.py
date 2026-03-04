import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_study_plan(topics):

    topic_text = ", ".join(topics)

    prompt = f"""
Create a 5 day study plan for learning these topics:

{topic_text}

Return simple steps for each day.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
