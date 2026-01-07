import os
from groq import Groq
from langsmith import traceable
from agents.coder import CoderAgent
from agents.researcher import ResearcherAgent
from agents.creative import CreativeAgent

class MainAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.coder = CoderAgent(api_key=api_key)
        self.researcher = ResearcherAgent(api_key=api_key)
        self.creative = CreativeAgent(api_key=api_key)

    @traceable(name="Main Agent")
    def route_request(self, user_query, history=None):
        q = user_query.lower()
        
        # 1. Intent Detection
        coder_keys = ["code", "website", "script", "function", "java", "python", "create"]
        research_keys = ["research", "branches", "sections", "facts", "data", "ai"]
        creative_keys = ["blog", "creative", "story", "write", "content"]

        is_coder = any(word in q for word in coder_keys)
        is_researcher = any(word in q for word in research_keys)
        is_creative = any(word in q for word in creative_keys)

        # 2. Apply Strict Filters for Tracing
        coder_hist = self._strict_filter(history, "Coder Agent", coder_keys)
        research_hist = self._strict_filter(history, "Researcher Agent", research_keys)
        creative_hist = self._strict_filter(history, "Creative Agent", creative_keys)

        # 3. Execution - Ensure results are collected as a DICTIONARY
        results = {}
        
        results["Coder Agent"] = self.coder.run(user_query, history=coder_hist) if is_coder else self.skip_coder_agent(history=coder_hist)
        results["Researcher Agent"] = self.researcher.run(user_query, history=research_hist) if is_researcher else self.skip_researcher_agent(history=research_hist)
        results["Creative Agent"] = self.creative.run(user_query, history=creative_hist) if is_creative else self.skip_creative_agent(history=creative_hist)

        return results

    def _strict_filter(self, history, agent_name, keywords):
        if not history: return []
        filtered = []
        for msg in history:
            # Only keep the history if it belongs to THIS specific sub-agent
            if msg.get("agent_name") == agent_name:
                filtered.append(msg)
            elif msg["role"] == "user":
                if any(key in msg["content"].lower() for key in keywords):
                    filtered.append(msg)
        return filtered

    @traceable(name="Coder Agent")
    def skip_coder_agent(self, history=None): return "Skipped."

    @traceable(name="Researcher Agent")
    def skip_researcher_agent(self, history=None): return "Skipped."

    @traceable(name="Creative Agent")
    def skip_creative_agent(self, history=None): return "Skipped."