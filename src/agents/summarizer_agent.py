#!/usr/bin/env python3
"""
Summarizer Agent - Specialized agent for text summarization and content analysis
Part of the multi-agent workflow automation system
"""

import os
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()


class SummarizerAgent:
    """
    Specialized agent for text summarization, content analysis, and document processing.
    Handles complex text analysis tasks delegated by the supervisor agent.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the summarizer agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,
            max_tokens=1000  # Optimized for summaries
        )
        
        self.agent_type = "summarization"
        self.model = model_name
        
        # Create processing chain
        self.chain = self._create_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the summarizer agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are an expert Document Analysis and Summarization Specialist with deep expertise in information extraction, content analysis, and executive communication. You transform complex documents into clear, actionable insights.

{current_info}

CRITICAL RULE: You are a SUMMARIZATION specialist. NEVER include code examples, programming snippets, or technical implementations in your summaries unless the original content is specifically about code. Focus purely on summarizing and analyzing the content provided.

RESPONSE STYLE:
- Professional and analytical, like a senior business analyst
- Well-structured with clear headers and sections
- Executive-ready summaries with strategic insights
- Comprehensive yet concise and actionable
- Include key metrics, trends, and recommendations
- NO CODE EXAMPLES unless summarizing technical documentation

CORE EXPERTISE:
- **Document Analysis**: Deep content analysis, pattern recognition, insight extraction
- **Executive Summarization**: C-level ready summaries with strategic implications
- **Information Synthesis**: Combining multiple sources into coherent narratives
- **Key Insight Identification**: Finding critical information and hidden patterns
- **Strategic Analysis**: Business implications, opportunities, and risks
- **Actionable Recommendations**: Next steps and implementation guidance

ANALYSIS SPECIALIZATIONS:
- **Business Reports**: Financial analysis, performance metrics, strategic insights
- **Market Research**: Consumer insights, competitive analysis, trend identification
- **Technical Documentation**: Complex technical content simplified for stakeholders
- **Academic Papers**: Research findings, methodologies, practical applications
- **Legal Documents**: Key terms, obligations, risks, and compliance requirements
- **Project Reports**: Status updates, milestones, risks, and recommendations
- **Biographical Content**: Life achievements, career highlights, impact analysis

RESPONSE STRUCTURE:
## Executive Summary
High-level overview and key takeaways

## Critical Insights
Most important findings and discoveries

## Key Metrics & Data
Important numbers, statistics, and measurements (when applicable)

## Strategic Implications
Business impact and strategic considerations (when applicable)

## Actionable Recommendations
Specific next steps and implementation guidance (when applicable)

IMPORTANT: Adapt the structure to the content type. For biographical content, focus on achievements, timeline, and impact. For business content, focus on metrics and strategy. NEVER add code examples to non-technical summaries.

Always provide professional, executive-level analysis that demonstrates deep analytical expertise and strategic thinking. Stay focused on summarizing the actual content provided."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Please analyze and summarize the following content:\n\n{content}\n\nTask: {task}")
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def summarize_text(self, content: str, task_description: str = "Create a comprehensive summary") -> Dict[str, Any]:
        """Summarize the provided text content."""
        try:
            # Process the content
            summary = self.chain.invoke({
                "content": content,
                "task": task_description
            })
            
            # Add metadata
            word_count_original = len(content.split())
            word_count_summary = len(summary.split())
            compression_ratio = round((1 - word_count_summary / word_count_original) * 100, 1) if word_count_original > 0 else 0
            
            enhanced_summary = f"""## Content Summary

{summary}

---
**Summary Statistics:**
- Original: {word_count_original} words
- Summary: {word_count_summary} words  
- Compression: {compression_ratio}% reduction
- Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

            return {
                "success": True,
                "summary": enhanced_summary,
                "original_length": word_count_original,
                "summary_length": word_count_summary,
                "compression_ratio": compression_ratio,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": f"Error during summarization: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def analyze_document(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Perform detailed document analysis."""
        analysis_prompts = {
            "general": "Provide a comprehensive analysis of this document including key themes, structure, and insights.",
            "technical": "Analyze this technical document focusing on methodologies, findings, and technical details.",
            "business": "Analyze this business document focusing on strategic insights, opportunities, and recommendations.",
            "academic": "Provide an academic analysis including methodology, findings, and scholarly significance."
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        
        try:
            analysis = self.chain.invoke({
                "content": content,
                "task": prompt
            })
            
            return {
                "success": True,
                "analysis": analysis,
                "analysis_type": analysis_type,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": f"Error during analysis: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def extract_key_points(self, content: str, max_points: int = 10) -> Dict[str, Any]:
        """Extract key points from the content."""
        try:
            task = f"Extract the {max_points} most important key points from this content. Present them as a clear, numbered list."
            
            key_points = self.chain.invoke({
                "content": content,
                "task": task
            })
            
            return {
                "success": True,
                "key_points": key_points,
                "max_points": max_points,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "key_points": f"Error extracting key points: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def process_task(self, task_description: str, content: str = "") -> Dict[str, Any]:
        """Main method to process summarization tasks."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="SummarizerAgent - Process Task",
            metadata={
                "agent": "SummarizerAgent",
                "task": task_description[:100],
                "content_length": len(content),
                "has_content": bool(content)
            },
            tags=["sub_agent", "summarizer", "execution"]
        )
        def execute_summarization(task_input: str, content_input: str = ""):  # ← Parameters show in Input tab
            try:
                # Determine the type of task
                task_lower = task_input.lower()
                
                if "summarize" in task_lower or "summary" in task_lower:
                    return self.summarize_text(content_input, task_input)
                elif "analyze" in task_lower or "analysis" in task_lower:
                    analysis_type = "technical" if "technical" in task_lower else "general"
                    return self.analyze_document(content_input, analysis_type)
                elif "key points" in task_lower or "extract" in task_lower:
                    return self.extract_key_points(content_input)
                else:
                    # Default to summarization
                    return self.summarize_text(content_input, task_input)
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "result": f"Summarizer Agent Error: {str(e)}",
                    "agent_type": self.agent_type
                }
        
        return execute_summarization(task_description, content)  # ← Pass parameters
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the summarizer agent."""
        return {
            "agent_type": self.agent_type,
            "name": "SummarizerAgent",
            "description": "Specialized in text summarization and content analysis",
            "capabilities": [
                "Text summarization with compression statistics",
                "Document analysis (general, technical, business, academic)",
                "Key point extraction",
                "Content structure analysis",
                "Theme identification"
            ],
            "optimal_for": [
                "Long document summarization",
                "Research paper analysis",
                "Meeting notes processing",
                "Content review and synthesis",
                "Information extraction"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY"))
        }