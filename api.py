import requests
import webbrowser
import os
import json
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from deep_translator import GoogleTranslator as gt
from google import genai
from google.genai import types
from groq import Groq
from memory import get_history, clear_history, add_to_memory
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def _extract_text(response):
    if getattr(response, 'text', None):
        return response.text

    candidates = getattr(response, 'candidates', None) or []
    for candidate in candidates:
        parts = getattr(candidate, 'content', None)
        parts = getattr(parts, 'parts', []) or []
        for part in parts:
            if getattr(part, 'text', None):
                return part.text
    return ""



def translate(command):
    try:
        return gt(source="auto", target="en").translate(command)
    except Exception as e:
        print(f"[Translation Error]: {e}")
        return command

def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            art = data.get("articles", [])
            headlines = [article["title"] for article in art[:5]]
            return headlines
        else:
            return f"Failed to retreive headlines: {response.status_code}"
        
    except requests.exceptions.ConnectionError:
        return ["Failed to fetch news. Check your internet connection."]
    except requests.exceptions.Timeout:
        return ["News request timed out. Try again."]
    except Exception as e:
        return [f"News error: {str(e)}"]


    
def get_weather(city):
    try:
        city = city.title().strip()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        return [{"city": city}, data['weather'][0]['description'], data['main']]
        
    except requests.exceptions.ConnectionError:
        return {"error": "No internet connection."}
    except requests.exceptions.Timeout:
        return {"error": "Weather request timed out."}
    except KeyError:
        return {"error": f"Could not find weather data for '{city}'."}
    except Exception as e:
        return {"error": f"Weather error: {str(e)}"}

def email(subject, body, recipient):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, message.as_string())

        return f"Email sent to {recipient} successfully."
    
    except Exception as e:
        print(f"[Email Error]: {e}")
        return f"failed to send email to {recipient}. Please try again."


    
    
def classify_intent(command):
    client = Groq(
    api_key= f"{GROQ_API_KEY}",
    )
    try:
        messages=[
            {
                # here we are setting instructions for the groq that is why system is used as a role
                "role": "system",
                "content": """
                            You are an intent classifier for a voice assistant.
                            Classify the user command into exactly one of these categories:
                            play, weather, news, search, chat, knowledge, email

                            If the category is weather, also extract the city name.
                            if category is play, also extract the song name.
                            if category is news and a city or country is mentioned in it, also extract the city or country name.
                            if category is search, also extract the platforn to search on along with the query to be searched
                            if the category is email, extract the recipient email and generate a polished, professional subject line (4-10 words)
                            Always return only valid JSON like this:
                                        Weather in Jaipur
                                        {"category":"weather","city":"Jaipur"}

                                        Play Believer
                                        {"category":"play","song":"Believer"}

                                        Search Python tutorial on YouTube
                                        {"category":"search","query":"Python tutorial","platform":"youtube"}

                                        Who is Newton?
                                        {"category":"knowledge"}

                                        Send an email to raj@gmail.com for tomorrow's meeting
                                        {"category":"email", "recipient":"raj@gmail.com", "subject":"Agenda and Preparation for Tomorrow's Meeting"}

                                        JSON only. No markdown. No explanation.
                            """
            }]
        history = get_history()
        if history:
            messages.extend(history[-4:])

        messages.append({
                # here groq will respond to the command, no instructions are enlisted here therefore we have used user as a role,
                # it will used instruction listed before to process it
                "role": "user",
                "content": command   # just the raw command, nothing else
            })
        chat_completion = client.chat.completions.create(
            messages = messages,
            model="llama-3.3-70b-versatile"
        )
        response = chat_completion.choices[0].message.content # it is a str - '{category:knowledge}'
        return json.loads(response) # it will convert response into dict

    except Exception as e:
        print(f"[Groq Classification Error]: {e}")
        return {"category": "chat"}

def groq_chat(command):
    client = Groq(
    api_key= f"{GROQ_API_KEY}",
    )
    try:
        messages=[
            {
                "role": "system",
                "content": """
                            You are ASTRA, a smart and friendly voice assistant.
                            Keep all responses short, conversational, and under 3 sentences.
                            You are talking out loud so never use bullet points, markdown, or lists.
                        """
            }
        ]
        messages.extend(get_history())
        messages.append({
            "role": "user",
            "content": command   # just the raw command
        })
        chat_completion = client.chat.completions.create(
            messages = messages,
            model="llama-3.3-70b-versatile" 
        )
        response = chat_completion.choices[0].message.content
        add_to_memory("user", command)
        add_to_memory("assistant", response)
        return response
    
    except Exception as e:
        print(f"[Groq Chat Error]: {e}")
        return "I'm not sure how to respond to that right now."

def gemini_request(prompt):
    client = genai.Client(
        api_key = GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )

    return response.text

def interpret_weather(data, command):
    if isinstance(data, dict) and "error" in data:
        return data["error"]
    
    city = data[0]['city']
    description = data[1]
    main = data[2]

    prompt = f"""You are a voice assistant. The user asked: "{command}"
 
Here is the current weather data for {city}:
- Description: {description}
- Temperature: {main['temp']}°C
- Feels like: {main['feels_like']}°C
- Min: {main['temp_min']}°C, Max: {main['temp_max']}°C
- Humidity: {main['humidity']}%
- Pressure: {main['pressure']} hPa
 
Answer the user's question naturally in 2-3 conversational sentences.
Give practical advice if relevant.
Do not use bullet points or markdown. Speak naturally as if talking out loud."""
    return gemini_request(prompt)

def summarize_news(headlines):
    if not headlines:  # it is true if headlines is empty or none that happens when API dont return any data
        return "I couldn't find any news right now"
    
    prompt = f"""
                You are a voice assistant reading out the news.
                Here are today's top headlines: {headlines}
                
                Summarize these in 3-4 conversational sentences as if speaking out loud.
                Do not use bullet points or markdown. Make it sound natural and engaging.
                """

    return gemini_request(prompt)

def answer_knowledge(question):
    history_text = ""
    history = get_history()

    if history:
        history_text = "\n".join([f"{'User' if m['role'] == 'user' else 'ASTRA'}:{m['content']}"
                                  for m in history[-6:]
                                  ])
    prompt = f"""
                You are a voice assistant answering a question out loud.
                Previous conversation: {history_text} 
                Question: "{question}"
                
                Answer in 2-3 clear, conversational sentences.
                Do not use bullet points, markdown, or lists.
                Speak naturally as if talking to someone.
                """
    response = gemini_request(prompt)
    add_to_memory("user", question)
    add_to_memory("assistant",response)
    return response

def generate_email(subject, recipient):
    if not subject and not recipient:
        return "Please provide both a subject and a recipient email address."
    elif not subject:
        return "Please provide a subject for the email."
    elif not recipient:
        return "Please provide a recipient email address."

    history_text = ""
    history = get_history()

    if history:
        history_text = "\n".join([f"{'User' if m['role'] == 'user' else 'ASTRA'}:{m['content']}"
                                  for m in history[-6:]
                                  ])
        
    prompt = f"""
                Act as an expert copywriter. Write a natural email body based on the context, subject, and recipient.

                Previous Conversation Context:
                {history_text if history_text else "No prior context available."}

                Subject: {subject}
                Recipient: {recipient}
                Output ONLY raw HTML. No conversational filler. No subject line. NO markdown (use <b>, <br>, <p>, <ul> instead)
            """
    body = gemini_request(prompt)
    result = email(subject, body, recipient)

    add_to_memory("user", f"send an email to {recipient} with subject '{subject}'")
    add_to_memory("assistant", f"Email sent to {recipient} with subject '{subject}'")

    return result