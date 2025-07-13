import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_cards_from_db(db_path="cards.db"):
    """Fetch credit cards from SQLite database, filter out blank names."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, bonus, rewards, annual_fee, apr FROM cards")
    rows = cursor.fetchall()
    conn.close()

    cards = []
    for name, bonus, rewards, fee, apr in rows:
        if not name or not name.strip():
            continue
        cards.append({
            "name": name.strip(),
            "bonus": bonus,
            "reward": rewards,
            "fee": fee,
            "apr": apr,
        })
    return cards

def build_prompt(user_input, cards):
    """Builds a prompt to feed to the OpenAI LLM."""
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
    """Main entry point: fetch cards, build prompt, call OpenAI, return result."""
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
