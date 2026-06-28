chat_history = []
MAX = 10

def add_to_memory(role, command):
    chat_history.append({
        'role': role,
        'content': command
    })

    if len(chat_history) > MAX*2:
        chat_history.pop(0)  # it will first remove the user command
        chat_history.pop(0)  # then it will remove the assistant reply from the list

def get_history():
    return chat_history

def clear_history():
    chat_history.clear()