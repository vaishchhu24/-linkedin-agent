import importlib.util
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
RESEND_API_KEY = config.RESEND_API_KEY
import requests

def send_prompt_email():
    data = {
        "from": "Empowrd Agent <vaishnavis@valixio.site>",
        "to": ["vaishchhu24@gmail.com"],
        "subject": "What's on your mind for your LinkedIn post today?",
        "html": """
            <p>What's on your mind for your LinkedIn post today?</p>
            <p>Just fill the form: https://tally.so/r/3j8rZx </p>
            <p>– Your Content Agent</p>
        """
    }

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )

    print("Email status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    send_prompt_email()
