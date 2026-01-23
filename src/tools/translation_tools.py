#!/usr/bin/env python3
"""
Translation Tools - Dedicated tools for language translation and localization
Part of the multi-agent workflow automation system
"""

import os
from typing import Dict, Any, List
from datetime import datetime
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM for translation tools
translation_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.1,  # Low temperature for accurate translations
    max_tokens=2000
)

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    "spanish": "es", "french": "fr", "german": "de", "italian": "it",
    "portuguese": "pt", "russian": "ru", "chinese": "zh", "japanese": "ja",
    "korean": "ko", "arabic": "ar", "hindi": "hi", "dutch": "nl",
    "swedish": "sv", "norwegian": "no", "danish": "da", "finnish": "fi",
    "polish": "pl", "czech": "cs", "hungarian": "hu", "turkish": "tr",
    "greek": "el", "hebrew": "he", "thai": "th", "vietnamese": "vi",
    "indonesian": "id", "malay": "ms", "filipino": "tl", "swahili": "sw",
    "ukrainian": "uk", "romanian": "ro", "bulgarian": "bg", "croatian": "hr",
    "serbian": "sr", "slovak": "sk", "slovenian": "sl", "estonian": "et",
    "latvian": "lv", "lithuanian": "lt"
}


@tool
def translate_text(text: str, target_language: str, source_language: str = "auto") -> Dict[str, Any]:
    """
    Translate text from source language to target language.
    
    Args:
        text: The text to translate
        target_language: Target language (e.g., 'spanish', 'french', 'german')
        source_language: Source language (default: 'auto' for auto-detection)
        
    Returns:
        Dict with translation result, metadata, and success status
    """
    try:
        # Normalize language names
        target_lang = _normalize_language(target_language)
        if not target_lang:
            return {
                "success": False,
                "error": f"Unsupported target language: {target_language}",
                "supported_languages": list(SUPPORTED_LANGUAGES.keys())
            }
        
        # Create translation prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a professional translator with expertise in {target_lang} language and culture.

TRANSLATION GUIDELINES:
- Provide accurate, natural translations that preserve meaning and tone
- Consider cultural context and idiomatic expressions
- Maintain the original formatting and structure
- For formal text, use formal register; for casual text, use casual register
- Include cultural notes if the translation requires explanation

RESPONSE FORMAT:
## Translation
[Provide the clean, professional translation here]

## Cultural Notes
[Any important cultural considerations or alternative translations]

## Confidence Level
[High/Medium/Low based on translation certainty]"""),
            ("human", f"Translate this text to {target_lang}:\n\n{text}")
        ])
        
        # Execute translation
        chain = prompt | translation_llm | StrOutputParser()
        result = chain.invoke({"text": text, "target_lang": target_lang})
        
        return {
            "success": True,
            "translation": result,
            "original_text": text,
            "source_language": source_language,
            "target_language": target_lang,
            "translated_at": datetime.now().isoformat(),
            "tool_used": "translate_text"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "translation": f"Translation error: {str(e)}",
            "tool_used": "translate_text"
        }


@tool
def localize_content(content: str, target_culture: str, content_type: str = "general") -> Dict[str, Any]:
    """
    Localize content for a specific culture and market.
    
    Args:
        content: The content to localize
        target_culture: Target culture/market (e.g., 'german_business', 'japanese_formal')
        content_type: Type of content (e.g., 'marketing', 'technical', 'legal')
        
    Returns:
        Dict with localized content and cultural adaptation notes
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a localization expert specializing in {target_culture} market adaptation.

LOCALIZATION GUIDELINES:
- Adapt content for {target_culture} cultural context
- Consider local business practices, social norms, and communication styles
- Adjust tone, formality level, and messaging approach
- Include market-specific references and examples
- Ensure cultural sensitivity and appropriateness

CONTENT TYPE: {content_type}

RESPONSE FORMAT:
## Localized Content
[Culturally adapted content for {target_culture}]

## Cultural Adaptations Made
[List of specific cultural adjustments and reasoning]

## Market Considerations
[Important cultural insights for this market]"""),
            ("human", f"Localize this {content_type} content for {target_culture}:\n\n{content}")
        ])
        
        chain = prompt | translation_llm | StrOutputParser()
        result = chain.invoke({"content": content, "target_culture": target_culture, "content_type": content_type})
        
        return {
            "success": True,
            "localized_content": result,
            "original_content": content,
            "target_culture": target_culture,
            "content_type": content_type,
            "localized_at": datetime.now().isoformat(),
            "tool_used": "localize_content"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "localized_content": f"Localization error: {str(e)}",
            "tool_used": "localize_content"
        }


@tool
def translate_document(document_content: str, target_language: str, document_type: str = "general") -> Dict[str, Any]:
    """
    Translate an entire document while preserving structure and formatting.
    
    Args:
        document_content: The document content to translate
        target_language: Target language for translation
        document_type: Type of document (e.g., 'legal', 'technical', 'marketing')
        
    Returns:
        Dict with translated document and formatting preservation notes
    """
    try:
        target_lang = _normalize_language(target_language)
        if not target_lang:
            return {
                "success": False,
                "error": f"Unsupported target language: {target_language}",
                "supported_languages": list(SUPPORTED_LANGUAGES.keys())
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a professional document translator specializing in {document_type} documents.

DOCUMENT TRANSLATION GUIDELINES:
- Preserve original formatting, structure, and layout
- Maintain professional terminology appropriate for {document_type} documents
- Keep headers, bullet points, numbering, and sections intact
- Translate content accurately while preserving document flow
- Use appropriate formal register for {document_type} content

RESPONSE FORMAT:
## Translated Document
[Complete translated document with preserved formatting]

## Translation Notes
[Any important terminology choices or formatting considerations]

## Quality Assurance
[Confidence level and any areas requiring review]"""),
            ("human", f"Translate this {document_type} document to {target_lang}:\n\n{document_content}")
        ])
        
        chain = prompt | translation_llm | StrOutputParser()
        result = chain.invoke({"document_content": document_content, "target_lang": target_lang, "document_type": document_type})
        
        return {
            "success": True,
            "translated_document": result,
            "original_document": document_content,
            "target_language": target_lang,
            "document_type": document_type,
            "translated_at": datetime.now().isoformat(),
            "tool_used": "translate_document"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "translated_document": f"Document translation error: {str(e)}",
            "tool_used": "translate_document"
        }


@tool
def create_multilingual_content(base_content: str, target_languages: List[str]) -> Dict[str, Any]:
    """
    Create multilingual versions of content for multiple target languages.
    
    Args:
        base_content: The base content to translate
        target_languages: List of target languages
        
    Returns:
        Dict with translations for each language
    """
    try:
        translations = {}
        errors = []
        
        for language in target_languages:
            result = translate_text.invoke({
                "text": base_content,
                "target_language": language,
                "source_language": "auto"
            })
            
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
            "base_content": base_content,
            "created_at": datetime.now().isoformat(),
            "tool_used": "create_multilingual_content"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "multilingual_content": {},
            "tool_used": "create_multilingual_content"
        }


@tool
def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of the given text.
    
    Args:
        text: Text to analyze for language detection
        
    Returns:
        Dict with detected language and confidence level
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a language detection expert. Analyze the given text and identify its language.

DETECTION GUIDELINES:
- Identify the primary language of the text
- Provide confidence level (High/Medium/Low)
- Note any mixed languages if present
- Consider script, vocabulary, and grammar patterns

RESPONSE FORMAT:
## Detected Language
[Language name in English]

## Language Code
[ISO language code if known]

## Confidence Level
[High/Medium/Low]

## Analysis Notes
[Brief explanation of detection reasoning]"""),
            ("human", f"Detect the language of this text:\n\n{text}")
        ])
        
        chain = prompt | translation_llm | StrOutputParser()
        result = chain.invoke({"text": text})
        
        return {
            "success": True,
            "detection_result": result,
            "analyzed_text": text,
            "detected_at": datetime.now().isoformat(),
            "tool_used": "detect_language"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detection_result": f"Language detection error: {str(e)}",
            "tool_used": "detect_language"
        }


def _normalize_language(language: str) -> str:
    """Normalize language name to standard format."""
    if not language or language == "auto":
        return None
        
    language_lower = language.lower().strip()
    
    # Direct match
    if language_lower in SUPPORTED_LANGUAGES:
        return language_lower
    
    # Check for language codes
    for lang_name, lang_code in SUPPORTED_LANGUAGES.items():
        if language_lower == lang_code:
            return lang_name
    
    # Partial matches
    for lang_name in SUPPORTED_LANGUAGES:
        if language_lower in lang_name or lang_name in language_lower:
            return lang_name
    
    return None


def get_supported_languages() -> Dict[str, str]:
    """Get list of supported languages with their codes."""
    return SUPPORTED_LANGUAGES.copy()