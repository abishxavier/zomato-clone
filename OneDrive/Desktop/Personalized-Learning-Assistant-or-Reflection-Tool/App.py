import streamlit as st
from core.llm import chat
import json
import warnings

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

difficulty = st.selectbox(
    "Select Difficulty Level",
    ["Beginner", "Intermediate", "Advanced"]
)

days = st.number_input("Number of study days", min_value=1, max_value=30, value=5)

hours = st.number_input("Daily study hours", min_value=1, max_value=12, value=2)

if st.button("Create Study Plan"):

    if not Topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating study plan... ⏳"):
            try:
                result = chat(Topic, difficulty, days, hours)

                parsed = json.loads(result)

                st.subheader("AI Study Plan")
                st.json(parsed)

            except json.JSONDecodeError:
                st.error("Model did not return valid JSON. Try again.")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")
