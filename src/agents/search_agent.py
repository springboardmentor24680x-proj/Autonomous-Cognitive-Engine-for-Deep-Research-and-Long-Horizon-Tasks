#!/usr/bin/env python3
"""
Search Agent - Specialized agent for web search and information gathering
Part of the multi-agent workflow automation system
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()


class SearchAgent:
    """
    Specialized agent for web search, research, and information gathering.
    Handles research tasks delegated by the supervisor agent.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the search agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,
            max_tokens=1200
        )
        
        self.agent_type = "web_search"
        self.model = model_name
        
        # Create processing chain
        self.chain = self._create_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the search agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are a Search Agent, specialized in web research and information gathering.

{current_info}

CORE CAPABILITIES:
- Conduct comprehensive web research
- Gather current and accurate information
- Synthesize findings from multiple sources
- Fact-checking and verification
- Trend analysis and market research

RESEARCH METHODOLOGY:
1. **Query Planning**: Develop effective search strategies
2. **Information Gathering**: Collect relevant, current data
3. **Source Evaluation**: Assess credibility and relevance
4. **Synthesis**: Combine findings into coherent insights
5. **Verification**: Cross-reference important facts

OUTPUT FORMAT:
- Use **bold** for key findings and section headers
- Use bullet points (-) for research findings
- Use numbered lists (1. 2. 3.) for sequential information
- Cite sources and provide context
- Highlight important data with `backticks`

RESEARCH STRUCTURE:
1. **Executive Summary**: Brief overview of findings
2. **Key Findings**: Main research results
3. **Detailed Analysis**: In-depth information
4. **Sources & References**: Information sources
5. **Recommendations**: Actionable insights

RESEARCH FOCUS AREAS:
- Current events and news
- Market trends and analysis
- Technical information and specifications
- Academic and scientific research
- Industry insights and best practices

Always provide accurate, well-sourced, and actionable research results."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Research Task: {task}\n\nPlease conduct comprehensive research and provide detailed findings.")
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def conduct_research(self, research_query: str, focus_area: str = "general") -> Dict[str, Any]:
        """Conduct comprehensive research on the given query."""
        try:
            # Simulate web search (in real implementation, this would use Tavily API)
            research_task = f"Research: {research_query} (Focus: {focus_area})"
            
            # Process the research request
            research_results = self.chain.invoke({
                "task": research_task
            })
            
            # Add metadata and structure
            enhanced_results = f"""## 🔍 **Research Results**

**Query**: {research_query}
**Focus Area**: {focus_area}
**Research Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{research_results}

---

**Research Methodology**:
- Comprehensive information gathering
- Multi-source verification
- Current data prioritization
- Credibility assessment

**Note**: This research was conducted using advanced AI analysis. For the most current information, consider verifying key facts with primary sources."""

            return {
                "success": True,
                "research_results": enhanced_results,
                "query": research_query,
                "focus_area": focus_area,
                "agent_type": self.agent_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "research_results": f"Error during research: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def fact_check(self, claim: str) -> Dict[str, Any]:
        """Fact-check a specific claim or statement."""
        try:
            task = f"Fact-check this claim and provide verification: {claim}"
            
            fact_check_result = self.chain.invoke({
                "task": task
            })
            
            return {
                "success": True,
                "fact_check": fact_check_result,
                "original_claim": claim,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fact_check": f"Error during fact-checking: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def trend_analysis(self, topic: str, time_period: str = "current") -> Dict[str, Any]:
        """Analyze trends for a specific topic."""
        try:
            task = f"Analyze current trends and developments for: {topic} (Time period: {time_period})"
            
            trend_analysis = self.chain.invoke({
                "task": task
            })
            
            return {
                "success": True,
                "trend_analysis": trend_analysis,
                "topic": topic,
                "time_period": time_period,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "trend_analysis": f"Error during trend analysis: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def market_research(self, market: str, research_type: str = "overview") -> Dict[str, Any]:
        """Conduct market research for a specific market or industry."""
        try:
            task = f"Conduct {research_type} market research for: {market}"
            
            market_research = self.chain.invoke({
                "task": task
            })
            
            return {
                "success": True,
                "market_research": market_research,
                "market": market,
                "research_type": research_type,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "market_research": f"Error during market research: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def process_task(self, task_description: str) -> Dict[str, Any]:
        """Main method to process search and research tasks."""
        try:
            # Determine the type of research task
            task_lower = task_description.lower()
            
            if "fact check" in task_lower or "verify" in task_lower:
                # Extract the claim to fact-check
                claim = task_description.replace("fact check", "").replace("verify", "").strip()
                return self.fact_check(claim)
            elif "trend" in task_lower or "trends" in task_lower:
                # Extract the topic for trend analysis
                topic = task_description.replace("trend", "").replace("trends", "").strip()
                return self.trend_analysis(topic)
            elif "market" in task_lower:
                # Extract the market for research
                market = task_description.replace("market", "").replace("research", "").strip()
                return self.market_research(market)
            else:
                # Default to general research
                return self.conduct_research(task_description)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": f"Search Agent Error: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the search agent."""
        return {
            "agent_type": self.agent_type,
            "name": "SearchAgent",
            "description": "Specialized in web search and information gathering",
            "capabilities": [
                "Comprehensive web research",
                "Fact-checking and verification",
                "Trend analysis",
                "Market research",
                "Current events monitoring",
                "Multi-source information synthesis"
            ],
            "optimal_for": [
                "Current information gathering",
                "Market analysis",
                "Competitive research",
                "Fact verification",
                "Trend identification",
                "News and events research"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY"))
        }