from llm_card_matcher import get_top_cards

user_input = input("What kind of credit card are you looking for? ")
recommendations = get_top_cards(user_input)
print("\nTop 3 recommended cards:\n")
print(recommendations)