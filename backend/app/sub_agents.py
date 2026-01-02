import json
from .utils import call_gemini


# =========================================================
# ENHANCED SUB-AGENT FACTORY
# =========================================================

def create_sub_agent(
    name: str,
    system_prompt: str,
    can_visualize: bool = False,
    can_read_state: bool = False,
    output_format: str = "prose"  # prose, json, markdown
):
    """
    Create a specialized sub-agent with specific capabilities
    
    Args:
        name: Agent identifier
        system_prompt: Instructions for the agent
        can_visualize: Whether agent can create charts/tables
        can_read_state: Whether agent can access todos/files (read-only)
        output_format: Expected output format
    """

    def agent_function(input_dict):
        messages = input_dict.get("messages", [])
        state = input_dict.get("state", {})

        # Extract user request
        user_text = ""
        for msg in messages:
            if isinstance(msg, dict):
                user_text += msg.get("content", "") + "\n"
            else:
                user_text += str(msg.content) + "\n"
        user_text = user_text.strip()

        # Build context
        context_sections = []

        # Add state information if allowed
        if can_read_state and state:
            todos = state.get("todos", [])
            files = state.get("files", {})
            calendar = state.get("calendar", [])
            
            if todos:
                pending = [t for t in todos if not t.get("completed")]
                completed = [t for t in todos if t.get("completed")]
                context_sections.append(
                    f"## Current Tasks\n"
                    f"Pending: {len(pending)} tasks\n"
                    f"Completed: {len(completed)} tasks\n"
                    f"Details: {json.dumps(todos, indent=2)}"
                )
            
            if calendar:
                context_sections.append(
                    f"## Calendar Events\n"
                    f"{len(calendar)} events scheduled\n"
                    f"Details: {json.dumps(calendar, indent=2)}"
                )
            
            if files:
                context_sections.append(
                    f"## Available Files\n"
                    f"Files: {', '.join(files.keys())}"
                )

        # Add visualization instructions if enabled
        if can_visualize:
            context_sections.append(
                "## Visualization Capabilities\n"
                "You can create visualizations using JSON format:\n"
                "- Table: {\"type\": \"table\", \"columns\": [\"col1\", \"col2\"], \"rows\": [[\"val1\", \"val2\"]]}\n"
                "- Bar Chart: {\"type\": \"bar_chart\", \"x\": [...], \"y\": [...], \"title\": \"...\"}\n"
                "- Line Chart: {\"type\": \"line_chart\", \"x\": [...], \"y\": [...], \"title\": \"...\"}\n"
                "- Pie Chart: {\"type\": \"pie_chart\", \"labels\": [...], \"values\": [...], \"title\": \"...\"}"
            )

        # Build full prompt
        context_text = "\n\n".join(context_sections) if context_sections else ""
        
        full_prompt = f"""{system_prompt}

{context_text}

## User Request
{user_text}

Please provide a comprehensive and accurate response."""

        # Call LLM
        response = call_gemini(full_prompt)

        return {
            "messages": [{"role": "assistant", "content": response}],
            "raw": response
        }

    return agent_function


# =========================================================
# SPECIALIZED SUB-AGENTS
# =========================================================

web_search_agent = create_sub_agent(
    name="web_search",
    system_prompt="""You are a research specialist agent focused on providing accurate, up-to-date information.

Your role:
- Provide comprehensive research on any topic
- Focus on accuracy, recency, and relevance
- Structure information clearly with sources when possible
- Highlight key findings and actionable insights
- Use bullet points and clear formatting

Be thorough but concise. Prioritize factual information.""",
    can_visualize=False,
    can_read_state=False,
    output_format="markdown"
)

summarizer_agent = create_sub_agent(
    name="summarizer",
    system_prompt="""You are a summarization specialist that distills complex information into clear, concise summaries.

Your role:
- Extract the most important points from any content
- Create well-structured bullet points
- Maintain accuracy while being brief
- Organize information hierarchically
- Use clear headings and sections

Format:
## Key Points
- Main point 1
- Main point 2

## Details
- Supporting detail 1
- Supporting detail 2

Be concise but comprehensive.""",
    can_visualize=False,
    can_read_state=True,
    output_format="markdown"
)

analyzer_agent = create_sub_agent(
    name="analyzer",
    system_prompt="""You are a deep analysis specialist that provides thorough insights and evaluation.

Your role:
- Conduct deep analysis of information, patterns, and trends
- Identify key insights, implications, and recommendations
- Evaluate strengths, weaknesses, opportunities, and threats
- Provide actionable recommendations
- Consider multiple perspectives

Structure your analysis:
## Overview
Brief context

## Key Findings
1. Finding with explanation
2. Finding with explanation

## Analysis
Detailed examination

## Recommendations
Actionable next steps

Be thorough, insightful, and practical.""",
    can_visualize=True,
    can_read_state=True,
    output_format="markdown"
)

report_generator_agent = create_sub_agent(
    name="report_generator",
    system_prompt="""You are a professional report writer that creates structured, comprehensive reports.

Your role:
- Create well-formatted professional reports
- Use clear structure with executive summary
- Include relevant data and insights
- Maintain professional tone
- Provide actionable recommendations

Report Structure:
# [Title]

## Executive Summary
Brief overview of key points

## Introduction
Context and purpose

## Main Sections
### Section 1
Detailed content

### Section 2
Detailed content

## Conclusions
Key takeaways

## Recommendations
Actionable next steps

Use professional language and clear formatting.""",
    can_visualize=True,
    can_read_state=True,
    output_format="markdown"
)

visualizer_agent = create_sub_agent(
    name="visualizer",
    system_prompt="""You are a data visualization specialist that creates charts and tables.

Your role:
- Transform data into visual representations
- Create appropriate chart types for the data
- Ensure visualizations are clear and informative
- Include proper labels and titles

When creating visualizations, respond with JSON:

For tables:
{
  "type": "table",
  "title": "Table Title",
  "columns": ["Column 1", "Column 2"],
  "rows": [["Data 1", "Data 2"], ["Data 3", "Data 4"]]
}

For bar charts:
{
  "type": "bar_chart",
  "title": "Chart Title",
  "x_label": "X Axis",
  "y_label": "Y Axis",
  "x": ["Category 1", "Category 2"],
  "y": [10, 20]
}

For pie charts:
{
  "type": "pie_chart",
  "title": "Chart Title",
  "labels": ["Slice 1", "Slice 2"],
  "values": [30, 70]
}

Choose the most appropriate visualization type for the data.""",
    can_visualize=True,
    can_read_state=True,
    output_format="json"
)

# =========================================================
# ADVANCED: PLANNING SUB-AGENT
# =========================================================

planning_agent = create_sub_agent(
    name="planning",
    system_prompt="""You are a strategic planning specialist that helps break down complex goals into actionable tasks.

Your role:
- Analyze goals and create detailed action plans
- Break down large projects into manageable tasks
- Prioritize tasks by importance and dependencies
- Suggest realistic timelines
- Identify potential challenges

Output Format:
## Goal Analysis
[Brief analysis of the goal]

## Action Plan
### Phase 1: [Phase Name]
- **Task**: [Task description]
  - Priority: High/Medium/Low
  - Estimated Time: [duration]
  - Dependencies: [if any]

### Phase 2: [Phase Name]
[Continue...]

## Timeline
[Suggested schedule]

## Potential Challenges
- Challenge 1: [mitigation strategy]
- Challenge 2: [mitigation strategy]

Be practical and thorough.""",
    can_visualize=True,
    can_read_state=True,
    output_format="markdown"
)


# =========================================================
# SUB-AGENT REGISTRY
# =========================================================

SUB_AGENTS = {
    "web_search": {
        "agent": web_search_agent,
        "description": "Real-time web research and information gathering",
        "capabilities": ["research", "fact-finding", "current events"]
    },
    "summarizer": {
        "agent": summarizer_agent,
        "description": "Summarize content into concise bullet points",
        "capabilities": ["summarization", "key points extraction", "brevity"]
    },
    "analyzer": {
        "agent": analyzer_agent,
        "description": "Deep analysis and insights",
        "capabilities": ["analysis", "evaluation", "recommendations", "visualization"]
    },
    "report_generator": {
        "agent": report_generator_agent,
        "description": "Create professional structured reports",
        "capabilities": ["report writing", "documentation", "visualization"]
    },
    "visualizer": {
        "agent": visualizer_agent,
        "description": "Generate tables and charts from data",
        "capabilities": ["charts", "tables", "data visualization"]
    },
    "planning": {
        "agent": planning_agent,
        "description": "Strategic planning and task breakdown",
        "capabilities": ["planning", "task breakdown", "prioritization", "timelines"]
    }
}


def get_agent_info() -> dict:
    """Return information about all available sub-agents"""
    return {
        name: {
            "description": info["description"],
            "capabilities": info["capabilities"]
        }
        for name, info in SUB_AGENTS.items()
    }