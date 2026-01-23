#!/usr/bin/env python3
"""
Main entry point for the restructured Autonomous Cognitive Engine
Multi-agent workflow automation system with proper folder structure
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.supervisor_agent import SupervisorAgent

load_dotenv()

def main():
    """Main interactive loop for the cognitive engine."""
    print("Autonomous Cognitive Engine - Restructured")
    print("=" * 50)
    print("Multi-agent workflow automation system")
    print("Type 'quit' to exit, 'help' for commands")
    print()
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("GROQ_API_KEY not found in environment variables")
        print("Please add your Groq API key to the .env file")
        return
    
    # Initialize the system
    try:
        print("Initializing supervisor agent...")
        supervisor = SupervisorAgent()
        
        print("System ready!")
        print(f"Available capabilities:")
        print(f"   - Natural conversation with context")
        print(f"   - Context-aware responses")
        print(f"   - Virtual file system for memory")
        print(f"   - Adaptive formatting for different tasks")
        print()
        
    except Exception as e:
        print(f"Initialization failed: {e}")
        return
    
    # Interactive loop with conversation context
    conversation_history = []
    
    while True:
        try:
            user_input = input("Enter your request: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() in ['help', 'h']:
                print_help()
                continue
            
            if user_input.lower() == 'status':
                print_status(supervisor)
                continue
            
            # Add to conversation history
            conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep history manageable (last 20 messages)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            print("Processing with supervisor agent...")
            result = supervisor.run_with_context(user_input, conversation_history)
            
            # Add response to history
            if result["success"]:
                conversation_history.append({
                    'role': 'assistant',
                    'content': result["final_response"],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Display results
            print("\n" + "="*60)
            if result["success"]:
                print("Task completed successfully!")
                print(f"Tools used: {result.get('tools_used', 0)}")
                if result.get('execution_plan'):
                    print(f"Plan: {result['execution_plan']}")
                print("\nResponse:")
                print(result["final_response"])
            else:
                print("Task failed:")
                print(result.get("error", "Unknown error"))
            
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def print_help():
    """Print help information."""
    print("\nAvailable Commands:")
    print("  help, h     - Show this help message")
    print("  status      - Show system status")
    print("  quit, exit  - Exit the program")
    print("\nExample requests:")
    print("  'What are good study tips?'")
    print("  'Plan a budget for $3000 monthly income'")
    print("  'Create a weekend trip itinerary for Paris'")
    print("  'Explain machine learning in simple terms'")
    print("\n💬 Conversation Context:")
    print("  The agent remembers your conversation and can handle follow-up questions!")
    print()

def print_status(supervisor):
    """Print system status."""
    print("\nSystem Status:")
    status = supervisor.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Check VFS status
    try:
        from memory.vfs import get_vfs
        vfs = get_vfs()
        vfs_stats = vfs.get_stats()
        print(f"\n📁 Virtual File System:")
        print(f"  Files: {vfs_stats['stats']['total_files']}")
        print(f"  Total size: {vfs_stats['stats']['total_size']} characters")
    except Exception as e:
        print(f"  VFS Status: Error - {e}")
    
    print()

if __name__ == "__main__":
    main()