import re
from backend.models import Reminder

def process_reminder_command(command, user_id):
    """
    Parses commands like 'set reminder buy milk at 5 PM'
    or 'view reminders' and performs operations on the database.
    """
    c = command.lower().strip()

    # Rule 1: View reminders
    if c in ["view reminders", "show reminders", "show my reminders", "list reminders", "reminders"]:
        reminders = Reminder.get_all(user_id)
        active_reminders = [r for r in reminders if r["status"] == "active"]
        if not active_reminders:
            return {
                "type": "text",
                "data": "You have no active reminders."
            }
        
        lines = []
        for i, r in enumerate(active_reminders, 1):
            lines.append(f"{i}. {r['text']} at {r['time']}")
        return {
            "type": "text",
            "data": "Here are your active reminders:\n" + "\n".join(lines)
        }

    # Rule 2: Set reminder
    # Matches: set reminder [text] at [time] or remind me to [text] at [time]
    pattern = r"(?:set reminder|remind me to|reminder for)\s+(.+?)\s+at\s+(.+)"
    match = re.search(pattern, command, re.IGNORECASE)
    
    if match:
        reminder_text = match.group(1).strip()
        reminder_time = match.group(2).strip()
        
        # Save to database
        saved = Reminder.create(user_id, reminder_text, reminder_time)
        if saved:
            return {
                "type": "text",
                "data": f"Reminder set: '{reminder_text}' at {reminder_time}."
            }
        else:
            return {
                "type": "text",
                "data": "Sorry, I couldn't save the reminder."
            }
            
    return {
        "type": "text",
        "data": "To set a reminder, please use the format: 'set reminder [action] at [time]' (e.g., 'set reminder buy groceries at 6 PM')."
    }
