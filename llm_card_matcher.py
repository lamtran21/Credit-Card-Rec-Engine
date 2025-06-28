import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_cards_from_db():
    conn = sqlite3.connect("cards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, bonus, rewards, annual_fee, apr FROM cards")
    rows = cursor.fetchall()
    conn.close()

    cards = []
    for row in rows:
        name = row[0]
        if not name or name.strip() == "":
            continue  # skip blank rows

        cards.append({
            "name": name.strip(),
            "bonus": row[1],
            "reward": row[2],
            "fee": row[3],
            "apr": row[4]
        })

    return cards

def build_prompt(user_input, cards):
    card_descriptions = "\n\n".join([
        f"Name: {c['name']}\nBonus: {c['bonus']}\nRewards: {c['reward']}\nAnnual Fee: {c['fee']}\nAPR: {c['apr']}"
        for c in cards
    ])
    return f"""
A user is looking for a credit card. Here’s what they said:

\"{user_input}\"

Below is a list of credit cards. Recommend the top 3 that best match their needs and explain why. Be concise and helpful.

{card_descriptions}
"""

def get_top_cards(user_input):
    cards = fetch_cards_from_db()
    prompt = build_prompt(user_input, cards)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful credit card assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
