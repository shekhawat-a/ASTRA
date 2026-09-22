import speech_recognition as sr
import pyttsx3

r = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
cv = voices[0].id  #cv = current voice(david)

def speak(text):
    engine.setProperty("voice",cv)
    engine.say(text)
    print(text)
    engine.runAndWait()

def set_voice(name):
    global cv
    if "orion" in name.lower():
        cv = voices[0].id
    elif "eva" in name.lower():
        cv = voices[1].id

def listen_for_wakeWord():
    while True:
        try:
            with sr.Microphone() as source:
                print("Waiting for wake word....")
                audio = r.listen(source, timeout=4, phrase_time_limit=2)
            text = r.recognize_google(audio)
            print(text)
            if "orion" in text.lower(): return "orion"
            elif "eva" in text.lower(): return "eva"
        
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            pass

        except sr.RequestError:
            speak("No internet connection")

def listen_for_command(name):
    while True:
        try:
            with sr.Microphone() as source:
                print(f"{name.title()} active...")
                audio = r.listen(source,timeout=4, phrase_time_limit= 15)
            text = r.recognize_google(audio)
            return text
        
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            print("Couldn't understand, listening again...")

        except sr.RequestError:
            speak("No internet connection")