from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def chat(topic, difficulty, days, hours):

    study_planner_prompt = ChatPromptTemplate.from_template(
"""
You are an expert study planner and academic mentor.

Topic:
{topic}

Difficulty Level:
{difficulty}

Total Days Available:
{days}

Daily Study Hours:
{hours}

Your task:

1. Break the topic into logical subtopics (basic to advanced).
2. Distribute subtopics across the available days.
3. Allocate realistic study time per day.
4. Include:
   - Learning time
   - Practice time
   - Short revision blocks
5. Add one final revision day.
6. Keep the plan practical and not overloaded.

Return JSON only in this format:

{{
  "Subtopics": ["...", "...", "..."],

  "Study_Plan": {{
    "Day 1": {{
        "Focus": "...",
        "Study_Time": "...",
        "Practice": "...",
        "Revision": "..."
    }},
    "Day 2": {{
        "Focus": "...",
        "Study_Time": "...",
        "Practice": "...",
        "Revision": "..."
    }}
  }},

  "Final_Revision_Day": "...",

  "Motivation_Tip": "..."
}}

Rules:
- Keep explanation concise.
- Make time allocation realistic.
- Avoid unnecessary text.
- Return valid JSON only.
"""
    )

    LLM = ChatOllama(
        model="qwen3:4b",
        temperature=0.2
    )

    parser = StrOutputParser()

    chain = study_planner_prompt | LLM | parser

    response = chain.invoke({
        "topic": topic,
        "difficulty": difficulty,
        "days": days,
        "hours": hours
    })

    return response