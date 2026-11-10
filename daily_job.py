import os
import urllib.parse
import pandas as pd
import requests  # <-- This was missing! It allows Python to talk to Telegram
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# 1. Setup Environment & Client
load_dotenv()
client = genai.Client()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PRO_CHAT_ID = os.getenv("PRO_CHAT_ID")

# 2. Load the Clean Data
try:
    df = pd.read_csv('birthdays_clean.csv')
except FileNotFoundError:
    print("Error: birthdays_clean.csv not found.")
    exit()

# 3. Time Engine: Calculate Tomorrow's Date
tomorrow = datetime.now() + timedelta(days=1)
target_date = tomorrow.strftime("%d-%m") 

print(f"--- Running Daily Birthday Scan for: {tomorrow.strftime('%B %d')} ---")

# 4. Filter for tomorrow's birthdays
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
    
    response = client.chats.create(model="gemini-3.8-flash").send_message(prompt)
    message_text = response.text.strip()
    
    # 6. Build the Zero-Cost Bridge (wa.me link)
    encoded_message = urllib.parse.quote(message_text)
    whatsapp_link = f"https://wa.me/{url_phone}?text={encoded_message}"
    
    # 7. Output to the PRO via Telegram
    print(f"🎂 Celebrant: {name} ({nickname})")
    print(f"📱 Phone: {phone}")
    print(f"🔗 CLICK TO SEND: {whatsapp_link}")
    
    # THIS is the magic code that was missing to actually ping your phone:
    telegram_message = f"🎂 *Birthday Alert!*\n\n{name} ({nickname}) has a birthday tomorrow!\n\nTap here to send the picture request:\n{whatsapp_link}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
  telegram_message = f"🎂 *Birthday Alert!*\n\n{name} ({nickname}) has a birthday tomorrow!\n\nTap here to send the picture request:\n{whatsapp_link}"
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Split the comma-separated IDs from your environment variable
    chat_ids = PRO_CHAT_ID.split(',')
    
    for chat_id in chat_ids:
        try:
            response = requests.post(telegram_url, data={'chat_id': chat_id.strip(), 'text': telegram_message, 'parse_mode': 'Markdown'})
            response.raise_for_status()
            print(f"✅ Telegram notification sent to ID {chat_id.strip()} for {name}'s birthday.")
        except Exception as e:
            print(f"❌ Failed to send Telegram message to ID {chat_id.strip()}: {e}")
            
    print("-" * 50)