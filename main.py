from command import process_command
from voice import speak, set_voice, listen_for_command, listen_for_wakeWord
from memory import clear_history


def main():
    speak("Initializing Astra...")
    speak("Say 'Orion' or 'EVA' to wake me up.")

    flag_voice = True
    current_name = None
    while True:
        name = listen_for_wakeWord()
        set_voice(name)
        if flag_voice:
            speak(f"Hello Master!, I'm {name}, how can I help you?")
            flag_voice = False
            current_name = name

        elif name != current_name:
            speak(f"Switching to {name.title()}.")
            current_name = name
            set_voice(name)
            clear_history()

        while True:
            command = listen_for_command(name)

            EXIT_WORDS = ["stop", "goodbye", "bye", "exit", "quit", "shutdown"]

            if command is None:
                speak("Sorry, I couldn't hear that.")
                continue

            elif any(word in command.lower() for word in EXIT_WORDS):
                speak(f"Going to sleep. Say 'ORION' or 'EVA' to wake me up again.")
                clear_history()
                break

            process_command(command)


if __name__ == "__main__":
    main()