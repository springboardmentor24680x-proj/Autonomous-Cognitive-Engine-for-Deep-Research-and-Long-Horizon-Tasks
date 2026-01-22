# agent.py

from langchain_groq import ChatGroq


class BaseAgent:
    """
    Abstract base class for all agents.
    Defines a common interface and shared LLM setup.
    """

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
        )

    def run(self, prompt: str) -> str:
        """
        Run the agent on a given prompt.
        Must be overridden by subclasses if needed.
        """

        full_prompt = (
            f"{self.system_prompt}\n\n"
            f"Task:\n{prompt}"
        )

        response = self.llm.invoke(full_prompt)
        return response.content
