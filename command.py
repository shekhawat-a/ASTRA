import webbrowser
from yt_dlp import YoutubeDL
from voice import speak
from memory import add_to_memory
from api import (
    generate_email,
    translate,
    get_news,
    get_weather,
    classify_intent,
    groq_chat,
    gemini_request,
    interpret_weather,
    summarize_news,
    answer_knowledge
)
first_time = True

def play(song):
    with YoutubeDL({"quiet": True}) as ydl:
        result = ydl.extract_info(f"ytsearch:{song}", download=False)
    video = result["entries"][0]    
    url = video["webpage_url"]
    speak(f"Playing {song}")
    webbrowser.open_new(url)
    add_to_memory("user", f"Play {song}")
    add_to_memory("assistant", f"Playing {song}")

def search(query, platform):
    if platform.lower() == "youtube":
        speak(f"Searching {query} on YouTube")
        webbrowser.open_new(f"https://www.youtube.com/results?search_query={query}")
    elif platform.lower() == "google":
        speak(f"Searching {query} on Google")
        webbrowser.open_new(f"https://www.google.com/search?q={query}")

def open_website(c):
    if "youtube" in c:
        speak("Opening YouTube")
        webbrowser.open_new("https://www.youtube.com")

    elif "google" in c:
        speak("Opening Google")
        webbrowser.open_new("https://www.google.com")

    elif "linkedin" in c:
        speak("Opening Linkedin")
        webbrowser.open_new("https://www.linkedin.com")

    elif "gmail" in c:
        speak("Opening Gmail")
        webbrowser.open_new("https://mail.google.com")

    elif "outlook" in c:
        speak("Opening Outlook")
        webbrowser.open_new("https://outlook.live.com")

    elif "zoho mail" in c or "zohomail" in c:
        speak("Opening Zoho Mail")
        webbrowser.open_new("https://mail.zoho.com")

    elif "hackerrank" in c:
        speak("Opening HackerRank")
        webbrowser.open_new("https://www.hackerrank.com")

    elif "leetcode" in c:
        speak("Opening LeetCode")
        webbrowser.open_new("https://leetcode.com")

    elif "netflix" in c:
        speak("Opening Netflix")
        webbrowser.open_new("https://www.netflix.com")

    elif "spotify" in c:
        speak("Opening Spotify")
        webbrowser.open_new("https://open.spotify.com")

    elif "prime video" in c or "primevideo" in c:
        speak("Opening Prime Video")
        webbrowser.open_new("https://www.primevideo.com")
    
def llm(result, command):
    global first_time
    intent = result['category']

    if intent == "weather":
        city = result.get('city', None)
        if not city:
            speak("Which city's weather would you like to know?")
            return
        if first_time:
            speak("Fetching the weather data...")
            first_time = False
        data = get_weather(city)
        response = interpret_weather(data,command)
        speak(response)
        add_to_memory("user", command)
        add_to_memory("assistant", response)

    elif intent == "news":
        if first_time:
            speak("Fetching the latest news...")
            first_time = False
        data = get_news()
        response = summarize_news(data)
        speak(response)
        add_to_memory("user", command)
        add_to_memory("assistant", response)

    elif intent == "chat":
        speak(groq_chat(command))

    elif intent == "knowledge":
        if first_time:
            speak("Let me think about that...")
            first_time = False
        speak(answer_knowledge(command))

    elif intent == "email":
        if not result.get('subject') or not result.get('recipient'):
            speak("I need both a subject and a recipient to generate an email. Please provide them.")
            return
        subject = result['subject']
        recipient = result['recipient']
        speak("Genrating the email...")
        speak(generate_email(subject, recipient))
        

def process_command(command):
    result = classify_intent(command)
    intent = result['category']
    
    c = translate(command).lower()
    
    if "open" in c:
        open_website(c)

    elif intent == "search":
        query = result['query']
        platform = result['platform']
        search(query, platform)
    
    elif intent == "play":
        song = result['song']
        play(song)
    
    else: llm(result, command)