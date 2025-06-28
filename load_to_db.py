import sqlite3
from datetime import date
import pandas as pd
from scrapers import scraper_amex, scraper_chase, scraper_citi

# ─── Scrape Data ─────────────────────────────
amex_db = scraper_amex.main()
chase_db = scraper_chase.main()
citi_db = scraper_citi.main()

# ─── Tag Each Row with Company ───────────────
for row in amex_db:
    row["company"] = "AMEX"
for row in chase_db:
    row["company"] = "CHASE"
for row in citi_db:
    row["company"] = "CITI"

# ─── Connect to SQLite ───────────────────────
conn = sqlite3.connect("cards.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etl_date TEXT,
    company TEXT,
    name TEXT,
    bonus TEXT,
    rewards TEXT,
    annual_fee TEXT,
    apr TEXT
)
""")

# ─── Insert All Records ──────────────────────
today = date.today().isoformat()

def insert_cards(card_list):
    cursor.executemany("""
        INSERT INTO cards (etl_date, company, name, bonus, rewards, annual_fee, apr)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (today,
         row.get("company", ""),
         row.get("name", ""),
         row.get("bonus", ""),
         row.get("reward", ""),
         row.get("fee", ""),
         row.get("apr", ""))
        for row in card_list
    ])

insert_cards(amex_db)
insert_cards(chase_db)
insert_cards(citi_db)

# ─── Finalize and View ───────────────────────
conn.commit()
df = pd.read_sql_query("SELECT * FROM cards", conn)
conn.close()

# Print preview
print(df.head())