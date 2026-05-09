#!/usr/bin/env python3
"""
Web UI for Restructured Autonomous Cognitive Engine
Clean, modern interface using the new folder structure
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.supervisor_agent import SupervisorAgent
from graph.state_graph import MultiAgentWorkflow
from tools.read_file import vfs_ls, vfs_read_file
from memory.vfs import get_current_agent_state

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global agent instances - no persistent conversation history
agent = SupervisorAgent()
langgraph_workflow = MultiAgentWorkflow()
# Remove persistent conversation_history dictionary - each session will be fresh

# Configuration for workflow selection
USE_LANGGRAPH = os.getenv('USE_LANGGRAPH', 'true').lower() == 'true'

print(f"\n{'='*70}")
print(f"FLASK APP CONFIGURATION")
print(f"{'='*70}")
print(f"USE_LANGGRAPH: {USE_LANGGRAPH}")
print(f"Environment value: {os.getenv('USE_LANGGRAPH')}")
print(f"Workflow: {'LangGraph TODO' if USE_LANGGRAPH else 'Traditional Supervisor'}")
print(f"{'='*70}\n")

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index_enhanced.html')

@app.route('/api/test')
def test_endpoint():
    """Test endpoint to verify app is running."""
    return jsonify({
        'status': 'ok',
        'message': 'App is running',
        'use_langgraph': USE_LANGGRAPH,
        'agent_ready': True
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads for analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        # Basic validation
        if len(content) > 1024 * 1024:  # 1MB limit
            return jsonify({'error': 'File too large'}), 400
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'content': content,
            'size': len(content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with fresh session context."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        use_langgraph = data.get('use_langgraph', USE_LANGGRAPH)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Generate fresh session ID for each request
        session_id = str(uuid.uuid4())
        
        # Start with empty conversation history for fresh session
        conversation_context = []
        
        # Run with LangGraph or traditional agent based on configuration
        if use_langgraph:
            print(f"[/api/chat] → Using LangGraph TODO workflow")  # Debug
            result = langgraph_workflow.run(
                message, 
                conversation_context,
                session_id
            )
        else:
            print(f"[/api/chat] → Using traditional supervisor workflow")  # Debug
            result = agent.run_with_context(message, conversation_context, session_id)
        
        # Format response
        response = {
            'success': result['success'],
            'message': result['final_response'],
            'tools_used': result.get('tools_used', 0),
            'session_id': session_id,
            'workflow': result.get('workflow', 'traditional'),
            'delegated_to': result.get('delegated_to'),
            'timestamp': datetime.now().isoformat(),
            'todos_created': result.get('todos_created', 0),
            'todos_completed': result.get('todos_completed', 0),
            'todo_breakdown': result.get('todo_breakdown', []),
            'todos_file': result.get('todos_file'),
            'synthesis_file': result.get('synthesis_file')
        }
        
        if not result['success']:
            response['error'] = result.get('error', 'Unknown error')
        
        return jsonify(response)
        
    except Exception as e:
        import traceback
        print(f"Chat error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vfs/files')
def list_vfs_files():
    """List files in virtual file system."""
    try:
        result = vfs_ls.invoke({"path": "/"})
        if result.get('success'):
            return jsonify({
                'files': result['files'],
                'count': result['count']
            })
        else:
            return jsonify({'error': result.get('error')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vfs/file/<filename>')
def get_vfs_file(filename):
    """Get content of a VFS file."""
    try:
        result = vfs_read_file.invoke({"filename": filename})
        if result.get('success'):
            return jsonify({
                'filename': filename,
                'content': result['content'],
                'size': result['size']
            })
        else:
            return jsonify({'error': result.get('error')}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos')
def get_todos():
    """Get current TODO list."""
    try:
        state = get_current_agent_state()
        todos = state.get('todos', [])
        
        # Handle both dict and TodoItem objects
        formatted_todos = []
        for todo in todos:
            if hasattr(todo, '__dict__'):
                # TodoItem object
                formatted_todos.append({
                    'id': getattr(todo, 'id', 'unknown'),
                    'task': getattr(todo, 'task', 'No task'),
                    'status': getattr(todo, 'status', 'pending'),
                    'created_at': getattr(todo, 'created_at', 'unknown')
                })
            elif isinstance(todo, dict):
                # Dictionary
                formatted_todos.append({
                    'id': todo.get('id', 'unknown'),
                    'task': todo.get('task', 'No task'),
                    'status': todo.get('status', 'pending'),
                    'created_at': todo.get('created_at', 'unknown')
                })
        
        return jsonify({
            'todos': formatted_todos,
            'count': len(formatted_todos)
        })
    except Exception as e:
        # Return empty list instead of error to keep UI working
        return jsonify({
            'todos': [],
            'count': 0,
            'error': str(e)
        })

@app.route('/api/sub-agents')
def get_sub_agents():
    """Get available sub-agents."""
    try:
        # Return all available sub-agents from the enhanced system
        agents = [
            {
                "name": "Strategic Planning Agent",
                "type": "planning",
                "description": "Enterprise strategy and project management specialist", 
                "capabilities": ["Strategic Planning", "Project Management", "Resource Allocation", "Risk Assessment", "Timeline Development", "Business Strategy"]
            },
            {
                "name": "Software Engineering Agent",
                "type": "programming", 
                "description": "Full-stack development and software architecture specialist",
                "capabilities": ["Code Generation", "System Architecture", "Performance Optimization", "Security Analysis", "Code Review", "Technical Documentation"]
            },
            {
                "name": "Content Strategy Agent",
                "type": "creative_content",
                "description": "Professional content creation and marketing communications specialist",
                "capabilities": ["Content Strategy", "Brand Messaging", "Marketing Copy", "Technical Writing", "Social Media Strategy", "Editorial Services"]
            },
            {
                "name": "Research Intelligence Agent",
                "type": "research",
                "description": "Market research and competitive intelligence specialist",
                "capabilities": ["Market Analysis", "Competitive Intelligence", "Industry Research", "Trend Analysis", "Due Diligence", "Information Synthesis"]
            },
            {
                "name": "Document Processing Agent",
                "type": "summarization",
                "description": "Document analysis and information extraction specialist",
                "capabilities": ["Document Summarization", "Content Analysis", "Information Extraction", "Report Generation", "Knowledge Synthesis", "Executive Briefings"]
            },
            {
                "name": "Translation & Localization Agent",
                "type": "translation",
                "description": "Multilingual translation and cultural localization specialist",
                "capabilities": ["Language Translation", "Content Localization", "Cultural Adaptation", "Multilingual Content", "Translation Quality", "Cross-Cultural Communication"]
            }
        ]
        
        return jsonify({
            'agents': agents,
            'count': len(agents)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Conversation Memory API Endpoints
@app.route('/api/conversation/history/<session_id>')
def get_conversation_history(session_id):
    """Get conversation history for a session."""
    try:
        context = agent.conversation_memory.get_conversation_context(session_id, max_messages=50)
        return jsonify({
            'session_id': session_id,
            'messages': context,
            'count': len(context)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/summary/<session_id>')
def get_conversation_summary(session_id):
    """Get conversation summary for a session."""
    try:
        summary = agent.get_conversation_summary(session_id)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/insights/<session_id>')
def get_conversation_insights(session_id):
    """Get conversation insights for a session."""
    try:
        insights = agent.get_conversation_insights(session_id)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/search', methods=['POST'])
def search_conversations():
    """Search through conversation history."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id')  # Optional
        
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        results = agent.search_conversation_history(query, session_id)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/preferences/<session_id>', methods=['POST'])
def update_user_preferences(session_id):
    """Update user preferences for a session."""
    try:
        data = request.get_json()
        preferences = data.get('preferences', {})
        
        success = agent.update_user_preferences(session_id, preferences)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update preferences'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/sessions')
def list_conversation_sessions():
    """List all active conversation sessions (empty for fresh sessions)."""
    try:
        # Return empty list since we don't persist sessions
        return jsonify({
            'sessions': [],
            'count': 0,
            'message': 'Fresh sessions - no persistent conversation history'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/clear-all', methods=['POST'])
def clear_all_conversations():
    """Clear all conversation history (no-op for fresh sessions)."""
    try:
        return jsonify({
            'success': True,
            'message': 'Sessions are already fresh - no persistent history to clear'
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/rename/<session_id>', methods=['POST'])
def rename_conversation(session_id):
    """Rename a conversation."""
    try:
        data = request.get_json()
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        
        # Update conversation title
        success = agent.conversation_memory.update_conversation_title(session_id, new_title)
        
        if success:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'title': new_title
            })
        else:
            return jsonify({'error': 'Conversation not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation/delete/<session_id>', methods=['DELETE'])
def delete_conversation(session_id):
    """Delete a conversation."""
    try:
        # Don't delete the current active session
        if session_id == getattr(agent.conversation_memory, 'current_session_id', None):
            return jsonify({'error': 'Cannot delete active conversation'}), 400
        
        # Delete conversation
        success = agent.conversation_memory.delete_conversation(session_id)
        
        if success:
            return jsonify({
                'success': True,
                'session_id': session_id
            })
        else:
            return jsonify({'error': 'Conversation not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to Autonomous Cognitive Engine'})

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages with fresh session context."""
    try:
        print(f"Received chat message: {data}")  # Debug log
        message = data.get('message', '').strip()
        if not message:
            emit('error', {'message': 'Message cannot be empty'})
            return
        
        # Generate fresh session ID for each message
        session_id = str(uuid.uuid4())
        
        # Start with empty conversation context for fresh session
        conversation_context = []
        
        print(f"Processing message: {message[:50]}... (Fresh Session: {session_id[:12]}...)")  # Debug log
        print(f"USE_LANGGRAPH = {USE_LANGGRAPH}")  # Debug: Check workflow selection
        
        # Emit thinking status
        emit('thinking', {'message': 'Agent is processing your request...'})
        
        # Run agent with fresh session context
        # Choose workflow based on configuration
        if USE_LANGGRAPH:
            print(f"→ Using LangGraph TODO workflow")  # Debug
            result = langgraph_workflow.run(message, conversation_context, session_id)
        else:
            print(f"→ Using traditional supervisor workflow")  # Debug
            result = agent.run_with_context(message, conversation_context, session_id)
        
        print(f"Agent result: success={result['success']}, tools={result.get('tools_used', 0)}, workflow={result.get('workflow', 'unknown')}")  # Debug log
        
        # Emit enhanced response with fresh session metadata
        response = {
            'success': result['success'],
            'message': result['final_response'],
            'tools_used': result.get('tools_used', 0),
            'timestamp': datetime.now().isoformat(),
            'session_id': result.get('session_id'),
            'conversation_context': 0,  # Always 0 for fresh sessions
            'delegated_to': result.get('delegated_to'),
            'workflow': result.get('workflow', 'traditional'),
            'todos_created': result.get('todos_created', 0),
            'todos_completed': result.get('todos_completed', 0),
            'todo_breakdown': result.get('todo_breakdown', []),
            'todos_file': result.get('todos_file'),
            'synthesis_file': result.get('synthesis_file')
        }
        
        if result['success']:
            emit('response', response)
        else:
            emit('error', {'message': result.get('error', 'Unknown error')})
            
    except Exception as e:
        print(f"Chat error: {e}")  # Debug log
        emit('error', {'message': str(e)})

@app.route('/api/workflow/status')
def workflow_status():
    """Get current workflow configuration."""
    return jsonify({
        'use_langgraph': USE_LANGGRAPH,
        'available_workflows': ['traditional', 'langgraph'],
        'current_workflow': 'langgraph' if USE_LANGGRAPH else 'traditional'
    })

@app.route('/api/workflow/toggle', methods=['POST'])
def toggle_workflow():
    """Toggle between LangGraph and traditional workflow."""
    global USE_LANGGRAPH
    data = request.get_json()
    use_langgraph = data.get('use_langgraph', not USE_LANGGRAPH)
    USE_LANGGRAPH = use_langgraph
    
    return jsonify({
        'success': True,
        'use_langgraph': USE_LANGGRAPH,
        'current_workflow': 'langgraph' if USE_LANGGRAPH else 'traditional',
        'message': f'Switched to {("LangGraph" if USE_LANGGRAPH else "Traditional")} workflow'
    })

if __name__ == '__main__':
    print("Starting Autonomous Cognitive Engine Web UI")
    print("=" * 50)
    print(f"URL: http://localhost:5000")
    print(f"Agent: Supervisor with specialized sub-agents")
    print(f"LangSmith: {'Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'Disabled'}")
    print(f"Architecture: Multi-agent workflow automation")
    
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)