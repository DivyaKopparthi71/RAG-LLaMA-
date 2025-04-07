import streamlit as st
import requests

st.set_page_config(page_title="BCPA Chatbot", layout="centered")
st.title("🤖 BCPA Chatbot")
st.markdown("Ask any question from the Candidate Handbook (Feb 2025)")

# Replace with your actual FastAPI backend URL (use ngrok if testing locally)
API_URL = "http://localhost:8000/query"

user_question = st.text_input("Enter your question:")

if st.button("Ask"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"question": user_question})
                if response.status_code == 200:
                    st.success("Answer:")
                    st.write(response.json().get("answer", "No answer returned."))
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")
