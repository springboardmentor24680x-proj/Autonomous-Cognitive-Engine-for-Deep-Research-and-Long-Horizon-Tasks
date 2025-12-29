#!/usr/bin/env python3
"""
Virtual File System (VFS) - Memory management for multi-agent workflow automation
Provides persistent context and information storage across agent interactions
Enhanced with persistent storage to fix "messy" user experience issues
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class VirtualFileSystem:
    """
    Virtual File System for agent memory management.
    Provides file-like operations for storing and retrieving context.
    Enhanced with persistent storage to avoid data loss on restart.
    """
    
    def __init__(self, enable_persistence: bool = True, storage_dir: str = "data/vfs_storage"):
        """Initialize the virtual file system."""
        self.files: Dict[str, str] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.now()
        
        # Persistent storage setup
        self.enable_persistence = enable_persistence
        if enable_persistence:
            self.storage_dir = Path(storage_dir)
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            self.metadata_file = self.storage_dir / "metadata.json"
            self.files_dir = self.storage_dir / "files"
            self.files_dir.mkdir(exist_ok=True)
            
            # Load existing data
            self._load_persistent_data()
    
    def _load_persistent_data(self):
        """Load persistent data from disk."""
        if not self.enable_persistence:
            return
            
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception:
                self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata to disk."""
        if not self.enable_persistence:
            return
            
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def _get_file_path(self, filename: str) -> Path:
        """Get the full path for a persistent file."""
        if not self.enable_persistence:
            return None
            
        # Sanitize filename for filesystem
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return self.files_dir / safe_filename
    
    def _save_file_to_disk(self, filename: str, content: str):
        """Save file content to disk."""
        if not self.enable_persistence:
            return
            
        try:
            file_path = self._get_file_path(filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Could not save file to disk: {e}")
    
    def _load_file_from_disk(self, filename: str) -> Optional[str]:
        """Load file content from disk."""
        if not self.enable_persistence:
            return None
            
        try:
            file_path = self._get_file_path(filename)
            if file_path and file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return None
    
    def write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Write content to a virtual file with persistent storage."""
        try:
            # Store in memory
            self.files[filename] = content
            
            # Update metadata
            self.metadata[filename] = {
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "size": len(content),
                "type": "text",
                "persistent": self.enable_persistence
            }
            
            # Save to disk if persistence enabled
            if self.enable_persistence:
                self._save_file_to_disk(filename, content)
                self._save_metadata()
            
            return {
                "success": True,
                "filename": filename,
                "size": len(content),
                "persistent": self.enable_persistence,
                "message": f"Successfully wrote {len(content)} characters to '{filename}'" + 
                          (" (persistent)" if self.enable_persistence else " (memory only)")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to write to '{filename}': {str(e)}"
            }
    
    def read_file(self, filename: str) -> Dict[str, Any]:
        """Read content from a virtual file with persistent storage support."""
        try:
            content = None
            
            # Try memory first
            if filename in self.files:
                content = self.files[filename]
            # Try disk if persistence enabled
            elif self.enable_persistence:
                content = self._load_file_from_disk(filename)
                if content is not None:
                    # Load into memory for faster access
                    self.files[filename] = content
            
            if content is None:
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"File '{filename}' does not exist"
                }
            
            metadata = self.metadata.get(filename, {})
            
            return {
                "success": True,
                "filename": filename,
                "content": content,
                "size": len(content),
                "metadata": metadata,
                "persistent": self.enable_persistence,
                "message": f"Successfully read {len(content)} characters from '{filename}'" +
                          (" (persistent)" if self.enable_persistence else " (memory only)")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to read '{filename}': {str(e)}"
            }
    
    def list_files(self, path: str = "/") -> Dict[str, Any]:
        """List all files in the virtual file system."""
        try:
            files = list(self.files.keys())
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "path": path,
                "message": f"Found {len(files)} files in {path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list files: {str(e)}"
            }
    
    def edit_file(self, filename: str, operation: str, content: str) -> Dict[str, Any]:
        """Edit an existing virtual file."""
        try:
            if filename not in self.files:
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"File '{filename}' does not exist"
                }
            
            current_content = self.files[filename]
            
            if operation == "append":
                new_content = current_content + "\n" + content
            elif operation == "prepend":
                new_content = content + "\n" + current_content
            elif operation == "replace":
                new_content = content
            else:
                return {
                    "success": False,
                    "error": "Invalid operation",
                    "message": f"Operation '{operation}' not supported. Use 'append', 'prepend', or 'replace'"
                }
            
            self.files[filename] = new_content
            self.metadata[filename]["modified_at"] = datetime.now().isoformat()
            self.metadata[filename]["size"] = len(new_content)
            
            added_chars = len(new_content) - len(current_content)
            
            return {
                "success": True,
                "filename": filename,
                "operation": operation,
                "size": len(new_content),
                "added_chars": added_chars,
                "message": f"{operation.capitalize()}ed {len(content)} characters to '{filename}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to edit '{filename}': {str(e)}"
            }
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a virtual file."""
        try:
            if filename not in self.files:
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"File '{filename}' does not exist"
                }
            
            del self.files[filename]
            if filename in self.metadata:
                del self.metadata[filename]
            
            return {
                "success": True,
                "filename": filename,
                "message": f"Successfully deleted '{filename}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete '{filename}': {str(e)}"
            }
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get metadata information about a file."""
        try:
            if filename not in self.files:
                return {
                    "success": False,
                    "error": "File not found",
                    "message": f"File '{filename}' does not exist"
                }
            
            metadata = self.metadata.get(filename, {})
            
            return {
                "success": True,
                "filename": filename,
                "metadata": metadata,
                "exists": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get info for '{filename}': {str(e)}"
            }
    
    def search_files(self, query: str) -> Dict[str, Any]:
        """Search for files containing specific content."""
        try:
            matching_files = []
            
            for filename, content in self.files.items():
                if query.lower() in content.lower() or query.lower() in filename.lower():
                    matching_files.append({
                        "filename": filename,
                        "size": len(content),
                        "metadata": self.metadata.get(filename, {})
                    })
            
            return {
                "success": True,
                "query": query,
                "matches": matching_files,
                "count": len(matching_files),
                "message": f"Found {len(matching_files)} files matching '{query}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Search failed: {str(e)}"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the virtual file system."""
        try:
            total_files = len(self.files)
            total_size = sum(len(content) for content in self.files.values())
            
            return {
                "success": True,
                "stats": {
                    "total_files": total_files,
                    "total_size": total_size,
                    "created_at": self.created_at.isoformat(),
                    "files": list(self.files.keys())
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get stats: {str(e)}"
            }


# Global VFS instance and state management
_global_vfs = VirtualFileSystem()
_current_agent_state = {
    "virtual_files": {},
    "todos": [],
    "current_todo_id": None,
    "step_count": 0,
    "max_steps": 10
}


def get_vfs() -> VirtualFileSystem:
    """Get the global VFS instance."""
    return _global_vfs


def get_current_agent_state() -> Dict[str, Any]:
    """Get the current agent state for tools to access."""
    return _current_agent_state


def update_agent_state(section: str, key: str, value: Any) -> bool:
    """Update a specific section of the agent state."""
    global _current_agent_state
    try:
        if section == "virtual_files":
            _current_agent_state["virtual_files"][key] = value
        elif section in _current_agent_state:
            _current_agent_state[section] = value
        
        return True
    except Exception:
        return False


def reset_agent_state():
    """Reset the agent state to initial values."""
    global _current_agent_state, _global_vfs
    _current_agent_state = {
        "virtual_files": {},
        "todos": [],
        "current_todo_id": None,
        "step_count": 0,
        "max_steps": 10
    }
    _global_vfs = VirtualFileSystem()


def export_state() -> Dict[str, Any]:
    """Export the current state for persistence."""
    return {
        "agent_state": _current_agent_state,
        "vfs_files": _global_vfs.files,
        "vfs_metadata": _global_vfs.metadata,
        "exported_at": datetime.now().isoformat()
    }


def import_state(state_data: Dict[str, Any]) -> bool:
    """Import state from exported data."""
    global _current_agent_state, _global_vfs
    try:
        _current_agent_state = state_data.get("agent_state", _current_agent_state)
        _global_vfs.files = state_data.get("vfs_files", {})
        _global_vfs.metadata = state_data.get("vfs_metadata", {})
        return True
    except Exception:
        return False