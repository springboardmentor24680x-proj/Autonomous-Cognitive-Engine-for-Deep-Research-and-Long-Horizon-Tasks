#!/usr/bin/env python3
"""
Read File Tools - Virtual File System read operations
Part of the multi-agent workflow automation system
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
from memory.vfs import get_vfs


@tool
def vfs_read_file(filename: str) -> Dict[str, Any]:
    """
    Read content from a file in the virtual file system.
    Supports both persistent and in-memory storage.
    
    Args:
        filename: Name of the file to read
        
    Returns:
        Dict with success status, filename, content, size, and message
    """
    try:
        vfs = get_vfs()
        return vfs.read_file(filename)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to read file '{filename}': {str(e)}"
        }


@tool
def vfs_ls(path: str = "/") -> Dict[str, Any]:
    """
    List files in the virtual file system.
    Shows all files from persistent and in-memory storage.
    
    Args:
        path: Path to list (currently only "/" is supported)
        
    Returns:
        Dict with success status, files list, count, and message
    """
    try:
        vfs = get_vfs()
        return vfs.list_files(path)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to list files in '{path}': {str(e)}"
        }


@tool
def vfs_edit_file(filename: str, operation: str, content: str) -> Dict[str, Any]:
    """
    Edit an existing file in the virtual file system.
    
    Args:
        filename: Name of the file to edit
        operation: Type of edit operation ('append', 'prepend', 'replace')
        content: Content to add/replace
        
    Returns:
        Dict with success status, operation details, and message
    """
    try:
        vfs = get_vfs()
        return vfs.edit_file(filename, operation, content)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to edit file '{filename}': {str(e)}"
        }


@tool
def get_file_info(filename: str) -> Dict[str, Any]:
    """
    Get metadata information about a file.
    
    Args:
        filename: Name of the file
        
    Returns:
        Dict with file metadata and information
    """
    try:
        vfs = get_vfs()
        return vfs.get_file_info(filename)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get info for '{filename}': {str(e)}"
        }


@tool
def search_files(query: str) -> Dict[str, Any]:
    """
    Search for files containing specific content.
    
    Args:
        query: Search query string
        
    Returns:
        Dict with matching files and search results
    """
    try:
        vfs = get_vfs()
        return vfs.search_files(query)
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Search failed for query '{query}': {str(e)}"
        }


def read_multiple_files(filenames: List[str]) -> Dict[str, Any]:
    """
    Read multiple files at once.
    
    Args:
        filenames: List of filenames to read
        
    Returns:
        Dict with results for each file
    """
    try:
        vfs = get_vfs()
        results = {}
        
        for filename in filenames:
            results[filename] = vfs.read_file(filename)
        
        return {
            "success": True,
            "files": results,
            "count": len(filenames),
            "message": f"Read {len(filenames)} files"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to read multiple files: {str(e)}"
        }


def get_vfs_stats() -> Dict[str, Any]:
    """
    Get statistics about the virtual file system.
    
    Returns:
        Dict with VFS statistics
    """
    try:
        vfs = get_vfs()
        return vfs.get_stats()
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get VFS stats: {str(e)}"
        }