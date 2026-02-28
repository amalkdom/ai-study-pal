import openai
from flask import current_app
from youtube_transcript_api import YouTubeTranscriptApi

def ask_ai(prompt):
    openai.api_key = current_app.config["OPENAI_API_KEY"]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def generate_study_plan(topic, hours):
    prompt = f"""
    Create a structured Pomodoro study plan for {topic}
    for {hours} hours including breaks and focus sessions.
    """
    return ask_ai(prompt)

def generate_quiz(topic, notes):
    prompt = f"""
    Generate 5 MCQs with 4 options each.
    Topic: {topic}
    Notes: {notes}
    Provide correct answers clearly.
    """
    return ask_ai(prompt)

def summarize_text(text):
    return ask_ai(f"Summarize in structured academic format:\n{text}")

def summarize_youtube(link):
    video_id = link.split("v=")[1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([x["text"] for x in transcript])
    return ask_ai(f"Summarize this lecture:\n{text}")
