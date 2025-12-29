#!/usr/bin/env python3
"""
Debug the "Unknown error" issue with the supervisor agent
"""

import sys
import os
import traceback
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent

def debug_supervisor_error():
    """Debug the supervisor agent error."""
    print("🔍 DEBUGGING SUPERVISOR AGENT ERROR")
    print("=" * 50)
    
    try:
        print("1️⃣ Initializing supervisor agent...")
        supervisor = SupervisorAgent()
        print("   ✅ Supervisor initialized successfully")
        
        print("\n2️⃣ Testing simple request...")
        simple_request = "Hello, how are you?"
        result = supervisor.run_with_context(simple_request, [])
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Response: {result['final_response'][:100]}...")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
        
        print("\n3️⃣ Testing trip planning request...")
        trip_request = "plan a 5 days trip for 2 ppl to ooty"
        
        try:
            result = supervisor.run_with_context(trip_request, [])
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Response: {result['final_response'][:200]}...")
            else:
                print(f"   Error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ Exception during trip planning: {e}")
            print(f"   Exception type: {type(e).__name__}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        print(f"Exception type: {type(e).__name__}")
        traceback.print_exc()

def test_individual_components():
    """Test individual components to isolate the issue."""
    print("\n🧪 TESTING INDIVIDUAL COMPONENTS")
    print("=" * 50)
    
    # Test environment variables
    print("1️⃣ Environment Variables:")
    groq_key = os.getenv("GROQ_API_KEY")
    print(f"   GROQ_API_KEY: {'✅ Set' if groq_key else '❌ Missing'}")
    if groq_key:
        print(f"   Key length: {len(groq_key)} characters")
    
    # Test imports
    print("\n2️⃣ Import Tests:")
    try:
        from langchain_groq import ChatGroq
        print("   ✅ ChatGroq import successful")
    except Exception as e:
        print(f"   ❌ ChatGroq import failed: {e}")
    
    try:
        from langchain_core.prompts import ChatPromptTemplate
        print("   ✅ ChatPromptTemplate import successful")
    except Exception as e:
        print(f"   ❌ ChatPromptTemplate import failed: {e}")
    
    # Test LLM initialization
    print("\n3️⃣ LLM Initialization:")
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            groq_api_key=groq_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1200
        )
        print("   ✅ LLM initialized successfully")
        
        # Test simple LLM call
        response = llm.invoke("Hello, this is a test.")
        print(f"   ✅ LLM response: {response.content[:50]}...")
        
    except Exception as e:
        print(f"   ❌ LLM initialization failed: {e}")
        traceback.print_exc()

def test_delegation_tools():
    """Test delegation tools."""
    print("\n🛠️ TESTING DELEGATION TOOLS")
    print("=" * 50)
    
    try:
        from tools.delegation_tool import analyze_task_for_delegation
        
        test_task = "plan a 5 days trip for 2 ppl to ooty"
        analysis = analyze_task_for_delegation(test_task)
        
        print(f"Task: {test_task}")
        print(f"Recommended Agent: {analysis['recommended_agent']}")
        print(f"Confidence: {analysis['confidence']}")
        print(f"Reasoning: {analysis['reasoning']}")
        
    except Exception as e:
        print(f"❌ Delegation tool test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_supervisor_error()
    test_individual_components()
    test_delegation_tools()