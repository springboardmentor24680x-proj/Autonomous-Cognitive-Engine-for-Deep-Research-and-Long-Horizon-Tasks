# multi_agent_research.py
# Multi-Agent Research Pipeline using GROQ (Llama 3.1) + LangGraph + LangSmith

import os
from typing import TypedDict, List, Annotated
import operator

# ------------------ LANGSMITH TRACING ------------------
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "GroqMultiAgentResearch"  # Change name if you want
# Make sure GROQ_API_KEY and LANGCHAIN_API_KEY are set in your terminal/environment

# ------------------ IMPORTS ------------------
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ------------------ LLM SETUP - GROQ ------------------
llm = ChatGroq(
    model="llama-3.1-70b-versatile",     # Fast & smart - best choice
    # model="llama3-70b-8192",           # Alternative
    # model="mixtral-8x7b-32768",        # Also good
    temperature=0.2,
    max_tokens=4096
)

# ------------------ TOOLS & WEB SEARCH AGENT ------------------
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

def create_web_search_agent():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a precise web research assistant. Use the search tool to get current, accurate information. Return clean factual content only - no fluff."),
        ("placeholder", "{messages}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

web_search_agent = create_web_search_agent()

# ------------------ SUB-AGENTS ------------------
# Summarizer
summarizer_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the content into concise, clear bullet points. Keep all important facts and details."),
    ("human", "{input}"),
])
summarizer_agent = summarizer_prompt | llm

# Analyzer
analyzer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Perform a deep analysis of the content:
    - Overview
    - Key findings
    - Strengths and weaknesses
    - Implications
    - Recommendations
    Use critical thinking.
    """),
    ("human", "{input}"),
])
analyzer_agent = analyzer_prompt | llm

# Report Generator
report_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Write a professional, well-structured markdown report including:
    - Title
    - Executive Summary
    - Key Findings
    - Detailed Analysis
    - Conclusion
    - Sources (if any)
    Use proper headings (##, ###) and formatting.
    """),
    ("human", "{input}"),
])
report_generator_agent = report_prompt | llm

# ------------------ LANGGRAPH STATE & SUPERVISOR ------------------
class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], operator.add]
    next: str

# Supervisor - decides which agent to route to next
supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are the supervisor agent in charge of orchestrating research.
    
    Available agents:
    - web_search
    - summarizer
    - analyzer
    - report_generator
    - end
    
    Based on the current state and user query, choose ONLY ONE next agent.
    Respond with exactly one of these words in lowercase: web_search, summarizer, analyzer, report_generator, or end
    
    Typical flow:
    1. web_search → get latest info
    2. summarizer → condense it
    3. analyzer → deep insights
    4. report_generator → final output
    5. end → finish
    """),
    ("placeholder", "{messages}"),
])

supervisor_chain = supervisor_prompt | llm | (lambda x: x.content.strip().lower())

def supervisor_node(state: AgentState):
    result = supervisor_chain.invoke(state["messages"])
    return {"next": result}

def delegate_node(state: AgentState):
    next_agent = state["next"]
    last_message = state["messages"][-1].content

    if next_agent == "web_search":
        result = web_search_agent.invoke({"input": last_message})
        output = result["output"]
    elif next_agent == "summarizer":
        output = summarizer_agent.invoke({"input": last_message}).content
    elif next_agent == "analyzer":
        output = analyzer_agent.invoke({"input": last_message}).content
    elif next_agent == "report_generator":
        output = report_generator_agent.invoke({"input": last_message}).content
    else:
        output = "Research task completed successfully."

    return {"messages": [AIMessage(content=output)]}

# ------------------ BUILD GRAPH ------------------
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("delegate", delegate_node)

graph.set_entry_point("supervisor")

graph.add_edge("delegate", "supervisor")

graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "web_search": "delegate",
        "summarizer": "delegate",
        "analyzer": "delegate",
        "report_generator": "delegate",
        "end": END,
    }
)

app = graph.compile()

# ------------------ RUN ------------------
if __name__ == "__main__":
    print(" Groq-Powered Multi-Agent Research System Ready!\n")
    
    query = input("Enter your research topic: ").strip()
    if not query:
        query = "Latest breakthroughs in AI agents and multi-agent systems as of January 2026"
    
    print(f"\nStarting research: {query}\n{'='*70}")
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next": ""
    }
    
    # Stream the steps (great for seeing progress)
    for step in app.stream(initial_state):
        if "__end__" not in step:
            node_name = list(step.keys())[0]
            print(f"→ Step: {node_name.upper()}")
            if "messages" in step.get(node_name, {}):
                print(step[node_name]["messages"][-1].content[:500] + "..." if len(step[node_name]["messages"][-1].content) > 500 else step[node_name]["messages"][-1].content)
            print("-" * 50)
    
    # Get final result
    final_state = app.get_state(initial_state).values
    final_messages = final_state["messages"]
    
    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)
    print(final_messages[-1].content)
    def run_research(query: str) -> str:
   
        print(f"Starting multi-agent research on: {query}\n")
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "next": ""
        }
        
        final_messages = []
        for step in app.stream(initial_state):
            if "__end__" not in step:
                node = list(step.keys())[0]
                msg = step[node].get("messages", [None])[-1]
                if msg:
                    final_messages.append(msg)
                    print(f"[{node.upper()}] {msg.content[:200]}...\n")
        
        if final_messages:
            return final_messages[-1].content
        return "No result generated."