#!/usr/bin/env python3
"""
Code Agent - Specialized agent for programming and code-related tasks
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


class CodeAgent:
    """
    Specialized agent for programming, code analysis, debugging, and software development tasks.
    Handles code-related tasks delegated by the supervisor agent.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the code agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,
            max_tokens=1500
        )
        
        self.agent_type = "programming"
        self.model = model_name
        
        # Create processing chain
        self.chain = self._create_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the code agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are a Senior Software Engineering Consultant with deep expertise in enterprise software development, system architecture, and engineering best practices. You provide professional, production-ready solutions with strategic technical insights.

{current_info}

RESPONSE STYLE:
- Professional and authoritative, like a senior technical architect
- Well-structured with clear sections and comprehensive explanations
- Include strategic considerations and architectural insights
- Provide enterprise-grade solutions with scalability in mind
- Demonstrate deep technical expertise and industry best practices

CORE EXPERTISE:
- **Enterprise Architecture**: System design, microservices, distributed systems
- **Full-Stack Development**: Frontend, backend, database, and infrastructure
- **Performance Engineering**: Optimization, scalability, load testing, monitoring
- **Security Engineering**: Secure coding, vulnerability assessment, compliance
- **DevOps & Infrastructure**: CI/CD, containerization, cloud architecture, automation
- **Code Quality**: Clean code, design patterns, testing strategies, documentation

TECHNOLOGY SPECIALIZATIONS:
- **Languages**: Python, JavaScript/TypeScript, Java, C#, Go, Rust, SQL
- **Frameworks**: React, Angular, Vue, Django, Flask, Spring Boot, .NET, Express
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, DynamoDB
- **Cloud Platforms**: AWS, Azure, GCP, serverless architectures
- **DevOps Tools**: Docker, Kubernetes, Jenkins, GitHub Actions, Terraform
- **Testing**: Unit testing, integration testing, performance testing, security testing

RESPONSE STRUCTURE:
## Technical Analysis
Assessment of requirements and technical considerations

## Architecture Overview
System design and architectural decisions

## Implementation Solution
Production-ready code with comprehensive explanations

## Security & Performance
Security considerations and performance optimizations

## Testing Strategy
Test cases, validation approaches, and quality assurance

## Deployment & Operations
Implementation guidance and operational considerations

Always provide enterprise-grade, production-ready solutions with professional insights that demonstrate senior-level software engineering expertise.

Always provide production-ready, well-documented code solutions."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Programming Task: {task}\n\nCode Context (if any): {code}\n\nPlease provide a comprehensive solution.")
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def generate_code(self, task: str, language: str = "python", context: str = "") -> Dict[str, Any]:
        """Generate code for a specific task."""
        try:
            full_task = f"Generate {language} code for: {task}"
            if context:
                full_task += f"\nContext: {context}"
            
            code_solution = self.chain.invoke({
                "task": full_task,
                "code": context
            })
            
            enhanced_solution = f"""## Code Generation Result

**Task**: {task}
**Language**: {language}
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{code_solution}

---

**Code Agent Notes**:
- Code follows {language} best practices
- Includes error handling and documentation
- Ready for production use with proper testing
- Consider security implications for production deployment"""

            return {
                "success": True,
                "code_solution": enhanced_solution,
                "task": task,
                "language": language,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code_solution": f"Error generating code: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def debug_code(self, code: str, error_description: str = "") -> Dict[str, Any]:
        """Debug and fix code issues."""
        try:
            debug_task = f"Debug this code and fix any issues. Error description: {error_description}"
            
            debug_result = self.chain.invoke({
                "task": debug_task,
                "code": code
            })
            
            return {
                "success": True,
                "debug_result": debug_result,
                "original_code": code,
                "error_description": error_description,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "debug_result": f"Error during debugging: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def review_code(self, code: str, review_type: str = "general") -> Dict[str, Any]:
        """Perform code review and provide suggestions."""
        try:
            review_task = f"Perform a {review_type} code review focusing on best practices, security, and performance"
            
            review_result = self.chain.invoke({
                "task": review_task,
                "code": code
            })
            
            return {
                "success": True,
                "review_result": review_result,
                "review_type": review_type,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "review_result": f"Error during code review: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def optimize_code(self, code: str, optimization_focus: str = "performance") -> Dict[str, Any]:
        """Optimize code for performance, readability, or other criteria."""
        try:
            optimize_task = f"Optimize this code for {optimization_focus}"
            
            optimization_result = self.chain.invoke({
                "task": optimize_task,
                "code": code
            })
            
            return {
                "success": True,
                "optimization_result": optimization_result,
                "optimization_focus": optimization_focus,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "optimization_result": f"Error during optimization: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def process_task(self, task_description: str, code_context: str = "") -> Dict[str, Any]:
        """Main method to process programming tasks."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="CodeAgent - Process Task",
            metadata={
                "agent": "CodeAgent",
                "task": task_description[:100],
                "has_context": bool(code_context),
                "task_type": "code"
            },
            tags=["sub_agent", "code", "execution"]
        )
        def execute_code(task_input: str, context_input: str = ""):  # ← Parameters show in Input tab
            try:
                task_lower = task_input.lower()
                
                if "generate" in task_lower or "create" in task_lower or "write" in task_lower:
                    # Extract language if mentioned
                    language = "python"  # default
                    if "javascript" in task_lower or "js" in task_lower:
                        language = "javascript"
                    elif "java" in task_lower and "javascript" not in task_lower:
                        language = "java"
                    elif "c++" in task_lower or "cpp" in task_lower:
                        language = "c++"
                    
                    return self.generate_code(task_input, language, context_input)
                    
                elif "debug" in task_lower or "fix" in task_lower or "error" in task_lower:
                    return self.debug_code(context_input, task_input)
                    
                elif "review" in task_lower or "analyze" in task_lower:
                    review_type = "security" if "security" in task_lower else "general"
                    return self.review_code(context_input, review_type)
                    
                elif "optimize" in task_lower or "improve" in task_lower:
                    focus = "performance" if "performance" in task_lower else "readability"
                    return self.optimize_code(context_input, focus)
                    
                else:
                    # Default to code generation
                    return self.generate_code(task_input, "python", context_input)
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "result": f"Code Agent Error: {str(e)}",
                    "agent_type": self.agent_type
                }
        
        return execute_code(task_description, code_context)  # ← Pass parameters
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the code agent."""
        return {
            "agent_type": self.agent_type,
            "name": "CodeAgent",
            "description": "Specialized in programming and software development",
            "capabilities": [
                "Code generation in multiple languages",
                "Bug detection and debugging",
                "Code review and analysis",
                "Performance optimization",
                "Security analysis",
                "Architecture recommendations",
                "Documentation generation"
            ],
            "optimal_for": [
                "Writing new code and functions",
                "Debugging and fixing errors",
                "Code review and optimization",
                "Architecture design",
                "Security analysis",
                "Performance improvements"
            ],
            "supported_languages": [
                "Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY"))
        }