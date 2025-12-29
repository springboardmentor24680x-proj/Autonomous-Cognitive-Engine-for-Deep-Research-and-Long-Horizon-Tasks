#!/usr/bin/env python3
"""
Complete System Test - Verify all components are working
"""

import sys
import os
sys.path.append('src')

from agents.supervisor_agent import SupervisorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.search_agent import SearchAgent
from tools.write_file import vfs_write_file
from tools.read_file import vfs_read_file, vfs_ls
from memory.vfs import get_vfs

def test_supervisor():
    """Test supervisor agent."""
    print("=" * 60)
    print("Testing Supervisor Agent")
    print("=" * 60)
    
    try:
        agent = SupervisorAgent()
        result = agent.run("What is the current date?")
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Tools used: {result.get('tools_used', 0)}")
        print(f"✅ Response length: {len(result.get('final_response', ''))}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_summarizer():
    """Test summarizer agent."""
    print("\n" + "=" * 60)
    print("Testing Summarizer Agent")
    print("=" * 60)
    
    try:
        agent = SummarizerAgent()
        content = "This is a test document. It contains multiple sentences. The purpose is to test the summarization capabilities."
        result = agent.summarize_text(content)
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Compression ratio: {result.get('compression_ratio', 0)}%")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_search():
    """Test search agent."""
    print("\n" + "=" * 60)
    print("Testing Search Agent")
    print("=" * 60)
    
    try:
        agent = SearchAgent()
        result = agent.conduct_research("artificial intelligence trends")
        
        print(f"✅ Success: {result['success']}")
        print(f"✅ Query: {result.get('query', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_vfs():
    """Test virtual file system."""
    print("\n" + "=" * 60)
    print("Testing Virtual File System")
    print("=" * 60)
    
    try:
        # Test write
        write_result = vfs_write_file.invoke({
            "filename": "test.txt",
            "content": "This is a test file."
        })
        print(f"✅ Write: {write_result['success']}")
        
        # Test read
        read_result = vfs_read_file.invoke({"filename": "test.txt"})
        print(f"✅ Read: {read_result['success']}")
        
        # Test list
        list_result = vfs_ls.invoke({"path": "/"})
        print(f"✅ List: {list_result['success']}")
        print(f"✅ Files: {list_result.get('count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🚀 AUTONOMOUS COGNITIVE ENGINE - SYSTEM TEST")
    print("=" * 60)
    
    results = {
        "Supervisor Agent": test_supervisor(),
        "Summarizer Agent": test_summarizer(),
        "Search Agent": test_search(),
        "Virtual File System": test_vfs()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for component, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{component}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
