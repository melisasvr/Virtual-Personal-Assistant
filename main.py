import sqlite3
import time
import json
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
import threading

# Set up memory to track conversation context
history = ChatMessageHistory()
pending_task = None  # To store task waiting for a time

# Preference tracker (stored in memory and file)
preferences = {"reminder_times": {}}

# Database setup for tasks
def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, task TEXT, time TEXT)''')
    conn.commit()
    conn.close()

# Load preferences from file
def load_preferences():
    global preferences
    try:
        with open("preferences.json", "r") as f:
            preferences = json.load(f)
    except FileNotFoundError:
        preferences = {"reminder_times": {}}

# Save preferences to file
def save_preferences():
    with open("preferences.json", "w") as f:
        json.dump(preferences, f)

# Add a task to the database
def add_task(task, time):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task, time) VALUES (?, ?)", (task, time))
    conn.commit()
    conn.close()

# Delete a task from the database
def delete_task(task):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE task = ?", (task,))
    conn.commit()
    conn.close()
    return c.rowcount > 0  # Return True if a task was deleted

# List all tasks
def list_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT task, time FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return tasks

# Update user preferences
def update_preferences(time):
    if time in preferences["reminder_times"]:
        preferences["reminder_times"][time] += 1
    else:
        preferences["reminder_times"][time] = 1
    save_preferences()

# Suggest a preferred time
def suggest_time():
    if preferences["reminder_times"]:
        most_common = max(preferences["reminder_times"], key=preferences["reminder_times"].get)
        return f"Would you like it set for {most_common}, your usual time?", most_common
    return "When would you like the reminder?", None

# Check reminders and notify
def check_reminders():
    while True:
        current_time = datetime.now().strftime("%I:%M %p").lower()
        tasks = list_tasks()
        for task, task_time in tasks:
            if task_time.lower() == current_time:
                print(f"\nReminder: It's time to '{task}'!")
        time.sleep(60)  # Check every minute

# Parse user input (rule-based)
def process_input(user_input):
    global pending_task
    user_input = user_input.lower().strip()
    
    # Save conversation context
    history.add_message(HumanMessage(content=user_input))
    
    # Handle "yes" for a pending task
    if pending_task and user_input in ["yes", "y"]:
        suggestion = preferences["reminder_times"]
        most_common = max(suggestion, key=suggestion.get)
        add_task(pending_task, most_common)
        update_preferences(most_common)
        response = f"Reminder set: '{pending_task}' at {most_common}"
        pending_task = None
        history.add_message(AIMessage(content=response))
        return response
    
    # Clear pending task if user starts a new command
    pending_task = None
    
    if "remind me" in user_input:
        try:
            task = user_input.split("to")[1].split("at")[0].strip()
            time = user_input.split("at")[1].strip()
            add_task(task, time)
            update_preferences(time)
            response = f"Reminder set: '{task}' at {time}"
            history.add_message(AIMessage(content=response))
            return response
        except IndexError:
            task = user_input.split("to")[1].strip()
            suggestion, suggested_time = suggest_time()
            pending_task = task
            response = f"I need a time for '{task}'. {suggestion}"
            history.add_message(AIMessage(content=response))
            return response
    
    elif "delete reminder" in user_input:
        try:
            task = user_input.split("delete reminder")[1].strip().strip("'\"")  # Handle quotes if used
            if delete_task(task):
                response = f"Deleted reminder: '{task}'"
            else:
                response = f"No reminder found for '{task}'"
            history.add_message(AIMessage(content=response))
            return response
        except IndexError:
            response = "Please specify a task to delete, e.g., 'delete reminder call john'"
            history.add_message(AIMessage(content=response))
            return response
    
    elif "list tasks" in user_input or "show reminders" in user_input:
        tasks = list_tasks()
        if tasks:
            response = "\n".join([f"- {task} at {time}" for task, time in tasks])
            history.add_message(AIMessage(content=response))
            return response
        response = "No tasks set yet."
        history.add_message(AIMessage(content=response))
        return response
    
    elif "hello" in user_input or "hi" in user_input:
        response = "Hello! How can I assist you today?"
        history.add_message(AIMessage(content=response))
        return response
    
    else:
        response = "Sorry, I didn’t understand that. Try 'remind me to [task] at [time]', 'list tasks', or 'delete reminder [task]'."
        history.add_message(AIMessage(content=response))
        return response

# Main interaction loop
def run_assistant():
    init_db()
    load_preferences()
    print("Hello! I'm your Virtual Personal Assistant. How can I help you?")
    print("You can say 'exit' or 'quit' to stop me anytime.")
    
    # Start reminder checking in a separate thread
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()
    
    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        response = process_input(user_input)
        print(response)

if __name__ == "__main__":
    run_assistant()