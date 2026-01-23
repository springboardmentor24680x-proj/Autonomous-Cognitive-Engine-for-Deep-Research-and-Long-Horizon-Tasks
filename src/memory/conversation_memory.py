#!/usr/bin/env python3
"""
Conversation Memory System - Tracks and manages conversation history
Provides context-aware responses and conversation continuity
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import uuid


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    session_id: str
    agent_used: Optional[str] = None
    tools_used: int = 0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationSession:
    """Represents a complete conversation session."""
    session_id: str
    created_at: str
    last_updated: str
    messages: List[ConversationMessage]
    user_preferences: Dict[str, Any]
    context_summary: str
    conversation_title: str  # New field for conversation name
    total_messages: int
    active: bool = True


class ConversationMemory:
    """
    Manages conversation history and context across sessions.
    Provides intelligent context retrieval and conversation continuity.
    """
    
    def __init__(self, storage_path: str = "data/conversations", auto_load: bool = False):
        """Initialize conversation memory system."""
        self.storage_path = storage_path
        self.current_sessions = {}  # In-memory active sessions
        self.max_context_messages = 20  # Maximum messages to keep in context
        self.session_timeout_hours = 24  # Hours before session expires
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load active sessions only if auto_load is True (disabled by default for fresh sessions)
        if auto_load:
            self._load_active_sessions()
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new conversation session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = ConversationSession(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            messages=[],
            user_preferences={},
            context_summary="",
            conversation_title="New Conversation",  # Default title
            total_messages=0,
            active=True
        )
        
        self.current_sessions[session_id] = session
        self._save_session(session)
        
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, 
                   agent_used: str = None, tools_used: int = 0, 
                   metadata: Dict[str, Any] = None) -> str:
        """Add a message to a conversation session."""
        if session_id not in self.current_sessions:
            self.create_session(session_id)
        
        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            id=message_id,
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
            agent_used=agent_used,
            tools_used=tools_used,
            metadata=metadata or {}
        )
        
        session = self.current_sessions[session_id]
        session.messages.append(message)
        session.last_updated = datetime.now().isoformat()
        session.total_messages += 1
        
        # Generate conversation title after first user message
        if role == 'user' and len(session.messages) == 1:
            session.conversation_title = self._generate_conversation_title(content)
        
        # Update context summary and title periodically
        if len(session.messages) % 5 == 0:
            self._update_context_summary(session_id)
            # Update title if it's still the default
            if session.conversation_title == "New Conversation":
                session.conversation_title = self._generate_conversation_title_from_messages(session.messages)
        
        # Save session
        self._save_session(session)
        
        return message_id
    
    def get_conversation_context(self, session_id: str, max_messages: int = None) -> List[Dict[str, Any]]:
        """Get recent conversation context for a session."""
        if session_id not in self.current_sessions:
            return []
        
        session = self.current_sessions[session_id]
        max_msgs = max_messages or self.max_context_messages
        
        # Get recent messages
        recent_messages = session.messages[-max_msgs:] if len(session.messages) > max_msgs else session.messages
        
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp,
                'agent_used': msg.agent_used,
                'tools_used': msg.tools_used
            }
            for msg in recent_messages
        ]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the conversation session."""
        if session_id not in self.current_sessions:
            return {}
        
        session = self.current_sessions[session_id]
        
        # Analyze conversation patterns
        user_messages = [msg for msg in session.messages if msg.role == 'user']
        assistant_messages = [msg for msg in session.messages if msg.role == 'assistant']
        
        agents_used = {}
        total_tools = 0
        
        for msg in assistant_messages:
            if msg.agent_used:
                agents_used[msg.agent_used] = agents_used.get(msg.agent_used, 0) + 1
            total_tools += msg.tools_used
        
        return {
            'session_id': session_id,
            'created_at': session.created_at,
            'last_updated': session.last_updated,
            'total_messages': session.total_messages,
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'agents_used': agents_used,
            'total_tools_used': total_tools,
            'context_summary': session.context_summary,
            'conversation_title': session.conversation_title,  # Include conversation title
            'user_preferences': session.user_preferences,
            'active': session.active
        }
    
    def update_user_preferences(self, session_id: str, preferences: Dict[str, Any]):
        """Update user preferences for a session."""
        if session_id not in self.current_sessions:
            self.create_session(session_id)
        
        session = self.current_sessions[session_id]
        session.user_preferences.update(preferences)
        session.last_updated = datetime.now().isoformat()
        
        self._save_session(session)
    
    def update_conversation_title(self, session_id: str, new_title: str) -> bool:
        """Update the conversation title for a session."""
        if session_id not in self.current_sessions:
            # Try to load the session if it exists
            session_data = self._load_session_data(session_id)
            if session_data:
                session = self._dict_to_session(session_data)
                self.current_sessions[session_id] = session
            else:
                return False
        
        session = self.current_sessions[session_id]
        session.conversation_title = new_title.strip()
        session.last_updated = datetime.now().isoformat()
        
        self._save_session(session)
        return True
    
    def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation session."""
        try:
            # Remove from memory
            if session_id in self.current_sessions:
                del self.current_sessions[session_id]
            
            # Delete the file
            filename = f"session_{session_id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def search_conversations(self, query: str, session_id: str = None) -> List[Dict[str, Any]]:
        """Search through conversation history."""
        results = []
        
        sessions_to_search = [self.current_sessions[session_id]] if session_id else self.current_sessions.values()
        
        for session in sessions_to_search:
            for message in session.messages:
                if query.lower() in message.content.lower():
                    results.append({
                        'session_id': session.session_id,
                        'message_id': message.id,
                        'role': message.role,
                        'content': message.content[:200] + "..." if len(message.content) > 200 else message.content,
                        'timestamp': message.timestamp,
                        'agent_used': message.agent_used
                    })
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_conversation_insights(self, session_id: str) -> Dict[str, Any]:
        """Get insights about the conversation patterns."""
        if session_id not in self.current_sessions:
            return {}
        
        session = self.current_sessions[session_id]
        messages = session.messages
        
        if not messages:
            return {}
        
        # Analyze conversation patterns
        topics = self._extract_topics(messages)
        sentiment = self._analyze_sentiment(messages)
        interaction_patterns = self._analyze_interaction_patterns(messages)
        
        return {
            'topics': topics,
            'sentiment': sentiment,
            'interaction_patterns': interaction_patterns,
            'session_duration': self._calculate_session_duration(session),
            'most_used_agent': self._get_most_used_agent(messages),
            'conversation_flow': self._analyze_conversation_flow(messages)
        }
    
    def clear_all_sessions(self):
        """Clear all conversation sessions from memory and storage."""
        try:
            # Clear in-memory sessions
            self.current_sessions.clear()
            
            # Delete all session files
            import shutil
            if os.path.exists(self.storage_path):
                shutil.rmtree(self.storage_path)
                os.makedirs(self.storage_path, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"Error clearing all sessions: {e}")
            return False
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Clean up old inactive sessions."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        sessions_to_remove = []
        for session_id, session in self.current_sessions.items():
            last_updated = datetime.fromisoformat(session.last_updated)
            if last_updated < cutoff_date and not session.active:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self._archive_session(session_id)
            del self.current_sessions[session_id]
    
    def _load_active_sessions(self):
        """Load active sessions from storage."""
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json') and filename.startswith('session_'):
                    session_id = filename.replace('session_', '').replace('.json', '')
                    session_data = self._load_session_data(session_id)
                    if session_data and session_data.get('active', True):
                        session = self._dict_to_session(session_data)
                        self.current_sessions[session_id] = session
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def _save_session(self, session: ConversationSession):
        """Save session to storage."""
        try:
            filename = f"session_{session.session_id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            session_dict = asdict(session)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session {session.session_id}: {e}")
    
    def _load_session_data(self, session_id: str) -> Dict[str, Any]:
        """Load session data from storage."""
        try:
            filename = f"session_{session_id}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
        
        return {}
    
    def _dict_to_session(self, session_dict: Dict[str, Any]) -> ConversationSession:
        """Convert dictionary to ConversationSession object."""
        messages = [
            ConversationMessage(**msg_dict) 
            for msg_dict in session_dict.get('messages', [])
        ]
        
        session_dict['messages'] = messages
        
        # Handle backward compatibility for conversation_title
        if 'conversation_title' not in session_dict:
            # Generate title from existing data
            if messages:
                user_messages = [msg for msg in messages if msg.role == 'user']
                if user_messages:
                    session_dict['conversation_title'] = self._generate_conversation_title(user_messages[0].content)
                else:
                    session_dict['conversation_title'] = "New Conversation"
            else:
                session_dict['conversation_title'] = "New Conversation"
        
        return ConversationSession(**session_dict)
    
    def _update_context_summary(self, session_id: str):
        """Update the context summary for a session."""
        session = self.current_sessions[session_id]
        
        # Simple context summary - in a real implementation, you might use an LLM
        recent_messages = session.messages[-10:]  # Last 10 messages
        
        topics = []
        for msg in recent_messages:
            if msg.role == 'user':
                # Extract key topics from user messages
                words = msg.content.lower().split()
                key_words = [w for w in words if len(w) > 4 and w.isalpha()]
                topics.extend(key_words[:3])  # Take first 3 meaningful words
        
        # Create summary
        unique_topics = list(set(topics))[:5]  # Top 5 unique topics
        session.context_summary = f"Recent topics: {', '.join(unique_topics)}" if unique_topics else "General conversation"
    
    def _generate_conversation_title(self, first_message: str) -> str:
        """Generate a conversation title from the first user message."""
        # Clean and truncate the message
        cleaned_message = first_message.strip()
        
        # Remove common question words and make it more title-like
        title_words = []
        words = cleaned_message.split()
        
        # Skip common starting words
        skip_words = {'hi', 'hello', 'hey', 'can', 'could', 'would', 'please', 'i', 'need', 'want', 'help', 'me', 'with'}
        
        for word in words:
            clean_word = word.lower().strip('.,!?')
            if clean_word not in skip_words and len(clean_word) > 2:
                title_words.append(word.strip('.,!?'))
            if len(title_words) >= 4:  # Limit to 4 meaningful words
                break
        
        if not title_words:
            # Fallback: use first few words
            title_words = words[:3]
        
        # Create title
        title = ' '.join(title_words)
        
        # Capitalize first letter and limit length
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
            if len(title) > 50:
                title = title[:47] + "..."
        else:
            title = "New Conversation"
        
        return title
    
    def _generate_conversation_title_from_messages(self, messages: List[ConversationMessage]) -> str:
        """Generate a conversation title from multiple messages."""
        user_messages = [msg for msg in messages if msg.role == 'user']
        
        if not user_messages:
            return "New Conversation"
        
        # Analyze all user messages to find common themes
        all_words = []
        for msg in user_messages[:3]:  # Use first 3 user messages
            words = msg.content.lower().split()
            meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
            all_words.extend(meaningful_words[:2])  # Take 2 words from each message
        
        # Find most common themes
        from collections import Counter
        word_counts = Counter(all_words)
        
        # Get top themes
        top_words = [word for word, count in word_counts.most_common(3)]
        
        if top_words:
            # Create a title from top themes
            title = ' '.join(top_words).title()
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        else:
            # Fallback to first message approach
            return self._generate_conversation_title(user_messages[0].content)
    
    def _extract_topics(self, messages: List[ConversationMessage]) -> List[str]:
        """Extract main topics from conversation."""
        topics = []
        for msg in messages:
            if msg.role == 'user':
                words = msg.content.lower().split()
                key_words = [w for w in words if len(w) > 4 and w.isalpha()]
                topics.extend(key_words[:2])
        
        # Return most common topics
        from collections import Counter
        topic_counts = Counter(topics)
        return [topic for topic, count in topic_counts.most_common(5)]
    
    def _analyze_sentiment(self, messages: List[ConversationMessage]) -> str:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'perfect', 'love', 'like', 'thanks']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'problem', 'issue', 'error']
        
        positive_count = 0
        negative_count = 0
        
        for msg in messages:
            if msg.role == 'user':
                content_lower = msg.content.lower()
                positive_count += sum(1 for word in positive_words if word in content_lower)
                negative_count += sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_interaction_patterns(self, messages: List[ConversationMessage]) -> Dict[str, Any]:
        """Analyze interaction patterns."""
        if not messages:
            return {}
        
        avg_user_length = sum(len(msg.content) for msg in messages if msg.role == 'user') / max(1, len([m for m in messages if m.role == 'user']))
        avg_assistant_length = sum(len(msg.content) for msg in messages if msg.role == 'assistant') / max(1, len([m for m in messages if m.role == 'assistant']))
        
        return {
            'avg_user_message_length': round(avg_user_length),
            'avg_assistant_message_length': round(avg_assistant_length),
            'total_exchanges': len(messages) // 2,
            'conversation_style': 'detailed' if avg_user_length > 100 else 'concise'
        }
    
    def _calculate_session_duration(self, session: ConversationSession) -> str:
        """Calculate session duration."""
        if not session.messages:
            return "0 minutes"
        
        start_time = datetime.fromisoformat(session.created_at)
        end_time = datetime.fromisoformat(session.last_updated)
        duration = end_time - start_time
        
        if duration.total_seconds() < 3600:  # Less than 1 hour
            return f"{int(duration.total_seconds() // 60)} minutes"
        else:
            return f"{duration.total_seconds() / 3600:.1f} hours"
    
    def _get_most_used_agent(self, messages: List[ConversationMessage]) -> str:
        """Get the most frequently used agent."""
        agent_counts = {}
        for msg in messages:
            if msg.agent_used:
                agent_counts[msg.agent_used] = agent_counts.get(msg.agent_used, 0) + 1
        
        if agent_counts:
            return max(agent_counts, key=agent_counts.get)
        return "Direct"
    
    def _analyze_conversation_flow(self, messages: List[ConversationMessage]) -> List[str]:
        """Analyze the flow of conversation topics."""
        flow = []
        current_topic = None
        
        for msg in messages:
            if msg.role == 'user':
                # Simple topic detection based on first few words
                words = msg.content.lower().split()[:3]
                topic = ' '.join(words) if len(words) > 1 else words[0] if words else 'general'
                
                if topic != current_topic:
                    flow.append(topic)
                    current_topic = topic
        
        return flow[-5:]  # Return last 5 topic changes
    
    def _archive_session(self, session_id: str):
        """Archive an old session."""
        try:
            current_file = os.path.join(self.storage_path, f"session_{session_id}.json")
            archive_file = os.path.join(self.storage_path, f"archived_session_{session_id}.json")
            
            if os.path.exists(current_file):
                os.rename(current_file, archive_file)
        except Exception as e:
            print(f"Error archiving session {session_id}: {e}")


# Global conversation memory instance
_conversation_memory = None

def get_conversation_memory() -> ConversationMemory:
    """Get the global conversation memory instance with fresh sessions."""
    global _conversation_memory
    if _conversation_memory is None:
        # Initialize with auto_load=False to start fresh each time
        _conversation_memory = ConversationMemory(auto_load=False)
    return _conversation_memory