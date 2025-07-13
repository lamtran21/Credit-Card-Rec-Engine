import streamlit as st
import requests

st.set_page_config(page_title="Card Matcher", page_icon="💳")
st.title("💳 Credit Card Chatbot")

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("What kind of credit card are you looking for?"):
    # Add user's message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to FastAPI
    try:
        response = requests.post(
            "http://localhost:8000/match_cards",
            json={"user_input": prompt},
            timeout=30
        )
        response.raise_for_status()
        reply = response.json()["response"]
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    # Add assistant's response to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
