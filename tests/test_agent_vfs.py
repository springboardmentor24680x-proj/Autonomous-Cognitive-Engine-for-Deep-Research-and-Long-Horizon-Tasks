#!/usr/bin/env python3
import sys
sys.path.append('src')
from agents.supervisor_agent import SupervisorAgent

print('🤖 Testing VFS with Agent...')
supervisor = SupervisorAgent()
result = supervisor.run_with_context('Create a detailed budget plan for a family of 4 with $75,000 annual income', [])
print(f'Success: {result["success"]}')
print(f'Tools Used: {result.get("tools_used", 0)}')
print(f'Response Length: {len(result.get("final_response", ""))}')
print(f'Response Preview: {result.get("final_response", "")[:200]}...')