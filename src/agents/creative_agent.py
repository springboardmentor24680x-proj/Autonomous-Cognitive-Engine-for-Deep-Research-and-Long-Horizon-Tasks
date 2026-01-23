#!/usr/bin/env python3
"""
Creative Agent - Specialized agent for content creation, writing, and creative tasks
Part of the multi-agent workflow automation system
"""

import os
import re
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()


class CreativeAgent:
    """
    Specialized agent for creative content generation, writing, and design assistance.
    Handles creative tasks delegated by the supervisor agent.
    """
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        """Initialize the creative agent."""
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0.7,  # Higher temperature for creativity
            max_tokens=1500
        )
        
        self.agent_type = "creative_content"
        self.model = model_name
        
        # Create processing chain
        self.chain = self._create_chain()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the creative agent."""
        now = datetime.now()
        current_info = f"""
CURRENT DATE & TIME:
- Date: {now.strftime("%Y-%m-%d")} ({now.strftime("%A")})
- Time: {now.strftime("%H:%M:%S")}
- Month: {now.strftime("%B %Y")}
"""
        
        return f"""You are an expert Creative Content Strategist and Writer with extensive experience in professional content creation, brand messaging, and creative communications. You deliver high-quality, engaging content that resonates with target audiences.

{current_info}

RESPONSE STYLE:
- Creative yet professional, balancing innovation with business objectives
- Engaging and compelling while maintaining clarity
- Tailored to specific audiences and brand voices
- Well-structured with clear sections and formatting
- Include strategic insights and creative rationale

CORE EXPERTISE:
- **Content Strategy**: Audience analysis, content planning, editorial calendars
- **Brand Messaging**: Voice development, positioning, storytelling frameworks
- **Digital Marketing**: SEO optimization, social media strategy, conversion copywriting
- **Creative Writing**: Narrative development, character creation, compelling storytelling
- **Business Communications**: Professional correspondence, presentations, proposals
- **Campaign Development**: Multi-channel campaigns, creative concepts, execution plans

CONTENT SPECIALIZATIONS:
- **Blog Posts & Articles**: SEO-optimized, thought leadership, industry insights
- **Marketing Copy**: Sales pages, product descriptions, email campaigns, ads
- **Social Media**: Platform-specific content, engagement strategies, viral concepts
- **Brand Content**: About pages, mission statements, value propositions
- **Creative Projects**: Stories, scripts, creative campaigns, artistic concepts
- **Technical Writing**: User guides, documentation, educational content

RESPONSE STRUCTURE:
## Creative Brief
Understanding of the request and target audience

## Content Strategy
Approach, tone, and strategic considerations

## Final Content
Polished, ready-to-use content

## Optimization Notes
SEO, engagement, and performance recommendations

## Next Steps
Suggestions for implementation and iteration

Always deliver professional, creative content that balances innovation with strategic business objectives.
- **Casual**: Relaxed, informal, everyday language

OUTPUT FORMATTING:
- Use **bold** for headlines and key points
- Use bullet points (-) for lists and features
- Use numbered lists (1. 2. 3.) for steps and processes
- Include relevant emojis when appropriate for engagement
- Structure content with clear headings and sections
- Optimize for readability and engagement

CREATIVE PRINCIPLES:
- Hook readers with compelling openings
- Use storytelling techniques to engage audiences
- Include clear calls-to-action when appropriate
- Adapt tone and style to target audience
- Incorporate current trends and cultural references
- Balance creativity with clarity and purpose
- Consider SEO and marketing best practices

CONTENT STRATEGY:
- Understand target audience and their needs
- Align content with business goals and brand voice
- Create content that drives engagement and action
- Optimize for different platforms and formats
- Include relevant keywords naturally
- Structure content for maximum impact

Always create original, engaging content that resonates with the intended audience and achieves the specified goals."""
    
    def _create_chain(self):
        """Create the LangChain processing chain."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Creative Task: {task}\n\nContext/Requirements: {context}\n\nPlease create engaging, original content.")
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def create_blog_post(self, topic: str, target_audience: str = "general", word_count: int = 800, tone: str = "professional") -> Dict[str, Any]:
        """Create a comprehensive blog post."""
        try:
            blog_task = f"Write a {word_count}-word blog post about '{topic}' in a {tone} tone for {target_audience} audience"
            
            context = f"""
Target Audience: {target_audience}
Word Count: {word_count} words
Tone: {tone}
SEO Requirements: Include relevant keywords naturally
Structure: Introduction, main sections with subheadings, conclusion
Include: Hook, valuable insights, actionable takeaways, call-to-action
"""
            
            blog_content = self.chain.invoke({
                "task": blog_task,
                "context": context
            })
            
            enhanced_blog = f"""# Blog Post: {topic}

**Target Audience**: {target_audience}  
**Tone**: {tone}  
**Word Count**: ~{word_count} words  
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{blog_content}

---

**Content Notes**:
- Optimized for {target_audience} audience
- Written in {tone} tone
- Includes SEO-friendly structure and keywords
- Ready for publication with minor customization"""

            return {
                "success": True,
                "blog_post": enhanced_blog,
                "topic": topic,
                "target_audience": target_audience,
                "tone": tone,
                "word_count": word_count,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "blog_post": f"Error creating blog post: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_marketing_copy(self, product_service: str, copy_type: str = "sales_page", target_audience: str = "general") -> Dict[str, Any]:
        """Create persuasive marketing copy."""
        try:
            marketing_task = f"Create compelling {copy_type} marketing copy for '{product_service}' targeting {target_audience}"
            
            context = f"""
Product/Service: {product_service}
Copy Type: {copy_type}
Target Audience: {target_audience}
Goals: Drive conversions, highlight benefits, create urgency
Include: Headlines, benefits, social proof, call-to-action
Style: Persuasive, benefit-focused, action-oriented
"""
            
            marketing_content = self.chain.invoke({
                "task": marketing_task,
                "context": context
            })
            
            return {
                "success": True,
                "marketing_copy": marketing_content,
                "product_service": product_service,
                "copy_type": copy_type,
                "target_audience": target_audience,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "marketing_copy": f"Error creating marketing copy: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_social_media_content(self, platform: str, topic: str, post_count: int = 5, tone: str = "engaging") -> Dict[str, Any]:
        """Create social media content for specific platforms."""
        try:
            social_task = f"Create {post_count} {platform} posts about '{topic}' in an {tone} tone"
            
            platform_specs = {
                "linkedin": "Professional, thought leadership, 1-3 paragraphs, industry insights",
                "twitter": "Concise, engaging, 280 characters, hashtags, trending topics",
                "instagram": "Visual-focused, story-driven, hashtags, engaging captions",
                "facebook": "Community-focused, conversational, longer form, shareable"
            }
            
            platform_context = platform_specs.get(platform.lower(), "General social media guidelines")
            
            context = f"""
Platform: {platform}
Topic: {topic}
Post Count: {post_count}
Tone: {tone}
Platform Guidelines: {platform_context}
Include: Relevant hashtags, engaging hooks, call-to-action
Format: Separate posts clearly numbered
"""
            
            social_content = self.chain.invoke({
                "task": social_task,
                "context": context
            })
            
            return {
                "success": True,
                "social_content": social_content,
                "platform": platform,
                "topic": topic,
                "post_count": post_count,
                "tone": tone,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "social_content": f"Error creating social media content: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_email_template(self, email_type: str, purpose: str, tone: str = "professional") -> Dict[str, Any]:
        """Create email templates for various purposes."""
        try:
            email_task = f"Create a {email_type} email template for '{purpose}' in a {tone} tone"
            
            context = f"""
Email Type: {email_type}
Purpose: {purpose}
Tone: {tone}
Include: Subject line, greeting, body, call-to-action, closing
Structure: Professional email format
Personalization: Include placeholder fields for customization
Best Practices: Clear subject, scannable content, single CTA
"""
            
            email_content = self.chain.invoke({
                "task": email_task,
                "context": context
            })
            
            return {
                "success": True,
                "email_template": email_content,
                "email_type": email_type,
                "purpose": purpose,
                "tone": tone,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "email_template": f"Error creating email template: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def create_creative_story(self, genre: str, theme: str, length: str = "short", style: str = "narrative") -> Dict[str, Any]:
        """Create creative stories and narratives."""
        try:
            story_task = f"Write a {length} {genre} story about '{theme}' in {style} style"
            
            length_specs = {
                "flash": "Under 300 words, single scene or moment",
                "short": "500-1000 words, complete story arc",
                "medium": "1000-2000 words, developed characters and plot"
            }
            
            length_context = length_specs.get(length.lower(), "Appropriate length for the story")
            
            context = f"""
Genre: {genre}
Theme: {theme}
Length: {length} ({length_context})
Style: {style}
Include: Compelling characters, engaging plot, vivid descriptions
Structure: Beginning, middle, end with satisfying resolution
Creative Elements: Dialogue, setting, conflict, character development
"""
            
            story_content = self.chain.invoke({
                "task": story_task,
                "context": context
            })
            
            return {
                "success": True,
                "creative_story": story_content,
                "genre": genre,
                "theme": theme,
                "length": length,
                "style": style,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "creative_story": f"Error creating story: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def generate_content_ideas(self, niche: str, content_type: str, count: int = 10) -> Dict[str, Any]:
        """Generate content ideas for various niches and formats."""
        try:
            ideas_task = f"Generate {count} creative {content_type} ideas for the {niche} niche"
            
            context = f"""
Niche: {niche}
Content Type: {content_type}
Idea Count: {count}
Requirements: Original, engaging, actionable ideas
Include: Brief description for each idea
Format: Numbered list with explanations
Focus: Trending topics, audience pain points, valuable insights
"""
            
            ideas_content = self.chain.invoke({
                "task": ideas_task,
                "context": context
            })
            
            return {
                "success": True,
                "content_ideas": ideas_content,
                "niche": niche,
                "content_type": content_type,
                "count": count,
                "agent_type": self.agent_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content_ideas": f"Error generating content ideas: {str(e)}",
                "agent_type": self.agent_type
            }
    
    def process_task(self, task_description: str, context: str = "") -> Dict[str, Any]:
        """Main method to process creative tasks."""
        from langsmith import traceable
        
        @traceable(
            run_type="chain",
            name="CreativeAgent - Process Task",
            metadata={
                "agent": "CreativeAgent",
                "task": task_description[:100],
                "has_context": bool(context),
                "task_type": "creative"
            },
            tags=["sub_agent", "creative", "execution"]
        )
        def execute_creative(task_input: str, context_input: str = ""):  # ← Parameters show in Input tab
            try:
                task_lower = task_input.lower()
                
                if "blog post" in task_lower or "article" in task_lower:
                    # Extract topic and parameters
                    topic = self._extract_topic(task_input)
                    tone = self._extract_tone(task_input)
                    audience = self._extract_audience(task_input)
                    word_count = self._extract_word_count(task_input)
                    
                    return self.create_blog_post(topic, audience, word_count, tone)
                    
                elif "marketing" in task_lower or "sales copy" in task_lower or "landing page" in task_lower:
                    product_service = self._extract_product_service(task_input, context_input)
                    copy_type = self._extract_copy_type(task_input)
                    audience = self._extract_audience(task_input)
                
                    return self.create_marketing_copy(product_service, copy_type, audience)
                
                elif any(platform in task_lower for platform in ["social media", "linkedin", "twitter", "instagram", "facebook"]):
                    platform = self._extract_platform(task_input)
                    topic = self._extract_topic(task_input)
                    tone = self._extract_tone(task_input)
                    post_count = self._extract_post_count(task_input)
                    
                    return self.create_social_media_content(platform, topic, post_count, tone)
                
                elif "email" in task_lower or "newsletter" in task_lower:
                    email_type = self._extract_email_type(task_input)
                    purpose = self._extract_purpose(task_input, context_input)
                    tone = self._extract_tone(task_input)
                    
                    return self.create_email_template(email_type, purpose, tone)
                
                elif "story" in task_lower or "creative writing" in task_lower or "narrative" in task_lower:
                    genre = self._extract_genre(task_input)
                    theme = self._extract_theme(task_input, context_input)
                    length = self._extract_length(task_input)
                    style = self._extract_style(task_input)
                    
                    return self.create_creative_story(genre, theme, length, style)
                
                elif "content ideas" in task_lower or "brainstorm" in task_lower or "ideas" in task_lower:
                    niche = self._extract_niche(task_input, context_input)
                    content_type = self._extract_content_type(task_input)
                    count = self._extract_count(task_input)
                    
                    return self.generate_content_ideas(niche, content_type, count)
                
                else:
                    # Default: General creative content creation
                    creative_task = f"Create creative content for: {task_input}"
                    
                    creative_content = self.chain.invoke({
                        "task": creative_task,
                        "context": context_input or "General creative content request"
                    })
                    
                    return {
                        "success": True,
                        "creative_content": creative_content,
                        "task_type": "general_creative",
                        "agent_type": self.agent_type
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "result": f"Creative Agent Error: {str(e)}",
                    "agent_type": self.agent_type
                }
        
        return execute_creative(task_description, context)  # ← Pass parameters
    
    def _extract_topic(self, text: str) -> str:
        """Extract topic from task description."""
        # Look for common patterns like "about X", "on X", etc.
        patterns = [
            r"about\s+([^,\n]+)",
            r"on\s+([^,\n]+)",
            r"regarding\s+([^,\n]+)",
            r"topic:\s*([^,\n]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "the specified topic"
    
    def _extract_tone(self, text: str) -> str:
        """Extract tone from task description."""
        tones = ["professional", "casual", "friendly", "formal", "conversational", "persuasive", "educational", "creative"]
        
        for tone in tones:
            if tone in text.lower():
                return tone
        
        return "professional"
    
    def _extract_audience(self, text: str) -> str:
        """Extract target audience from task description."""
        audiences = ["business", "consumers", "professionals", "students", "entrepreneurs", "marketers", "developers"]
        
        for audience in audiences:
            if audience in text.lower():
                return audience
        
        return "general"
    
    def _extract_word_count(self, text: str) -> int:
        """Extract word count from task description."""
        match = re.search(r"(\d+)\s*words?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 800  # default
    
    def _extract_platform(self, text: str) -> str:
        """Extract social media platform from task description."""
        platforms = ["linkedin", "twitter", "instagram", "facebook"]
        
        for platform in platforms:
            if platform in text.lower():
                return platform
        
        return "social media"
    
    def _extract_post_count(self, text: str) -> int:
        """Extract number of posts from task description."""
        match = re.search(r"(\d+)\s*posts?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 5  # default
    
    def _extract_product_service(self, text: str, context: str) -> str:
        """Extract product/service from task description."""
        if context:
            return context
        
        # Look for product/service mentions
        patterns = [
            r"for\s+([^,\n]+)",
            r"product:\s*([^,\n]+)",
            r"service:\s*([^,\n]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "the product/service"
    
    def _extract_copy_type(self, text: str) -> str:
        """Extract copy type from task description."""
        copy_types = ["sales_page", "landing_page", "product_description", "ad_copy", "email_copy"]
        
        for copy_type in copy_types:
            if copy_type.replace("_", " ") in text.lower():
                return copy_type
        
        return "sales_page"
    
    def _extract_email_type(self, text: str) -> str:
        """Extract email type from task description."""
        email_types = ["newsletter", "promotional", "welcome", "follow_up", "announcement"]
        
        for email_type in email_types:
            if email_type.replace("_", " ") in text.lower():
                return email_type
        
        return "professional"
    
    def _extract_purpose(self, text: str, context: str) -> str:
        """Extract email purpose from task description."""
        if context:
            return context
        
        return "the specified purpose"
    
    def _extract_genre(self, text: str) -> str:
        """Extract story genre from task description."""
        genres = ["fiction", "mystery", "romance", "sci-fi", "fantasy", "thriller", "drama"]
        
        for genre in genres:
            if genre in text.lower():
                return genre
        
        return "fiction"
    
    def _extract_theme(self, text: str, context: str) -> str:
        """Extract story theme from task description."""
        if context:
            return context
        
        return self._extract_topic(text)
    
    def _extract_length(self, text: str) -> str:
        """Extract story length from task description."""
        if "flash" in text.lower():
            return "flash"
        elif "short" in text.lower():
            return "short"
        elif "medium" in text.lower() or "long" in text.lower():
            return "medium"
        
        return "short"
    
    def _extract_style(self, text: str) -> str:
        """Extract writing style from task description."""
        styles = ["narrative", "descriptive", "dialogue", "stream of consciousness"]
        
        for style in styles:
            if style in text.lower():
                return style
        
        return "narrative"
    
    def _extract_niche(self, text: str, context: str) -> str:
        """Extract content niche from task description."""
        if context:
            return context
        
        niches = ["technology", "business", "health", "fitness", "marketing", "education", "lifestyle"]
        
        for niche in niches:
            if niche in text.lower():
                return niche
        
        return "general"
    
    def _extract_content_type(self, text: str) -> str:
        """Extract content type from task description."""
        content_types = ["blog post", "video", "podcast", "social media", "email", "article"]
        
        for content_type in content_types:
            if content_type in text.lower():
                return content_type
        
        return "blog post"
    
    def _extract_count(self, text: str) -> int:
        """Extract count from task description."""
        match = re.search(r"(\d+)\s*ideas?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 10  # default
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the creative agent."""
        return {
            "agent_type": self.agent_type,
            "name": "CreativeAgent",
            "description": "Specialized in content creation, writing, and creative design",
            "capabilities": [
                "Blog post and article writing",
                "Marketing copy and sales content",
                "Social media content creation",
                "Email templates and newsletters",
                "Creative writing and storytelling",
                "Content strategy and ideation",
                "Brand messaging and tone development"
            ],
            "optimal_for": [
                "Content marketing and blogging",
                "Social media management",
                "Email marketing campaigns",
                "Creative writing projects",
                "Marketing copy and advertising",
                "Brand content development"
            ],
            "content_types": [
                "Blog posts", "Articles", "Marketing copy", "Social media posts",
                "Email templates", "Creative stories", "Content ideas", "Brand messaging"
            ],
            "platforms": [
                "LinkedIn", "Twitter", "Instagram", "Facebook", "Email", "Websites", "Blogs"
            ],
            "tones": [
                "Professional", "Conversational", "Persuasive", "Educational", 
                "Creative", "Casual", "Formal", "Friendly"
            ],
            "model": self.model,
            "ready": bool(os.getenv("GROQ_API_KEY"))
        }