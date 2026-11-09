import os
import urllib.parse
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# 1. Setup Environment & Client
load_dotenv()
client = genai.Client()

# 2. Load the Clean Data
try:
    df = pd.read_csv('birthdays_clean.csv')
except FileNotFoundError:
    print("Error: birthdays_clean.csv not found.")
    exit()

# 3. Time Engine: Calculate Tomorrow's Date
# We use %d-%m because that is the format we applied during data cleaning
tomorrow = datetime.now() + timedelta(days=1)
target_date = tomorrow.strftime("%d-%m") 

print(f"--- Running Daily Birthday Scan for: {tomorrow.strftime('%B %d')} ---")

# 4. Filter for tomorrow's birthdays
# Convert the column to string just in case pandas read it as something else
df['date_of_birth'] = df['date_of_birth'].astype(str)
celebrants = df[df['date_of_birth'] == target_date]

if celebrants.empty:
    print("No birthdays tomorrow. Agent sleeping.")
    exit()

print(f"Found {len(celebrants)} celebrant(s)! Generating messages...\n")

# 5. Agent Generation Loop
for index, row in celebrants.iterrows():
    name = row['Name']
    nickname = row['nickname']
    phone = str(row['whatsapp_no']).strip()
    
    # Clean the phone number for the URL (remove any '+' symbols, WhatsApp URLs just want the raw digits)
    url_phone = phone.replace('+', '')
    
    # The Prompt Engine
    prompt = f"""
    You are writing a WhatsApp message on behalf of the PRO of the Physics and Engineering Physics Association (PEPSA).
    Write a friendly, brief message to a student named {name} (who goes by {nickname}). 
    Their birthday is TOMORROW! 
    
    The goal of this message is to warmly inform them that we are preparing their birthday design and ask them to send a clear, nice picture of themselves.
    
    Rules:
    - Keep it short, conversational, and energetic.
    - Include a couple of relevant emojis.
    - Do NOT include any placeholders like [Your Name]. Sign off as "PEPSA PRO".
    """
    
    # Generate the message with Gemini
    response = client.chats.create(model="gemini-3.8-flash").send_message(prompt)
    message_text = response.text.strip()
    
    # 6. Build the Zero-Cost Bridge (wa.me link)
    # URL encoding converts spaces to %20, newlines to %0A, etc., so it works in a browser link
    encoded_message = urllib.parse.quote(message_text)
    whatsapp_link = f"https://wa.me/{url_phone}?text={encoded_message}"
    
    # 7. Output for the PRO
    print(f"🎂 Celebrant: {name} ({nickname})")
    print(f"📱 Phone: {phone}")
    print(f"🤖 Agent Draft:\n{message_text}")
    print(f"🔗 CLICK TO SEND: {whatsapp_link}")
    print("-" * 50)