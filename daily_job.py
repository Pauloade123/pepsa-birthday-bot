import os
import urllib.parse
import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai

# 1. Setup Environment
load_dotenv()
client = genai.Client()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PRO_CHAT_ID = os.getenv("PRO_CHAT_ID")
chat_ids = PRO_CHAT_ID.split(',')

# 2. Load the Clean Data
try:
    df = pd.read_csv('birthdays_clean.csv')
    df['date_of_birth'] = df['date_of_birth'].astype(str)
except FileNotFoundError:
    print("Error: birthdays_clean.csv not found.")
    exit()

# 3. Time Engine: Calculate Both Target Dates
today = datetime.now()
tomorrow = today + timedelta(days=1)

target_today = today.strftime("%d-%m")
target_tomorrow = tomorrow.strftime("%d-%m")

print(f"--- Running Scan: Checking for TOMORROW ({target_tomorrow}) and TODAY ({target_today}) ---")

celebrants_tomorrow = df[df['date_of_birth'] == target_tomorrow]
celebrants_today = df[df['date_of_birth'] == target_today]

# 4. Agent Generation Logic (Helper Function)
def process_celebrants(celebrants, day_type):
    if celebrants.empty:
        print(f"No birthdays {day_type.lower()}.")
        return
        
    print(f"\nFound {len(celebrants)} celebrant(s) for {day_type.upper()}! Generating messages...")
    
    for index, row in celebrants.iterrows():
        name = row['Name']
        nickname = row['nickname']
        phone = str(row['whatsapp_no']).strip()
        url_phone = phone.replace('+', '')
        
        # Dynamically switch the prompt and Telegram alert text
        if day_type == "Tomorrow":
            alert_title = "🎂 *Advance Birthday Alert (Tomorrow)!*"
            action_text = "Tap here to send the picture request:"
            prompt = f"""
            You are writing a WhatsApp message on behalf of the PRO of the Physics and Engineering Physics Association (PEPSA).
            Write a friendly, brief message to a student named {name} (who goes by {nickname}). Their birthday is TOMORROW! 
            The goal is to warmly inform them that we are preparing their birthday design and ask them to send a clear, nice picture of themselves.
            Rules: Keep it short, conversational, and energetic. Include relevant emojis. Do NOT include placeholders. Sign off as "PEPSA PRO".
            """
        else:
            alert_title = "🎉 *IT'S TODAY! Official Birthday Alert!*"
            action_text = "Tap here to send the official birthday wish:"
            prompt = f"""
            You are writing a WhatsApp message on behalf of the PRO of the Physics and Engineering Physics Association (PEPSA).
            Write a warm, celebratory Happy Birthday message to a student named {name} (who goes by {nickname}). Their birthday is TODAY! 
            The goal is to wish them a fantastic birthday on behalf of the association now that their design is ready. 
            Rules: Keep it celebratory, warm, and energetic. Include cake/party emojis. Do NOT include placeholders. Sign off as "PEPSA PRO".
            """
            
        # Generate the message
        response = client.chats.create(model="gemini-1.5-flash").send_message(prompt)
        message_text = response.text.strip()
        
        # Build the URL
        encoded_message = urllib.parse.quote(message_text)
        whatsapp_link = f"https://wa.me/{url_phone}?text={encoded_message}"
        
        # Dispatch to Telegram
        telegram_message = f"{alert_title}\n\n{name} ({nickname})\n\n{action_text}\n{whatsapp_link}"
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        for chat_id in chat_ids:
            try:
                res = requests.post(telegram_url, data={'chat_id': chat_id.strip(), 'text': telegram_message, 'parse_mode': 'Markdown'})
                res.raise_for_status()
                print(f"✅ Telegram notification sent to ID {chat_id.strip()} for {name}.")
            except Exception as e:
                print(f"❌ Failed to send to ID {chat_id.strip()}: {e}")
                
        print("-" * 50)

# 5. Execute Pipeline
process_celebrants(celebrants_tomorrow, "Tomorrow")
process_celebrants(celebrants_today, "Today")