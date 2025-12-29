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
        return """You are a Summarization Agent, specialized in text analysis and content summarization.

CORE CAPABILITIES:
- Extract key information from long documents
- Create concise, comprehensive summaries
- Identify main themes and important points
- Analyze document structure and content
- Provide actionable insights from text

SUMMARIZATION PRINCIPLES:
1. **Accuracy**: Maintain factual correctness
2. **Completeness**: Cover all important points
3. **Conciseness**: Remove redundancy while preserving meaning
4. **Clarity**: Use clear, accessible language
5. **Structure**: Organize information logically

OUTPUT FORMAT:
- Use **bold** for key points and section headers
- Use bullet points (-) for main ideas
- Use numbered lists (1. 2. 3.) for sequential information
- Highlight important terms with `backticks`
- Provide clear section breaks

ANALYSIS APPROACH:
1. **Overview**: Brief description of the content
2. **Key Points**: Main ideas and important information
3. **Themes**: Recurring topics and patterns
4. **Insights**: Analysis and implications
5. **Recommendations**: Actionable next steps (if applicable)

Always provide value-driven summaries that help users quickly understand and act on the information."""
    
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
            
            enhanced_summary = f"""## 📄 **Content Summary**

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
        try:
            # Determine the type of task
            task_lower = task_description.lower()
            
            if "summarize" in task_lower or "summary" in task_lower:
                return self.summarize_text(content, task_description)
            elif "analyze" in task_lower or "analysis" in task_lower:
                analysis_type = "technical" if "technical" in task_lower else "general"
                return self.analyze_document(content, analysis_type)
            elif "key points" in task_lower or "extract" in task_lower:
                return self.extract_key_points(content)
            else:
                # Default to summarization
                return self.summarize_text(content, task_description)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": f"Summarizer Agent Error: {str(e)}",
                "agent_type": self.agent_type
            }
    
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