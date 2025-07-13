from fastapi import FastAPI
from pydantic import BaseModel
from llm_card_matcher import get_top_cards
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Streamlit frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    user_input: str

@app.post("/match_cards")
def get_card_match(req: MatchRequest):
    result = get_top_cards(req.user_input)
    return {"response": result}
