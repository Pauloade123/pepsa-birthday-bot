import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# 1. Load Environment Variables (Your API Key Vault)
load_dotenv()

# The SDK automatically finds GEMINI_API_KEY in your .env file
client = genai.Client()

# 2. Load the Cleaned Knowledge Base
try:
    df = pd.read_csv('birthdays_clean.csv')
    # Convert the dataframe to a clean markdown string for the LLM
    birthday_data_str = df.to_markdown(index=False)
except FileNotFoundError:
    print("Error: birthdays_clean.csv not found in this folder.")
    exit()

# 3. Give the Agent Time Awareness
today_date = datetime.now().strftime("%B %d") # e.g., November 07
current_month = datetime.now().strftime("%m") # e.g., 11

# 4. Build the System Instructions (The Brain)
system_prompt = f"""
You are the official Birthday Assistant Agent for the PRO of the Physics and Engineering Physics Association (PEPSA).
Your job is to help the PRO track student birthdays using the provided database.

CURRENT CONTEXT:
- Today's date is: {today_date}
- The current month is: {current_month}

DATABASE:
{birthday_data_str}

RULES:
- When asked who is having a birthday today or this month, check the 'date_of_birth' column.
- When asked for details, format your response EXACTLY like this example: 
  "[Name] is having birthday on [date], whatsapp no: [whatsapp_no], nickname: [nickname]"
- Do not use markdown bolding or bullet points for the final details output, just plain text as requested.
- If no one has a birthday, politely inform the PRO.
"""

# 5. Initialize the Chat Session
# We use temperature=0.0 so the agent doesn't hallucinate dates or numbers
chat = client.chats.create(
    model="gemini-3.8-flash",
    config=genai.types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.0 
    )
)

print("=====================================================")
print(f"PEPSA Birthday Agent Initialized. (Today is {today_date})")
print("Type 'exit' to end the session.")
print("=====================================================\n")

# 6. The Chat Loop
while True:
    user_input = input("PRO: ")
    
    if user_input.lower() in ['exit', 'quit']:
        print("Agent: Shutting down. Have a great day!")
        break
        
    if not user_input.strip():
        continue
        
    try:
        response = chat.send_message(user_input)
        print(f"\nAgent: {response.text}\n")
    except Exception as e:
        print(f"\n[Error communicating with Gemini: {e}]\n")