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
from tools.read_file import vfs_ls, vfs_read_file
from memory.vfs import get_current_agent_state

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global agent instance and conversation history
agent = SupervisorAgent()
conversation_history = {}  # Store conversation history per session

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with conversation history."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        
        # Initialize conversation history for this session
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add current message to history
        conversation_history[session_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 messages to avoid context overflow
        if len(conversation_history[session_id]) > 20:  # 10 user + 10 assistant
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        # Run agent with conversation context
        result = agent.run_with_context(message, conversation_history[session_id])
        
        # Add assistant response to history
        if result['success']:
            conversation_history[session_id].append({
                'role': 'assistant',
                'content': result['final_response'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Format response
        response = {
            'success': result['success'],
            'message': result['final_response'],
            'tools_used': result.get('tools_used', 0),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        if not result['success']:
            response['error'] = result.get('error', 'Unknown error')
        
        return jsonify(response)
        
    except Exception as e:
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
        # Return the available sub-agents from the restructured system
        agents = [
            {
                "name": "SummarizerAgent",
                "type": "summarization",
                "description": "Specialized in text summarization and content analysis",
                "capabilities": ["Text summarization", "Key point extraction", "Document analysis"]
            },
            {
                "name": "SearchAgent", 
                "type": "web_search",
                "description": "Specialized in web research and information gathering",
                "capabilities": ["Web research", "Fact checking", "Trend analysis"]
            }
        ]
        
        return jsonify({
            'agents': agents,
            'count': len(agents)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to Autonomous Cognitive Engine'})

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages with conversation history."""
    try:
        print(f"📨 Received chat message: {data}")  # Debug log
        message = data.get('message', '').strip()
        if not message:
            emit('error', {'message': 'Message cannot be empty'})
            return
        
        # Use request session ID or create one
        session_id = request.sid  # WebSocket session ID
        
        # Initialize conversation history for this session
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        # Add current message to history
        conversation_history[session_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 20 messages
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        print(f"🤖 Processing message: {message[:50]}...")  # Debug log
        
        # Emit thinking status
        emit('thinking', {'message': 'Agent is processing your request...'})
        
        # Run agent with context
        result = agent.run_with_context(message, conversation_history[session_id])
        print(f"✅ Agent result: success={result['success']}, tools={result.get('tools_used', 0)}")  # Debug log
        
        # Add assistant response to history
        if result['success']:
            conversation_history[session_id].append({
                'role': 'assistant',
                'content': result['final_response'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Emit response
        response = {
            'success': result['success'],
            'message': result['final_response'],
            'tools_used': result.get('tools_used', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        if result['success']:
            emit('response', response)
        else:
            emit('error', {'message': result.get('error', 'Unknown error')})
            
    except Exception as e:
        print(f"❌ Chat error: {e}")  # Debug log
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Autonomous Cognitive Engine Web UI")
    print("=" * 50)
    print(f"🌐 URL: http://localhost:8080")
    print(f"🤖 Agent: Supervisor with specialized sub-agents")
    print(f"📊 LangSmith: {'Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'Disabled'}")
    print(f"🏗️ Architecture: Multi-agent workflow automation")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)