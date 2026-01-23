#!/usr/bin/env python3
"""
Planning Agent - Specialized agent for project planning, strategy, and organization
Part of the multi-agent workflow automation system
"""

import os
from typing import Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()


class PlanningAgent:
    """
    Specialized agent for project planning, strategic thinking, and organizational tasks.
    Handles planning and strategy tasks delegated by the supervisor agent.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the planning agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,  # Lower temperature for faster, more focused responses
            max_tokens=800    # Reduced tokens for faster generation
        )
        
        self.agent_type = "planning"
        self.model = model_name
        
        # Create processing chain
        self.chain = self._create_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the optimized system prompt for the planning agent."""
        now = datetime.now()
        current_info = f"Current Date: {now.strftime('%Y-%m-%d')} ({now.strftime('%A')})"
        
        return f"""You are a Strategic Planning Expert specializing in project management, business strategy, and travel planning.

{current_info}

CORE EXPERTISE:
- Strategic Planning & Business Strategy
- Project Management & Timeline Development  
- Travel Planning & Itinerary Creation
- Risk Assessment & Mitigation
- Budget Planning & Resource Allocation

RESPONSE FORMAT:
## Overview
Brief summary of the plan

## Key Components
Main elements and requirements

## Implementation
Step-by-step execution plan

## Timeline & Budget
Realistic timeframes and cost estimates

## Recommendations
Best practices and success tips

Keep responses focused, actionable, and professional. Provide practical solutions with clear next steps."""
    
    def _create_chain(self):
        """Create the optimized LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "{task}")
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def create_project_plan(self, project: str, timeline: str = "3 months", context: str = "") -> Dict[str, Any]:
        """Create a comprehensive project plan."""
        try:
            planning_task = f"Create a detailed project plan for: {project} (Timeline: {timeline})"
            
            project_plan = self.chain.invoke({
                "task": planning_task,
                "context": context
            })
            
            enhanced_plan = f"""## Project Plan: {project}

**Timeline**: {timeline}
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{project_plan}

---

**Planning Notes**:
- Plan includes realistic timelines with buffers
- Consider regular review points for adjustments
- Identify critical dependencies early
- Monitor progress against key milestones"""

            return {
                "success": True,
                "project_plan": enhanced_plan,
                "project": project,
                "timeline": timeline,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "project_plan": f"Error creating project plan: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_strategy(self, goal: str, strategy_type: str = "business") -> Dict[str, Any]:
        """Create strategic plans and roadmaps."""
        try:
            strategy_task = f"Create a {strategy_type} strategy for: {goal}"
            
            strategy_result = self.chain.invoke({
                "task": strategy_task,
                "context": f"Strategy type: {strategy_type}"
            })
            
            return {
                "success": True,
                "strategy": strategy_result,
                "goal": goal,
                "strategy_type": strategy_type,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "strategy": f"Error creating strategy: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def break_down_tasks(self, main_task: str, detail_level: str = "detailed") -> Dict[str, Any]:
        """Break down complex tasks into manageable subtasks."""
        try:
            breakdown_task = f"Break down this complex task into {detail_level} subtasks: {main_task}"
            
            task_breakdown = self.chain.invoke({
                "task": breakdown_task,
                "context": f"Detail level: {detail_level}"
            })
            
            return {
                "success": True,
                "task_breakdown": task_breakdown,
                "main_task": main_task,
                "detail_level": detail_level,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task_breakdown": f"Error breaking down tasks: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_travel_plan(self, destination: str, duration: str, context: str = "") -> Dict[str, Any]:
        """Create detailed travel itineraries and plans."""
        try:
            travel_task = f"Create a comprehensive {duration} travel itinerary for {destination}"
            
            travel_plan = self.chain.invoke({
                "task": travel_task,
                "context": f"Travel planning for {destination}, Duration: {duration}, Additional context: {context}"
            })
            
            enhanced_plan = f"""## {duration.title()} Travel Plan: {destination.title()}

**Duration**: {duration}
**Destination**: {destination.title()}
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{travel_plan}

---

**Travel Planning Notes**:
- Check weather conditions before departure
- Book accommodations and transportation in advance
- Keep emergency contacts and important documents handy
- Consider travel insurance for international trips"""

            return {
                "success": True,
                "project_plan": enhanced_plan,
                "destination": destination,
                "duration": duration,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "project_plan": f"Error creating travel plan: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_timeline(self, project: str, duration: str, milestones: str = "") -> Dict[str, Any]:
        """Create detailed timelines with milestones."""
        try:
            timeline_task = f"Create a detailed timeline for: {project} (Duration: {duration})"
            if milestones:
                timeline_task += f" with these key milestones: {milestones}"
            
            timeline_result = self.chain.invoke({
                "task": timeline_task,
                "context": f"Duration: {duration}, Milestones: {milestones}"
            })
            
            return {
                "success": True,
                "timeline": timeline_result,
                "project": project,
                "duration": duration,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timeline": f"Error creating timeline: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def process_task(self, task_description: str, context: str = "") -> Dict[str, Any]:
        """Main method to process planning tasks."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="PlanningAgent - Process Task",
            metadata={
                "agent": "PlanningAgent",
                "task": task_description[:100],
                "has_context": bool(context),
                "task_type": "planning"
            },
            tags=["sub_agent", "planning", "execution"]
        )
        def execute_planning(task_input: str, context_input: str = ""):  # ← Parameters show in Input tab
            try:
                # Use a single, optimized LLM call instead of multiple methods
                planning_prompt = f"""Create a focused plan for: {task_input}

Context: {context_input if context_input else 'General planning request'}

Provide a concise, actionable plan with:
1. Overview (1-2 sentences)
2. Key Steps (3-5 main actions)
3. Timeline (realistic timeframe)
4. Budget/Resources (if applicable)
5. Success Tips (2-3 recommendations)

Keep the response practical and under 300 words."""

                result = self.chain.invoke({
                    "task": planning_prompt
                })
                
                return {
                    "success": True,
                    "result": result,  # Changed from "plan" to "result" for consistency
                    "plan": result,    # Keep both for compatibility
                    "task_type": "planning",
                    "agent_type": self.agent_type,
                    "created_at": datetime.now().isoformat()
                }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "result": f"Planning Agent Error: {str(e)}",
                    "agent_type": self.agent_type
                }
        
        return execute_planning(task_description, context)  # ← Pass parameters
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the planning agent."""
        return {
            "agent_type": self.agent_type,
            "name": "PlanningAgent",
            "description": "Specialized in strategic planning and project management",
            "capabilities": [
                "Comprehensive project planning",
                "Strategic roadmap creation",
                "Task breakdown and organization",
                "Timeline and milestone planning",
                "Resource allocation planning",
                "Risk assessment and mitigation",
                "Goal setting and OKR creation"
            ],
            "optimal_for": [
                "Project planning and management",
                "Strategic planning and roadmaps",
                "Task organization and breakdown",
                "Timeline creation and scheduling",
                "Business strategy development",
                "Goal setting and milestone tracking"
            ],
            "methodologies": [
                "Agile/Scrum", "Waterfall", "Kanban", "OKRs", "SMART Goals"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY"))
        }