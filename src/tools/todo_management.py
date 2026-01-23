#!/usr/bin/env python3
"""
TODO Management Tools - Complete TODO lifecycle management with VFS integration
Part of the multi-agent workflow automation system
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.tools import tool
from memory.vfs import get_vfs, get_current_agent_state, update_agent_state


@tool
def write_todos(task_description: str, todo_list: List[str]) -> Dict[str, Any]:
    """
    Create and persist a list of TODO items for a complex task.
    
    Args:
        task_description: The main task description
        todo_list: List of sub-task descriptions
        
    Returns:
        Dict with created TODO items and VFS storage info
    """
    try:
        vfs = get_vfs()
        todos_created = []
        
        # Create TODO items
        for i, todo_task in enumerate(todo_list, 1):
            todo_id = f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i:02d}"
            
            todo_item = {
                "id": todo_id,
                "task": todo_task,
                "main_task": task_description,
                "priority": "medium",
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "assigned_agent": None,
                "result": None,
                "result_file": None,
                "completed_at": None
            }
            
            todos_created.append(todo_item)
        
        # Save TODOs to VFS
        todos_filename = f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        todos_data = {
            "main_task": task_description,
            "created_at": datetime.now().isoformat(),
            "total_todos": len(todos_created),
            "todos": todos_created
        }
        
        vfs_result = vfs.write_file(todos_filename, json.dumps(todos_data, indent=2))
        
        # Update agent state
        state = get_current_agent_state()
        state["todos"] = todos_created
        state["todos_file"] = todos_filename
        state["current_todo_index"] = 0
        
        return {
            "success": True,
            "todos_created": len(todos_created),
            "todos_file": todos_filename,
            "todo_items": todos_created,
            "vfs_result": vfs_result,
            "message": f"Created {len(todos_created)} TODO items and saved to {todos_filename}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create TODOs: {str(e)}"
        }


@tool
def get_next_todo() -> Dict[str, Any]:
    """
    Get the next pending TODO item from the current task list.
    
    Returns:
        Dict with next TODO item or completion status
    """
    try:
        state = get_current_agent_state()
        todos = state.get("todos", [])
        current_index = state.get("current_todo_index", 0)
        
        if not todos:
            return {
                "success": False,
                "message": "No TODOs found in current state",
                "has_next": False
            }
        
        # Find next pending TODO
        for i in range(current_index, len(todos)):
            todo = todos[i]
            if todo["status"] == "pending":
                # Update current index
                state["current_todo_index"] = i
                return {
                    "success": True,
                    "todo": todo,
                    "todo_index": i,
                    "has_next": True,
                    "remaining_todos": len([t for t in todos if t["status"] == "pending"]),
                    "message": f"Next TODO: {todo['task']}"
                }
        
        # No pending TODOs found
        return {
            "success": True,
            "has_next": False,
            "message": "All TODOs completed",
            "completed_todos": len([t for t in todos if t["status"] == "completed"]),
            "total_todos": len(todos)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get next TODO: {str(e)}"
        }


@tool
def complete_todo(todo_id: str, result: str, assigned_agent: str = None) -> Dict[str, Any]:
    """
    Mark a TODO as completed and save the result to VFS.
    
    Args:
        todo_id: ID of the TODO to complete
        result: The result/output of the completed task
        assigned_agent: Name of the agent that completed the task
        
    Returns:
        Dict with completion status and result file info
    """
    try:
        vfs = get_vfs()
        state = get_current_agent_state()
        todos = state.get("todos", [])
        
        # Find and update the TODO
        todo_found = False
        for todo in todos:
            if todo["id"] == todo_id:
                todo["status"] = "completed"
                todo["completed_at"] = datetime.now().isoformat()
                todo["assigned_agent"] = assigned_agent
                todo["result"] = result[:500] + "..." if len(result) > 500 else result  # Summary
                
                # Save full result to VFS
                result_filename = f"result_{todo_id}.txt"
                result_content = f"""TODO Task: {todo['task']}
Assigned Agent: {assigned_agent}
Completed At: {todo['completed_at']}
Main Task: {todo.get('main_task', 'N/A')}

=== RESULT ===
{result}

=== METADATA ===
TODO ID: {todo_id}
Status: completed
Priority: {todo.get('priority', 'medium')}
"""
                
                vfs_result = vfs.write_file(result_filename, result_content)
                todo["result_file"] = result_filename
                todo_found = True
                break
        
        if not todo_found:
            return {
                "success": False,
                "error": f"TODO with ID {todo_id} not found",
                "message": f"Could not find TODO: {todo_id}"
            }
        
        # Update TODOs file in VFS
        todos_file = state.get("todos_file")
        if todos_file:
            todos_data = {
                "main_task": todos[0].get("main_task", "Unknown") if todos else "Unknown",
                "updated_at": datetime.now().isoformat(),
                "total_todos": len(todos),
                "completed_todos": len([t for t in todos if t["status"] == "completed"]),
                "todos": todos
            }
            vfs.write_file(todos_file, json.dumps(todos_data, indent=2))
        
        # Update agent state
        state["todos"] = todos
        
        return {
            "success": True,
            "todo_id": todo_id,
            "result_file": result_filename,
            "completed_todos": len([t for t in todos if t["status"] == "completed"]),
            "remaining_todos": len([t for t in todos if t["status"] == "pending"]),
            "message": f"TODO {todo_id} completed and result saved to {result_filename}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to complete TODO: {str(e)}"
        }


@tool
def get_todo_status() -> Dict[str, Any]:
    """
    Get the current status of all TODOs in the workflow.
    
    Returns:
        Dict with TODO status summary
    """
    try:
        state = get_current_agent_state()
        todos = state.get("todos", [])
        
        if not todos:
            return {
                "success": True,
                "total_todos": 0,
                "message": "No TODOs in current workflow"
            }
        
        completed = [t for t in todos if t["status"] == "completed"]
        pending = [t for t in todos if t["status"] == "pending"]
        
        return {
            "success": True,
            "total_todos": len(todos),
            "completed_todos": len(completed),
            "pending_todos": len(pending),
            "completion_rate": len(completed) / len(todos) * 100,
            "todos_file": state.get("todos_file"),
            "current_index": state.get("current_todo_index", 0),
            "todos": todos,
            "message": f"Status: {len(completed)}/{len(todos)} TODOs completed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get TODO status: {str(e)}"
        }


@tool
def synthesize_todo_results() -> Dict[str, Any]:
    """
    Read all TODO result files from VFS and synthesize into final output.
    
    Returns:
        Dict with synthesized results from all completed TODOs
    """
    try:
        vfs = get_vfs()
        state = get_current_agent_state()
        todos = state.get("todos", [])
        
        if not todos:
            return {
                "success": False,
                "message": "No TODOs found to synthesize"
            }
        
        completed_todos = [t for t in todos if t["status"] == "completed"]
        
        if not completed_todos:
            return {
                "success": False,
                "message": "No completed TODOs to synthesize"
            }
        
        # Read all result files
        synthesized_results = []
        result_files_read = []
        
        for todo in completed_todos:
            result_file = todo.get("result_file")
            if result_file:
                file_result = vfs.read_file(result_file)
                if file_result["success"]:
                    synthesized_results.append({
                        "todo_id": todo["id"],
                        "task": todo["task"],
                        "agent": todo.get("assigned_agent"),
                        "completed_at": todo.get("completed_at"),
                        "result_content": file_result["content"],
                        "result_file": result_file
                    })
                    result_files_read.append(result_file)
        
        # Create synthesis summary
        main_task = todos[0].get("main_task", "Complex Task") if todos else "Complex Task"
        synthesis_content = f"""# COMPREHENSIVE TASK COMPLETION REPORT

## Main Task
{main_task}

## Execution Summary
- **Total TODOs**: {len(todos)}
- **Completed**: {len(completed_todos)}
- **Success Rate**: {len(completed_todos)/len(todos)*100:.1f}%
- **Completion Time**: {datetime.now().isoformat()}

## Individual TODO Results

"""
        
        for i, result in enumerate(synthesized_results, 1):
            synthesis_content += f"""### {i}. {result['task']}
- **Agent**: {result['agent']}
- **Completed**: {result['completed_at']}
- **Result File**: {result['result_file']}

**Output:**
{result['result_content']}

---

"""
        
        # Save synthesis to VFS
        synthesis_filename = f"synthesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        vfs.write_file(synthesis_filename, synthesis_content)
        
        return {
            "success": True,
            "synthesis_file": synthesis_filename,
            "synthesis_content": synthesis_content,
            "result_files_read": result_files_read,
            "completed_todos": len(completed_todos),
            "total_todos": len(todos),
            "message": f"Synthesized {len(completed_todos)} TODO results into {synthesis_filename}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to synthesize results: {str(e)}"
        }


@tool
def reset_todo_workflow() -> Dict[str, Any]:
    """
    Reset the current TODO workflow state.
    
    Returns:
        Dict with reset confirmation
    """
    try:
        state = get_current_agent_state()
        state["todos"] = []
        state["todos_file"] = None
        state["current_todo_index"] = 0
        
        return {
            "success": True,
            "message": "TODO workflow state reset successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to reset workflow: {str(e)}"
        }