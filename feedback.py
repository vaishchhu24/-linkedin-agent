import json

def get_feedback_context(client_id="vaishnavi"):
    with open("feedback_memory.json") as f:
        memory = json.load(f)

    feedback_chunks = [
        f"- {entry['feedback']}"
        for entry in memory
        if entry['client_id'] == client_id
    ]

    return "\n".join(feedback_chunks)
