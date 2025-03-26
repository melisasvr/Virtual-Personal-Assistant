# Virtual Personal Assistant

A simple, offline AI-powered personal assistant built with Python. It helps you manage tasks by setting reminders, learning your preferences, and notifying you when it’s time to act, all without relying on external APIs.

## Features
- **Set Reminders**: Add tasks with specific times (e.g., "Remind me to call John at 3 PM").
- **Preference Learning**: Suggests your most-used time when none is provided (e.g., "Remind me to email Sarah" → suggests "3 PM" if that’s common).
- **List Tasks**: View all reminders with "list tasks" or "show reminders".
- **Delete Tasks**: Remove reminders with "delete reminder [task]" (e.g., "delete reminder call john").
- **Time Notifications**: Alerts you when a reminder’s time matches the current system time.
- **Persistent Storage**: Tasks are saved in `tasks.db`, and preferences are stored in `preferences.json`.
- **Exit Gracefully**: Type "exit" or "quit" to stop the program.

## Requirements
- Python 3.6+
- Required packages:
  - `langchain` (for conversation memory)

## Installation
1. Clone or download this project to your local machine.
2. Install dependencies:
   ```bash
   pip install langchain

3. Run the assistant:
- python main.py

## Usage
1. Start the program and follow the prompts.
- Example commands:
> Remind me to call John at 3 PM
Reminder set: 'call john' at 3 pm
> Remind me to email Sarah
I need a time for 'email sarah'. Would you like it set for 3 pm, your usual time?
> yes
Reminder set: 'email sarah' at 3 pm
> list tasks
- call john at 3 pm
- email sarah at 3 pm
> delete reminder call john
Deleted reminder: 'call john'
> exit
- Goodbye!
- Notifications will appear automatically when the system time matches a task’s time.

## Files
- main.py: The main script containing the assistant’s logic.
- tasks.db: SQLite database storing reminders (created automatically).
- preferences.json: File storing your time preferences (created automatically).

## Notes
- The assistant checks for reminders every minute in the background.
- All data is stored locally—no internet required.
- Time format should match your system’s 12-hour clock (e.g., "3 PM", "10:45 AM")


