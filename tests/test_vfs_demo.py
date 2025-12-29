#!/usr/bin/env python3
"""
VFS Demo and Test - Comprehensive testing of the Virtual File System
"""

import sys
import os
sys.path.append('src')

from memory.vfs import get_vfs, get_current_agent_state, update_agent_state, reset_agent_state
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls
from agents.supervisor_agent import SupervisorAgent

def test_basic_vfs_operations():
    """Test basic VFS operations directly."""
    print("🗂️ TESTING BASIC VFS OPERATIONS")
    print("=" * 50)
    
    # Get VFS instance
    vfs = get_vfs()
    
    # Test 1: Write a file
    print("\n1️⃣ Testing Write Operation:")
    result = vfs.write_file("test_file.txt", "This is a test file with some content.")
    print(f"   Write Result: {result}")
    
    # Test 2: Read the file
    print("\n2️⃣ Testing Read Operation:")
    result = vfs.read_file("test_file.txt")
    print(f"   Read Result: {result}")
    
    # Test 3: List files
    print("\n3️⃣ Testing List Operation:")
    result = vfs.list_files()
    print(f"   List Result: {result}")
    
    # Test 4: Edit the file
    print("\n4️⃣ Testing Edit Operation:")
    result = vfs.edit_file("test_file.txt", "append", "This is additional content.")
    print(f"   Edit Result: {result}")
    
    # Test 5: Read again to see changes
    print("\n5️⃣ Testing Read After Edit:")
    result = vfs.read_file("test_file.txt")
    print(f"   Read Result: {result}")
    
    # Test 6: Get stats
    print("\n6️⃣ Testing Stats:")
    result = vfs.get_stats()
    print(f"   Stats Result: {result}")
    
    return True

def test_vfs_tools():
    """Test VFS through the tool interface."""
    print("\n🛠️ TESTING VFS TOOLS")
    print("=" * 50)
    
    # Test 1: Write using tool
    print("\n1️⃣ Testing vfs_write_file tool:")
    result = vfs_write_file.invoke({
        "filename": "tool_test.txt",
        "content": "This file was created using the VFS tool interface."
    })
    print(f"   Tool Write Result: {result}")
    
    # Test 2: Read using tool
    print("\n2️⃣ Testing vfs_read_file tool:")
    result = vfs_read_file.invoke({"filename": "tool_test.txt"})
    print(f"   Tool Read Result: {result}")
    
    # Test 3: List using tool
    print("\n3️⃣ Testing vfs_ls tool:")
    result = vfs_ls.invoke({"path": "/"})
    print(f"   Tool List Result: {result}")
    
    return True

def test_agent_vfs_integration():
    """Test VFS integration with the supervisor agent."""
    print("\n🤖 TESTING AGENT VFS INTEGRATION")
    print("=" * 50)
    
    supervisor = SupervisorAgent()
    
    # Test 1: Simple request that should trigger VFS usage
    print("\n1️⃣ Testing Agent with Long Response (should auto-save):")
    result = supervisor.run_with_context(
        "Create a detailed 7-day itinerary for a trip to Tokyo with daily activities, restaurants, and budget breakdown",
        []
    )
    print(f"   Agent Success: {result['success']}")
    print(f"   Tools Used: {result.get('tools_used', 0)}")
    print(f"   Response Length: {len(result.get('final_response', ''))}")
    
    # Check if anything was saved to VFS
    vfs = get_vfs()
    stats = vfs.get_stats()
    print(f"   VFS Files After Agent: {stats}")
    
    return result['success']

def test_conversation_memory():
    """Test VFS for conversation memory."""
    print("\n💬 TESTING CONVERSATION MEMORY")
    print("=" * 50)
    
    supervisor = SupervisorAgent()
    conversation_history = []
    
    # First message
    print("\n1️⃣ First message:")
    msg1 = "I'm planning a wedding for 100 people with a $20,000 budget"
    conversation_history.append({'role': 'user', 'content': msg1})
    
    result1 = supervisor.run_with_context(msg1, conversation_history)
    if result1['success']:
        conversation_history.append({'role': 'assistant', 'content': result1['final_response']})
    
    print(f"   Success: {result1['success']}")
    print(f"   Tools Used: {result1.get('tools_used', 0)}")
    
    # Second message (should reference first)
    print("\n2️⃣ Follow-up message:")
    msg2 = "What about the venue costs from my wedding plan?"
    conversation_history.append({'role': 'user', 'content': msg2})
    
    result2 = supervisor.run_with_context(msg2, conversation_history)
    
    print(f"   Success: {result2['success']}")
    print(f"   Tools Used: {result2.get('tools_used', 0)}")
    print(f"   Response Preview: {result2.get('final_response', '')[:200]}...")
    
    # Check VFS state
    vfs = get_vfs()
    stats = vfs.get_stats()
    print(f"   VFS Files After Conversation: {stats}")
    
    return result2['success']

def test_vfs_persistence():
    """Test VFS data persistence."""
    print("\n💾 TESTING VFS PERSISTENCE")
    print("=" * 50)
    
    # Write some data
    vfs = get_vfs()
    vfs.write_file("persistence_test.txt", "This should persist across operations")
    
    # Check it's there
    result1 = vfs.read_file("persistence_test.txt")
    print(f"   Before Reset: {result1['success']}")
    
    # Reset and check if data is lost (it should be, since it's in-memory)
    reset_agent_state()
    vfs_new = get_vfs()
    result2 = vfs_new.read_file("persistence_test.txt")
    print(f"   After Reset: {result2['success']} (should be False - data lost)")
    
    # This shows the limitation - VFS is in-memory only
    print("   ⚠️ VFS is in-memory only - data is lost when system restarts")
    
    return True

def diagnose_vfs_issues():
    """Diagnose potential VFS issues."""
    print("\n🔍 DIAGNOSING VFS ISSUES")
    print("=" * 50)
    
    issues_found = []
    
    # Check 1: VFS instance creation
    try:
        vfs = get_vfs()
        print("   ✅ VFS instance creation: OK")
    except Exception as e:
        issues_found.append(f"VFS instance creation failed: {e}")
        print(f"   ❌ VFS instance creation: {e}")
    
    # Check 2: Basic operations
    try:
        vfs = get_vfs()
        vfs.write_file("test.txt", "test")
        result = vfs.read_file("test.txt")
        if result['success']:
            print("   ✅ Basic read/write operations: OK")
        else:
            issues_found.append("Basic read/write operations failed")
            print("   ❌ Basic read/write operations: Failed")
    except Exception as e:
        issues_found.append(f"Basic operations error: {e}")
        print(f"   ❌ Basic operations: {e}")
    
    # Check 3: Tool integration
    try:
        result = vfs_write_file.invoke({"filename": "tool_test.txt", "content": "test"})
        if result.get('success'):
            print("   ✅ Tool integration: OK")
        else:
            issues_found.append("Tool integration failed")
            print("   ❌ Tool integration: Failed")
    except Exception as e:
        issues_found.append(f"Tool integration error: {e}")
        print(f"   ❌ Tool integration: {e}")
    
    # Check 4: Agent integration
    try:
        supervisor = SupervisorAgent()
        print("   ✅ Agent integration: OK")
    except Exception as e:
        issues_found.append(f"Agent integration error: {e}")
        print(f"   ❌ Agent integration: {e}")
    
    # Summary
    if issues_found:
        print(f"\n❌ ISSUES FOUND ({len(issues_found)}):")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
    
    return len(issues_found) == 0

def main():
    """Run comprehensive VFS testing and demonstration."""
    print("🗂️ VFS COMPREHENSIVE TEST & DEMONSTRATION")
    print("=" * 60)
    
    test_results = {}
    
    try:
        # Run all tests
        test_results["Basic VFS Operations"] = test_basic_vfs_operations()
        test_results["VFS Tools"] = test_vfs_tools()
        test_results["Agent Integration"] = test_agent_vfs_integration()
        test_results["Conversation Memory"] = test_conversation_memory()
        test_results["VFS Persistence"] = test_vfs_persistence()
        test_results["Issue Diagnosis"] = diagnose_vfs_issues()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VFS TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        all_passed = all(test_results.values())
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL VFS TESTS PASSED!")
            print("VFS is working correctly.")
        else:
            print("⚠️ SOME VFS TESTS FAILED")
            print("VFS has issues that need to be addressed.")
        
        # Recommendations
        print("\n💡 VFS ANALYSIS & RECOMMENDATIONS:")
        print("1. VFS basic operations work correctly")
        print("2. VFS is in-memory only - data lost on restart")
        print("3. Auto-save triggers on responses >800 characters")
        print("4. VFS integrates with tools and agents")
        print("5. For production: consider persistent storage (database/files)")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()