#!/usr/bin/env python3
"""
Write File Tool - Virtual File System write operations
Part of the multi-agent workflow automation system
"""

from typing import Dict, Any
from langchain_core.tools import tool
from memory.vfs import get_vfs, update_agent_state


@tool
def vfs_write_file(filename: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file in the virtual file system.
    Uses persistent storage to avoid data loss on restart.
    
    Args:
        filename: Name of the file to create/write
        content: Content to write to the file
        
    Returns:
        Dict with success status, filename, size, and message
    """
    try:
        vfs = get_vfs()
        result = vfs.write_file(filename, content)
        
        # Update agent state
        if result["success"]:
            update_agent_state("virtual_files", filename, content)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to write file '{filename}': {str(e)}"
        }


@tool  
def create_file(filename: str, content: str) -> Dict[str, Any]:
    """
    Create a new file in the virtual file system.
    Alias for vfs_write_file for compatibility.
    
    Args:
        filename: Name of the file to create
        content: Initial content for the file
        
    Returns:
        Dict with success status and file information
    """
    return vfs_write_file(filename, content)


def save_content(filename: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
    """
    Save content to a file with overwrite protection.
    
    Args:
        filename: Name of the file
        content: Content to save
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict with operation result
    """
    try:
        vfs = get_vfs()
        
        # Check if file exists and overwrite is False
        if not overwrite and filename in vfs.files:
            return {
                "success": False,
                "error": "File exists",
                "message": f"File '{filename}' already exists and overwrite is disabled"
            }
        
        return vfs.write_file(filename, content)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save content to '{filename}': {str(e)}"
        }