#!/usr/bin/env python3
"""
VFS Manager - Simple tool to manage and view VFS contents
Fixes the "messy" VFS experience
"""

import sys
import os
sys.path.append('src')

from memory.vfs import get_vfs
from memory.persistent_vfs import get_persistent_vfs

def show_current_vfs():
    """Show current in-memory VFS contents."""
    print("🗂️ CURRENT IN-MEMORY VFS")
    print("=" * 40)
    
    vfs = get_vfs()
    stats = vfs.get_stats()
    
    if stats['success']:
        print(f"📊 Files: {stats['stats']['total_files']}")
        print(f"📊 Size: {stats['stats']['total_size']} characters")
        print()
        
        if stats['stats']['files']:
            print("📁 Files:")
            for filename in stats['stats']['files']:
                file_info = vfs.read_file(filename)
                if file_info['success']:
                    content = file_info['content']
                    print(f"  📄 {filename} ({len(content)} chars)")
                    print(f"     Created: {file_info['metadata'].get('created_at', 'unknown')}")
                    print(f"     Preview: {content[:80]}{'...' if len(content) > 80 else ''}")
                    print()
        else:
            print("📁 No files in memory")
    else:
        print("❌ Could not get VFS stats")

def show_persistent_vfs():
    """Show persistent VFS contents."""
    print("\n💾 PERSISTENT VFS")
    print("=" * 40)
    
    pvfs = get_persistent_vfs()
    stats = pvfs.get_stats()
    
    if stats['success']:
        print(f"📊 Total Files: {stats['stats']['total_files']}")
        print(f"📊 User Files: {stats['stats']['user_files']}")
        print(f"📊 Temp Files: {stats['stats']['temp_files']}")
        print(f"📊 Total Size: {stats['stats']['total_size']} characters")
        print(f"📊 Storage: {stats['stats']['storage_dir']}")
        print()
        
        if stats['stats']['files']:
            print("📁 Files:")
            for filename in stats['stats']['files']:
                file_info = pvfs.read_file(filename)
                if file_info['success']:
                    content = file_info['content']
                    is_temp = filename.startswith('chat_')
                    icon = "🗑️" if is_temp else "📄"
                    print(f"  {icon} {filename} ({len(content)} chars)")
                    print(f"     Created: {file_info['metadata'].get('created_at', 'unknown')}")
                    print(f"     Preview: {content[:80]}{'...' if len(content) > 80 else ''}")
                    print()
        else:
            print("📁 No persistent files")
    else:
        print("❌ Could not get persistent VFS stats")

def clean_temp_files():
    """Clean up temporary files."""
    print("\n🧹 CLEANING TEMPORARY FILES")
    print("=" * 40)
    
    # Clean in-memory VFS
    vfs = get_vfs()
    stats = vfs.get_stats()
    if stats['success']:
        temp_files = [f for f in stats['stats']['files'] if f.startswith('chat_')]
        for filename in temp_files:
            result = vfs.delete_file(filename)
            if result['success']:
                print(f"🗑️ Deleted: {filename}")
    
    # Clean persistent VFS
    pvfs = get_persistent_vfs()
    result = pvfs.clean_temp_files()
    if result['success']:
        print(f"🗑️ Cleaned {result['deleted_count']} persistent temp files")

def test_persistent_vfs():
    """Test the persistent VFS."""
    print("\n🧪 TESTING PERSISTENT VFS")
    print("=" * 40)
    
    pvfs = get_persistent_vfs()
    
    # Write a test file
    result = pvfs.write_file("test_persistent.txt", "This is a persistent test file that survives restarts!")
    print(f"Write: {result['success']} - {result['message']}")
    
    # Read it back
    result = pvfs.read_file("test_persistent.txt")
    print(f"Read: {result['success']} - Content: {result.get('content', 'N/A')[:50]}...")
    
    # List files
    result = pvfs.list_files()
    print(f"List: {result['success']} - Found {result['count']} files")

def interactive_menu():
    """Interactive VFS management menu."""
    while True:
        print("\n🗂️ VFS MANAGER")
        print("=" * 30)
        print("1. Show Current VFS")
        print("2. Show Persistent VFS")
        print("3. Clean Temp Files")
        print("4. Test Persistent VFS")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            show_current_vfs()
        elif choice == '2':
            show_persistent_vfs()
        elif choice == '3':
            clean_temp_files()
        elif choice == '4':
            test_persistent_vfs()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def main():
    """Main VFS manager function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'show':
            show_current_vfs()
            show_persistent_vfs()
        elif command == 'clean':
            clean_temp_files()
        elif command == 'test':
            test_persistent_vfs()
        else:
            print("Usage: python vfs_manager.py [show|clean|test]")
    else:
        interactive_menu()

if __name__ == "__main__":
    main()