import streamlit as st
from core.llm import chat

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(page_title="Personalized Learning Assistant for Learning Hard Topics",layout="centered")
st.title("Personalized Learning Assistant")
st.markdown(
    """
Enter a hard topic, paste a reference link, or upload your notes.

The AI will help you with:

- Simple explanation of difficult concepts  
- Personalized study planner  
- Subtopic breakdown  
- Practice tasks  
- Revision schedule  

Powered by local AI (Ollama – Qwen3 4B).
"""
)


Topic = st.text_area(
    "Enter the hard topic you want to understand:",
    height=200
)

if st.button("Create Simple Notes"):

    if not Topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating explanation... ⏳"):
            try:
                result = chat(Topic)
                st.subheader("AI Explanation")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")