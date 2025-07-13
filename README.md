# 💳 Card Matcher: AI-Powered Credit Card Recommender

An end-to-end project that scrapes real credit card data, stores it in a local database, and uses OpenAI’s GPT to recommend cards based on user input. Built with:

- 🔧 FastAPI for the backend API
- 💬 Streamlit for a chatbot-style interface
- 🗃 SQLite for data storage
- 🧠 OpenAI for recommendation logic
- ☁️ Deployed on Render (API) + Streamlit Cloud (frontend)

---

## 🌟 Features

- User enters their credit card preferences (e.g. *"I want a student card with no annual fee"*)
- Streamlit frontend sends input to FastAPI backend
- Backend:
  - Loads all cards from a local SQLite database
  - Sends them along with the user’s needs to OpenAI GPT
  - Returns top 3 card matches with concise reasoning
- Frontend displays the results like a chatbot

---

## 🚀 Live Demo

🔗 **Frontend (Streamlit)**: [https://credit-card-rec-engine.streamlit.app/](#)

---

## 📁 Project Structure

├── api.py # FastAPI backend
├── streamlit.py # Streamlit chatbot frontend
├── llm_card_matcher.py # Core logic: fetch cards + OpenAI prompt
├── load_to_db.py # Load scraped data into cards.db
├── cards.db # SQLite database of credit cards
├── scrapers/ # Scraping logic for Amex, Chase, Citi
│ ├── scraper_amex.py
│ ├── scraper_chase.py
│ └── scraper_citi.py
├── requirements.txt # Python dependencies
├── runtime.txt # Python version for Render
├── .python-version # Local Python version (used by pyenv)
├── .gitignore # Ignores .env, .db, venv, etc.


---

## 📦 Tech Stack

| Layer        | Tech                |
|--------------|---------------------|
| 🧠 AI         | OpenAI GPT-3.5      |
| 🔙 Backend    | FastAPI, Uvicorn    |
| 💬 Frontend   | Streamlit           |
| 🗃 Database   | SQLite              |
| 🌐 Web Scraping | `requests`, `BeautifulSoup`, `Selenium` |
| ☁️ Deployment | Render, Streamlit Cloud |
| 🔐 Secrets    | `.env` + `python-dotenv` |

---

## 🧪 Example Prompt

> "I’m looking for a card that earns airline miles with no foreign transaction fee"

Output (from OpenAI via backend):
- Card 1: [name] – Best for frequent flyers with no international fees
- Card 2: [name] – Solid travel rewards and signup bonus
- Card 3: [name] – No annual fee, good for beginners

---

## 🛠 How to Run Locally

### 1. Clone and Set Up

```bash
git clone https://github.com/lamtran21/Credit-Card-Rec-Engine.git
cd card-matcher
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

Create a `.env` file in the root folder:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Run the backend (FastAPI)

```bash
uvicorn api:app --reload
```

### 4. Run the frontend (Streamlit)

```bash
streamlit run streamlit.py
```

---

## 📊 Scrapers

To update the card database:

1. Run each scraper inside the `scrapers/` folder (e.g. `scraper_chase.py`)  
2. Then run `load_to_db.py` to populate `cards.db` with fresh data

---

## 🔐 Environment Variables

- `.env` is used for storing your OpenAI key.
- Make sure it is **not committed to GitHub** (included in `.gitignore`).

---

## 📌 Deployment

- **Backend** is deployed to Render (`api.py`, `cards.db`, and related files)
- **Frontend** is deployed to Streamlit Cloud (`streamlit.py`)
- Deployment uses:
  - `requirements.txt` for dependencies
  - `runtime.txt` to specify Python version (e.g., `python-3.11`)

---

## ✍️ Author

**Lam Tran**  
🎓 Data Science | Python  
🔗 [LinkedIn](linkedin.com/in/lam-tran21/)

---

## 📄 License

MIT License – Free to use, modify, and distribute.
