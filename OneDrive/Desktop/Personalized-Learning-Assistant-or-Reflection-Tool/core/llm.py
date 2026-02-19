from langchain_core.prompts import ChatPromptTemplate #creating a chat bot
from langchain_core.output_parsers import StrOutputParser #eliminating white spaces in output
from langchain_ollama import ChatOllama

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def chat(topic):
    prompt_template=ChatPromptTemplate.from_template(
        """
You are a patient teacher.

Topic:
{topic}

Explain the topic in simple words.

Break into:
1. Basic idea
2. Key concepts
3. Example
4. Short summary

Return JSON only:

{{
  "Basic_Idea": "...",
  "Key_Concepts": ["...", "..."],
  "Example": "...",
  "Summary": "..."
}}
""")

    LLM=ChatOllama(
        model="qwen3:4b",
        temperature=0.1
    )

    parser =StrOutputParser()
    chain=prompt_template | LLM | parser
    response=chain.invoke(
        {
            "topic":topic
        }
    )
    return response