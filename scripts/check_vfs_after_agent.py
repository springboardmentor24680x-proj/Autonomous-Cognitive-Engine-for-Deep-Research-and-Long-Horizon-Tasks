#!/usr/bin/env python3
import sys
sys.path.append('src')
from memory.vfs import get_vfs
from agents.supervisor_agent import SupervisorAgent

# Run agent first
print('🤖 Running agent with long response...')
supervisor = SupervisorAgent()
result = supervisor.run_with_context('Create a detailed budget plan for a family of 4 with $75,000 annual income', [])
print(f'Agent Success: {result["success"]}')
print(f'Tools Used: {result.get("tools_used", 0)}')
print(f'Response Length: {len(result.get("final_response", ""))}')

# Check VFS immediately after
print('\n📁 Checking VFS after agent run...')
vfs = get_vfs()
stats = vfs.get_stats()
print(f'Files in VFS: {stats["stats"]["total_files"]}')

if stats['stats']['files']:
    for filename in stats['stats']['files']:
        file_info = vfs.read_file(filename)
        if file_info['success']:
            print(f'  📄 {filename}: {len(file_info["content"])} chars')
            print(f'     Preview: {file_info["content"][:100]}...')
else:
    print('  No files found in VFS')