import pandas as pd
import json

# Load your exported CSV or XLSX from Airtable/Sheets
df = pd.read_csv("feedback_log.csv")  # or use pd.read_excel("feedback_log.xlsx")

# Filter high-quality responses
filtered = df[(df["Voice Score"] >= 4) & (df["Quality Score"] >= 4)]

# Convert to OpenAI JSONL format
jsonl_data = []
for _, row in filtered.iterrows():
    jsonl_data.append({
        "messages": [
            {"role": "system", "content": "You are a LinkedIn content writer for HR coaches."},
            {"role": "user", "content": f"Write a LinkedIn post about {row['Topic']}."},
            {"role": "assistant", "content": row["Output"]}
        ]
    })

# Save to JSONL file
with open("daily_feedback.jsonl", "w") as f:
    for item in jsonl_data:
        f.write(json.dumps(item) + "\n")

print("✅ JSONL file created: daily_feedback.jsonl")
