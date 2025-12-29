#!/usr/bin/env python3
import sys
sys.path.append('src')
from memory.vfs import get_vfs

vfs = get_vfs()
stats = vfs.get_stats()

print('📊 Current VFS Status:')
print(f'Files: {stats["stats"]["total_files"]}')
print(f'Total Size: {stats["stats"]["total_size"]} characters')
print()

print('📁 Files in VFS:')
for filename in stats['stats']['files']:
    file_info = vfs.read_file(filename)
    if file_info['success']:
        print(f'  📄 {filename} ({len(file_info["content"])} chars)')
        print(f'     Preview: {file_info["content"][:100]}...')
        print()