import requests
import json
from config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

# Fetch all records from Airtable
records = []
offset = None
while True:
    params = {"offset": offset} if offset else {}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    records.extend(data["records"])
    offset = data.get("offset")
    if not offset:
        break

# Convert to OpenAI fine-tuning JSONL format
jsonl_data = []
for record in records:
    fields = record.get("fields", {})
    if fields.get("voice quality", 0) >= 4 and fields.get("post quality", 0) >= 4:
        jsonl_data.append({
            "messages": [
                {"role": "system", "content": "You are a LinkedIn content writer for HR coaches."},
                {"role": "user", "content": f"Write a LinkedIn post about {fields.get('topic', 'a business topic')}."},
                {"role": "assistant", "content": fields.get("post", "")}
            ]
        })

# Save to daily_feedback.jsonl
with open("daily_feedback.jsonl", "w") as f:
    for item in jsonl_data:
        f.write(json.dumps(item) + "\n")

print("✅ Generated daily_feedback.jsonl from Airtable")
