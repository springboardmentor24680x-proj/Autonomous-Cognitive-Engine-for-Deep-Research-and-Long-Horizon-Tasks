#!/usr/bin/env python3
"""
Translation Agent - Specialized agent for language translation and localization
Part of the multi-agent workflow automation system
Enhanced with dedicated translation tools for better tracing and functionality
"""

import os
import json
import re
from typing import Dict, Any, List, Union
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import translation tools
from tools.translation_tools import (
    translate_text, localize_content, translate_document, 
    create_multilingual_content, detect_language, get_supported_languages
)

# Load environment variables
load_dotenv()


class TranslationAgent:
    """
    Specialized agent for language translation, localization, and multilingual content creation.
    Handles text translation, document localization, and cross-cultural communication tasks.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the translation agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.1,  # Low temperature for accurate translations
            max_tokens=2000
        )
        
        self.agent_type = "translation"
        self.model = model_name
        
        # Import and bind translation tools
        from tools.translation_tools import (
            translate_text, localize_content, translate_document, 
            create_multilingual_content, detect_language
        )
        
        # Bind tools to the LLM for proper tracing
        self.tools = [
            translate_text,
            localize_content, 
            translate_document,
            create_multilingual_content,
            detect_language
        ]
        
        # Create tool-enabled LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Supported languages
        self.supported_languages = get_supported_languages()
        
        # Create processing chains
        self.translation_chain = self._create_translation_chain()
        self.localization_chain = self._create_localization_chain()
        self.document_chain = self._create_document_chain()
        self.multilingual_chain = self._create_multilingual_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the translation agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are an expert Translation and Localization Specialist with deep expertise in multilingual communication, cultural adaptation, and professional translation services. You provide comprehensive language solutions that go beyond simple translation.

{current_info}

RESPONSE STYLE:
- Professional and comprehensive, providing context and insights
- Well-structured with clear sections and formatting
- Include cultural considerations and localization notes
- Provide strategic recommendations for global communication
- Maintain accuracy while explaining nuances and alternatives

CORE EXPERTISE:
- **Professional Translation**: Business documents, technical content, marketing materials
- **Cultural Localization**: Adapting content for specific markets and cultures
- **Multilingual Strategy**: Global communication planning and execution
- **Quality Assurance**: Translation accuracy, cultural appropriateness, tone consistency
- **Content Adaptation**: SEO localization, cultural sensitivity, market-specific messaging
- **Language Consulting**: Best practices, style guides, terminology management

TRANSLATION SPECIALIZATIONS:
- **Business Communications**: Contracts, proposals, presentations, emails
- **Marketing Content**: Campaigns, websites, social media, advertising copy
- **Technical Documentation**: User manuals, specifications, software interfaces
- **Legal Documents**: Terms of service, privacy policies, compliance materials
- **Creative Content**: Brand messaging, storytelling, creative campaigns
- **Educational Materials**: Training content, courses, instructional guides

RESPONSE STRUCTURE:
## Translation Overview
Brief analysis of the content and translation approach

## Primary Translation
High-quality, professional translation

## Cultural Considerations
Localization notes and cultural adaptations

## Alternative Versions
Context-specific variations when applicable

## Quality Notes
Accuracy assessment and recommendations

## Implementation Guidance
Best practices for using the translated content

Always provide professional, accurate translations with strategic insights that demonstrate deep linguistic and cultural expertise."""
    
    def _create_translation_chain(self):
        """Create the translation chain for simple text translation."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Translate this text to {target_language}:\n\n{content}")
        ])
        return prompt | self.llm | StrOutputParser()
    
    def _create_localization_chain(self):
        """Create the localization chain for cultural adaptation."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt() + "\n\nFor localization tasks, adapt the content culturally while translating."),
            ("human", "Localize this content for {target_culture}:\n\n{content}")
        ])
        return prompt | self.llm | StrOutputParser()
    
    def _create_document_chain(self):
        """Create the document translation chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt() + "\n\nFor document translation, preserve formatting and structure."),
            ("human", "Translate this {document_type} document to {target_language}:\n\n{content}")
        ])
        return prompt | self.llm | StrOutputParser()
    
    def _create_multilingual_chain(self):
        """Create the multilingual content chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt() + "\n\nFor multilingual content, provide clean translations for each language."),
            ("human", "Translate this content to {target_language}:\n\n{content}")
        ])
        return prompt | self.llm | StrOutputParser()
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto", context: str = "") -> Dict[str, Any]:
        """Translate text from source language to target language."""
        try:
            # Normalize language names
            target_lang = self._normalize_language(target_language)
            source_lang = self._normalize_language(source_language) if source_language != "auto" else "auto-detect"
            
            if not target_lang:
                return {
                    "success": False,
                    "error": f"Unsupported target language: {target_language}",
                    "supported_languages": list(self.supported_languages.keys())
                }
            
            translation_result = self.translation_chain.invoke({
                "content": text,
                "target_language": target_lang
            })
            
            return {
                "success": True,
                "translation": translation_result,
                "source_language": source_lang,
                "target_language": target_lang,
                "original_text": text,
                "context": context,
                "agent_type": self.agent_type,
                "translated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "translation": f"Translation error: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def localize_content(self, content: str, target_culture: str, content_type: str = "general") -> Dict[str, Any]:
        """Localize content for a specific culture and market."""
        try:
            localization_result = self.localization_chain.invoke({
                "content": content,
                "target_culture": target_culture
            })
            
            return {
                "success": True,
                "localized_content": localization_result,
                "target_culture": target_culture,
                "content_type": content_type,
                "original_content": content,
                "agent_type": self.agent_type,
                "localized_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "localized_content": f"Localization error: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def translate_document(self, document_content: str, target_language: str, document_type: str = "general", preserve_formatting: bool = True) -> Dict[str, Any]:
        """Translate an entire document while preserving structure and formatting."""
        try:
            target_lang = self._normalize_language(target_language)
            
            if not target_lang:
                return {
                    "success": False,
                    "error": f"Unsupported target language: {target_language}",
                    "supported_languages": list(self.supported_languages.keys())
                }
            
            document_result = self.document_chain.invoke({
                "content": document_content,
                "target_language": target_lang,
                "document_type": document_type
            })
            
            return {
                "success": True,
                "translated_document": document_result,
                "target_language": target_lang,
                "document_type": document_type,
                "preserve_formatting": preserve_formatting,
                "original_document": document_content,
                "agent_type": self.agent_type,
                "translated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "translated_document": f"Document translation error: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_multilingual_content(self, base_content: str, target_languages: List[str], content_type: str = "general") -> Dict[str, Any]:
        """Create multilingual versions of content for multiple target languages."""
        try:
            translations = {}
            errors = []
            
            for language in target_languages:
                result = self.translate_text(base_content, language, context=f"Multilingual {content_type} content")
                
                if result["success"]:
                    translations[language] = result["translation"]
                else:
                    errors.append(f"{language}: {result['error']}")
            
            return {
                "success": len(translations) > 0,
                "multilingual_content": translations,
                "target_languages": target_languages,
                "successful_translations": len(translations),
                "failed_translations": len(errors),
                "errors": errors,
                "content_type": content_type,
                "base_content": base_content,
                "agent_type": self.agent_type,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "multilingual_content": {},
                "agent_type": self.agent_type
            }
    
    def assess_translation_quality(self, original_text: str, translated_text: str, target_language: str) -> Dict[str, Any]:
        """Assess the quality of a translation and provide improvement suggestions."""
        try:
            target_lang = self._normalize_language(target_language)
            
            assessment_task = f"Assess the quality of this translation to {target_lang}. Evaluate accuracy, fluency, cultural appropriateness, and naturalness. Provide specific feedback and suggestions for improvement."
            
            assessment_content = f"Original Text: {original_text}\n\nTranslation: {translated_text}"
            
            assessment_result = self.chain.invoke({
                "task": assessment_task,
                "content": assessment_content,
                "target_language": target_lang,
                "source_language": "original",
                "context": "Translation quality assessment"
            })
            
            return {
                "success": True,
                "quality_assessment": assessment_result,
                "original_text": original_text,
                "translated_text": translated_text,
                "target_language": target_lang,
                "agent_type": self.agent_type,
                "assessed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "quality_assessment": f"Assessment error: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def _normalize_language(self, language: str) -> str:
        """Normalize language name to standard format."""
        if not language or language == "auto":
            return None
            
        language_lower = language.lower().strip()
        
        # Direct match
        if language_lower in self.supported_languages:
            return language_lower
        
        # Check for language codes
        for lang_name, lang_code in self.supported_languages.items():
            if language_lower == lang_code:
                return lang_name
        
        # Partial matches
        for lang_name in self.supported_languages:
            if language_lower in lang_name or lang_name in language_lower:
                return lang_name
        
        return None
    
    def process_task(self, task_description: str, content: str = "") -> Dict[str, Any]:
        """Main method to process translation tasks."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="TranslationAgent - Process Task",
            metadata={
                "agent": "TranslationAgent",
                "task": task_description[:100],
                "has_content": bool(content),
                "task_type": "translation",
                "tools_available": [tool.name for tool in self.tools]
            },
            tags=["sub_agent", "translation", "execution"]
        )
        def execute_translation(task_input: str, content_input: str = ""):
            try:
                task_lower = task_input.lower()
                
                # If no content provided, try to extract it from the task description
                translation_content = content_input
                if not translation_content:
                    translation_content = self._extract_content_from_task(task_input)
                
                # Extract languages from task description
                target_language = self._extract_target_language(task_input)
                source_language = self._extract_source_language(task_input)
                
                # Import tools for direct invocation with tracing
                from langsmith import traceable as trace_tool
                
                # Determine task type and execute using tools with proper tracing
                if "localize" in task_lower or "localization" in task_lower:
                    culture = target_language or "international"
                    content_type = self._extract_content_type(task_input)
                    
                    @trace_tool(name="Tool: localize_content", tags=["translation_tool"])
                    def call_localize_tool():
                        return localize_content.invoke({
                            "content": translation_content,
                            "target_culture": culture,
                            "content_type": content_type
                        })
                    return call_localize_tool()
                    
                elif "document" in task_lower or "file" in task_lower:
                    if not target_language:
                        target_language = "spanish"  # Default
                    document_type = self._extract_content_type(task_input)
                    
                    @trace_tool(name="Tool: translate_document", tags=["translation_tool"])
                    def call_document_tool():
                        return translate_document.invoke({
                            "document_content": translation_content,
                            "target_language": target_language,
                            "document_type": document_type
                        })
                    return call_document_tool()
                    
                elif "multilingual" in task_lower or "multiple language" in task_lower:
                    languages = self._extract_multiple_languages(task_input)
                    if not languages:
                        languages = ["spanish", "french", "german"]  # Default
                    
                    @trace_tool(name="Tool: create_multilingual_content", tags=["translation_tool"])
                    def call_multilingual_tool():
                        return create_multilingual_content.invoke({
                            "base_content": translation_content,
                            "target_languages": languages
                        })
                    return call_multilingual_tool()
                    
                elif "detect" in task_lower or "identify" in task_lower:
                    @trace_tool(name="Tool: detect_language", tags=["translation_tool"])
                    def call_detect_tool():
                        return detect_language.invoke({
                            "text": translation_content
                        })
                    return call_detect_tool()
                    
                else:
                    # Default to text translation using the tool
                    if not target_language:
                        target_language = "spanish"  # Default
                    
                    @trace_tool(name="Tool: translate_text", tags=["translation_tool"])
                    def call_translate_tool():
                        return translate_text.invoke({
                            "text": translation_content,
                            "target_language": target_language,
                            "source_language": source_language
                        })
                    return call_translate_tool()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "result": f"Translation Agent Error: {str(e)}",
                    "agent_type": self.agent_type
                }
        
        return execute_translation(task_description, content)
    
    def _extract_target_language(self, task: str) -> str:
        """Extract target language from task description."""
        task_lower = task.lower()
        
        # Look for "to [language]" patterns
        to_patterns = [
            r"to\s+(\w+)",
            r"into\s+(\w+)",
            r"in\s+(\w+)",
        ]
        
        for pattern in to_patterns:
            match = re.search(pattern, task_lower)
            if match:
                potential_lang = match.group(1)
                if self._normalize_language(potential_lang):
                    return self._normalize_language(potential_lang)
        
        # Look for direct language mentions
        for language in self.supported_languages:
            if language in task_lower:
                return language
        
        return None
    
    def _extract_source_language(self, task: str) -> str:
        """Extract source language from task description."""
        task_lower = task.lower()
        
        # Look for "from [language]" patterns
        from_patterns = [
            r"from\s+(\w+)",
            r"translate\s+(\w+)",
        ]
        
        for pattern in from_patterns:
            match = re.search(pattern, task_lower)
            if match:
                potential_lang = match.group(1)
                if self._normalize_language(potential_lang):
                    return self._normalize_language(potential_lang)
        
        return "auto"
    
    def _extract_multiple_languages(self, task: str) -> List[str]:
        """Extract multiple target languages from task description."""
        languages = []
        task_lower = task.lower()
        
        for language in self.supported_languages:
            if language in task_lower:
                languages.append(language)
        
        return languages[:5]  # Limit to 5 languages
    
    def _extract_content_type(self, task: str) -> str:
        """Extract content type from task description."""
        task_lower = task.lower()
        
        content_types = {
            "business": ["business", "corporate", "professional"],
            "marketing": ["marketing", "advertisement", "promotional"],
            "technical": ["technical", "documentation", "manual"],
            "legal": ["legal", "contract", "terms"],
            "creative": ["creative", "story", "literature"],
            "website": ["website", "web", "online"],
            "email": ["email", "message", "communication"]
        }
        
        for content_type, keywords in content_types.items():
            if any(keyword in task_lower for keyword in keywords):
                return content_type
        
        return "general"
    
    def _extract_context(self, task: str) -> str:
        """Extract context information from task description."""
        task_lower = task.lower()
        
        contexts = []
        if "business" in task_lower:
            contexts.append("business context")
        if "formal" in task_lower:
            contexts.append("formal tone")
        if "casual" in task_lower:
            contexts.append("casual tone")
        if "technical" in task_lower:
            contexts.append("technical content")
        
        return ", ".join(contexts) if contexts else "general context"
    
    def _extract_content_from_task(self, task: str) -> str:
        """Extract content to translate from the task description."""
        task_lower = task.lower()
        
        # Common patterns for content extraction
        patterns = [
            r"translate\s+this\s+to\s+\w+:\s*[\"']?([^\"']+)[\"']?",
            r"translate\s+[\"']([^\"']+)[\"']\s+to\s+\w+",
            r"translate\s+this:\s*[\"']?([^\"']+)[\"']?",
            r"translate\s+[\"']([^\"']+)[\"']",
            r":\s*[\"']([^\"']+)[\"']",
            r":\s*(.+)$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Clean up common prefixes/suffixes
                content = re.sub(r'^(this|the)\s+', '', content, flags=re.IGNORECASE)
                if len(content) > 3:  # Avoid extracting very short matches
                    return content
        
        # If no pattern matches, look for quoted content
        quotes_match = re.search(r'["\']([^"\']{4,})["\']', task)
        if quotes_match:
            return quotes_match.group(1).strip()
        
        # Last resort: look for content after common keywords
        keywords = ["translate", "localize", "convert"]
        for keyword in keywords:
            if keyword in task_lower:
                parts = task.split(keyword, 1)
                if len(parts) > 1:
                    remaining = parts[1].strip()
                    # Remove common prefixes
                    remaining = re.sub(r'^(this|the|to\s+\w+:?)\s*', '', remaining, flags=re.IGNORECASE)
                    if len(remaining) > 10:
                        return remaining
        
        return ""
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the translation agent."""
        return {
            "agent_type": self.agent_type,
            "name": "TranslationAgent",
            "description": "Specialized in language translation and localization using dedicated tools",
            "capabilities": [
                "Text translation between 35+ languages",
                "Document translation with formatting preservation",
                "Content localization for different cultures",
                "Multilingual content creation",
                "Language detection and identification",
                "Cultural adaptation and context awareness"
            ],
            "tools_used": [
                "translate_text",
                "localize_content", 
                "translate_document",
                "create_multilingual_content",
                "detect_language"
            ],
            "supported_languages": list(self.supported_languages.keys()),
            "language_count": len(self.supported_languages),
            "optimal_for": [
                "Business document translation",
                "Website and marketing localization",
                "Technical documentation translation",
                "Multilingual content creation",
                "Cross-cultural communication",
                "Language detection tasks"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY")),
            "framework": "LangChain + Groq + Dedicated Tools"
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with their codes."""
        return self.supported_languages.copy()