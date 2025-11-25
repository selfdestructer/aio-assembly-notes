import json
import os

BRAIN_DIR = os.path.join(os.path.dirname(__file__), "Life_OS", "04_Brain")
MEMORY_FILE = os.path.join(BRAIN_DIR, "memory.json")
DECISIONS_FILE = os.path.join(BRAIN_DIR, "decisions.json")

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def get_context():
    """Returns the full context memory."""
    return load_json(MEMORY_FILE)

def log_decision(dilemma, choice, outcome, alternate_timeline_prediction=None):
    """Logs a major life decision and its potential alternate timeline."""
    decisions = load_json(DECISIONS_FILE)
    
    entry = {
        "id": len(decisions) + 1,
        "dilemma": dilemma,
        "choice_made": choice,
        "actual_outcome": outcome,
        "alternate_timeline": alternate_timeline_prediction, # The Ghost Ship
        "timestamp": str(os.times()) # Placeholder, better to use datetime
    }
    
    decisions.append(entry)
    save_json(DECISIONS_FILE, decisions)
    print(f"Decision logged: {dilemma[:30]}...")

def update_memory(new_event, characters=None):
    """Updates the core memory timeline and character sheet."""
    memory = load_json(MEMORY_FILE)
    
    memory["timeline_events"].append(new_event)
    
    if characters:
        for char_name, details in characters.items():
            if char_name not in memory["characters"]:
                memory["characters"][char_name] = details
            else:
                # Merge details? For now, simplistic overwrite or append
                memory["characters"][char_name] += f"; {details}"
                
    save_json(MEMORY_FILE, memory)
