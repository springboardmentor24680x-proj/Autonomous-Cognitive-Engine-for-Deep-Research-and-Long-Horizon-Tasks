from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    max_tokens=2048,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def create_sub_agent(
    name: str,
    system_prompt: str,
    can_visualize: bool = False,
    can_read_state: bool = False
):
    """
    Factory to create traceable sub-agents
    Now each sub-agent will appear as a separate node in LangSmith
    """
    
    def build_prompt(input_dict):
        """Build the full prompt with context"""
        messages = input_dict.get("messages", [])
        state = input_dict.get("state", {})
        
        # Extract user request
        user_text = messages[-1].get("content", "") if messages else ""
        
        # Build context if agent can read state
        context_parts = []
        
        if can_read_state and state:
            todos = state.get("todos", [])
            if todos:
                pending = [t for t in todos if not t.get("completed")]
                completed = [t for t in todos if t.get("completed")]
                
                high = len([t for t in pending if t.get("priority") == "high"])
                medium = len([t for t in pending if t.get("priority") == "medium"])
                low = len([t for t in pending if t.get("priority") == "low"])
                
                context_parts.append(f"""## Current Tasks
- Total: {len(todos)} tasks
- Completed: {len(completed)} ({len(completed)/len(todos)*100:.0f}%)
- Pending: {len(pending)}
  - High priority: {high}
  - Medium priority: {medium}
  - Low priority: {low}
""")
            
            calendar = state.get("calendar", [])
            if calendar:
                context_parts.append(f"## Calendar\n{len(calendar)} upcoming events")
            
            files = state.get("files", {})
            if files:
                context_parts.append(f"## Files\n{len(files)} files: {', '.join(list(files.keys())[:5])}")
        
        # Add visualization instructions for capable agents
        if can_visualize:
            context_parts.append("""
## Visualization Instructions
When data visualization would help, end your response with these EXACT trigger lines:

- `CHART: task_completion_doughnut` - Shows completed vs pending tasks
- `CHART: priority_distribution_pie` - Shows distribution of pending tasks by priority
- `CHART: priority_bar` - Bar chart of tasks by priority level

Use ONE chart trigger per response. The system will automatically render it.
Do NOT output JSON or code - just use the trigger phrase.
""")
        
        context_text = "\n".join(context_parts)
        
        # Return formatted prompt
        return {
            "context": context_text,
            "user_request": user_text,
            "state": state  
        }
    
    def process_response(llm_output):
        """Process LLM response and extract charts"""
        response_text = llm_output.content if hasattr(llm_output, 'content') else str(llm_output)
        state = llm_output.get("state", {}) if isinstance(llm_output, dict) else {}
        
        # Extract charts if this agent can visualize
        render_components = []
        if can_visualize:
            render_components = _extract_charts(response_text, state)
        
        # Clean response (remove CHART: lines)
        clean_response = _remove_chart_triggers(response_text)
        
        return {
            "messages": [{"role": "assistant", "content": clean_response}],
            "render_components": render_components
        }
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt + "\n\n{context}"),
        ("human", "{user_request}")
    ])
    
    # Build chain: input → prompt → LLM → process
    # This chain will be traced in LangSmith with the agent name
    chain = (
        RunnableLambda(build_prompt).with_config({"run_name": f"{name}_build_context"})
        | prompt.with_config({"run_name": f"{name}_prompt"})
        | llm.with_config({"run_name": f"{name}_llm_call"})
        | RunnableLambda(lambda x: {"content": x.content, "state": None}).with_config({"run_name": f"{name}_extract"})
    )
    
    def agent_function(input_dict):
        """Wrapper that calls the chain and processes result"""
        state = input_dict.get("state", {})
        
        # Invoke the chain (this will be traced)
        result = chain.invoke(input_dict)
        
        response_text = result.get("content", "")
        
        # Extract charts
        render_components = []
        if can_visualize:
            render_components = _extract_charts(response_text, state)
        
        # Clean response
        clean_response = _remove_chart_triggers(response_text)
        
        return {
            "messages": [{"role": "assistant", "content": clean_response}],
            "render_components": render_components
        }
    
    # Return as a RunnableLambda so it's traced
    return RunnableLambda(agent_function).with_config({"run_name": f"SubAgent_{name}"})


def _extract_charts(response_text: str, state: dict) -> list:
    """Extract and generate chart configs from response"""
    charts = []
    
    # Calculate task stats
    todos = state.get("todos", [])
    if not todos:
        return charts
    
    pending = [t for t in todos if not t.get("completed")]
    completed = len(todos) - len(pending)
    
    high = len([t for t in pending if t.get("priority") == "high"])
    medium = len([t for t in pending if t.get("priority") == "medium"])
    low = len([t for t in pending if t.get("priority") == "low"])
    
    # Check for chart triggers
    if "CHART: task_completion_doughnut" in response_text or "CHART: task_completion" in response_text:
        charts.append({
            "type": "doughnut",
            "data": {
                "labels": ["Completed", "Pending"],
                "datasets": [{
                    "data": [completed, len(pending)],
                    "backgroundColor": ["#22c55e", "#ef4444"],
                    "borderColor": ["#ffffff", "#ffffff"],
                    "borderWidth": 4
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"position": "bottom", "labels": {"font": {"size": 14}}},
                    "title": {
                        "display": True,
                        "text": "Task Completion Status",
                        "font": {"size": 18, "weight": "bold"}
                    }
                }
            }
        })
    
    if "CHART: priority_distribution" in response_text or "CHART: priority_pie" in response_text:
        charts.append({
            "type": "pie",
            "data": {
                "labels": ["High Priority", "Medium Priority", "Low Priority"],
                "datasets": [{
                    "data": [high, medium, low],
                    "backgroundColor": ["#ef4444", "#f59e0b", "#3b82f6"],
                    "borderColor": ["#ffffff", "#ffffff", "#ffffff"],
                    "borderWidth": 3
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"position": "right", "labels": {"font": {"size": 14}}},
                    "title": {
                        "display": True,
                        "text": "Priority Distribution (Pending Tasks)",
                        "font": {"size": 18, "weight": "bold"}
                    }
                }
            }
        })
    
    if "CHART: priority_bar" in response_text or "CHART: tasks_by_priority" in response_text:
        charts.append({
            "type": "bar",
            "data": {
                "labels": ["High", "Medium", "Low"],
                "datasets": [{
                    "label": "Pending Tasks",
                    "data": [high, medium, low],
                    "backgroundColor": ["#ef4444", "#f59e0b", "#3b82f6"],
                    "borderColor": ["#991b1b", "#9a3412", "#1e40af"],
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Pending Tasks by Priority",
                        "font": {"size": 18, "weight": "bold"}
                    },
                    "legend": {"display": False}
                },
                "scales": {
                    "y": {"beginAtZero": True, "ticks": {"stepSize": 1}}
                }
            }
        })
    
    return charts


def _remove_chart_triggers(text: str) -> str:
    """Remove CHART: trigger lines from response"""
    lines = text.split("\n")
    clean_lines = [line for line in lines if not line.strip().startswith("CHART:")]
    return "\n".join(clean_lines).strip()


# ============================================================================
# SPECIALIZED SUB-AGENTS (Now properly traced in LangSmith)
# ============================================================================

visualizer_agent = create_sub_agent(
    name="visualizer",
    system_prompt="""You are an expert data visualization specialist.
Your role is to create beautiful, insightful charts that make complex data easy to understand.

When analyzing tasks:
- Always suggest the most appropriate visualization
- Provide brief insights about the data
- Use CHART: triggers to generate actual visualizations

Be concise and focus on visual insights.""",
    can_visualize=True,
    can_read_state=True
)

analyzer_agent = create_sub_agent(
    name="analyzer",
    system_prompt="""You are a deep analytical thinker specializing in productivity analysis.

Provide:
- Clear insights from the data
- Identify patterns and trends
- Highlight potential issues
- Give actionable recommendations

Support your analysis with visualizations when helpful.""",
    can_visualize=True,
    can_read_state=True
)

report_generator_agent = create_sub_agent(
    name="report_generator",
    system_prompt="""You are a professional report writer.

Create structured reports with:
- **Executive Summary** (2-3 sentences)
- **Key Metrics** (bullet points)
- **Detailed Findings**
- **Recommendations**
- **Visual Summary** (use chart triggers)

Use markdown formatting. Be professional yet concise.""",
    can_visualize=True,
    can_read_state=True
)

planning_agent = create_sub_agent(
    name="planning",
    system_prompt="""You are a strategic planning expert.

Break down goals into:
1. Clear phases/milestones
2. Specific actionable tasks
3. Priority assignments
4. Estimated timelines

Provide structured, step-by-step plans.""",
    can_visualize=True,
    can_read_state=True
)

web_search_agent = create_sub_agent(
    name="web_search",
    system_prompt="""You are a precise research specialist.

Provide well-sourced, accurate information:
- Start with a brief summary
- Include key facts in bullet points
- Cite sources when possible
- Stay objective and factual""",
    can_visualize=False,
    can_read_state=False
)

summarizer_agent = create_sub_agent(
    name="summarizer",
    system_prompt="""You are an expert at distilling information into clear, concise summaries.

Create summaries that:
- Capture all key points
- Use hierarchical structure
- Are easy to scan
- Maintain accuracy""",
    can_visualize=False,
    can_read_state=True
)


# ============================================================================
# SUB-AGENT REGISTRY
# ============================================================================

SUB_AGENTS = {
    "web_search": {
        "agent": web_search_agent,
        "description": "Real-time web research and information gathering",
        "capabilities": ["research", "fact-finding", "current events"]
    },
    "summarizer": {
        "agent": summarizer_agent,
        "description": "Summarize content into concise key points",
        "capabilities": ["summarization", "distillation"]
    },
    "analyzer": {
        "agent": analyzer_agent,
        "description": "Deep analysis with insights and visualizations",
        "capabilities": ["analysis", "patterns", "charts"]
    },
    "report_generator": {
        "agent": report_generator_agent,
        "description": "Professional structured reports with visuals",
        "capabilities": ["reporting", "documentation", "charts"]
    },
    "visualizer": {
        "agent": visualizer_agent,
        "description": "Generate beautiful charts from task data",
        "capabilities": ["charts", "graphs", "visualization"]
    },
    "planning": {
        "agent": planning_agent,
        "description": "Strategic planning and task breakdown",
        "capabilities": ["planning", "prioritization", "strategy"]
    }
}


def get_agent_info() -> dict:
    """Get info about available sub-agents"""
    return {
        name: {
            "description": info["description"],
            "capabilities": info["capabilities"]
        }
        for name, info in SUB_AGENTS.items()
    }