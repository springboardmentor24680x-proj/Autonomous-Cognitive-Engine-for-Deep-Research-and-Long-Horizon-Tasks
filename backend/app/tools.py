from datetime import datetime
import uuid
from typing import Dict
from .utils import AgentState

class ToolExecutor:
    """Executes tools and updates state - returns rich data for narration"""
   
    @staticmethod
    def create_todo(state: AgentState, title: str, description: str = "",
                    priority: str = "medium", due_date: str = None) -> dict:
        """Create a new todo item"""
        todo = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        state["todos"].append(todo)
        return {
            "success": True,
            "action": "created_todo",
            "todo": todo,
            "summary": f"Created task: '{title}' with {priority} priority"
        }
   
    @staticmethod
    def create_multiple_todos(state: AgentState, todos_list: list[dict]) -> dict:
        """Create multiple todos at once (for trip planning, etc.)"""
        created = []
        summaries = {"high": [], "medium": [], "low": []}
       
        for item in todos_list:
            priority = item.get("priority", "medium")
            todo = {
                "id": str(uuid.uuid4())[:8],
                "title": item.get("title", "Untitled"),
                "description": item.get("description", ""),
                "priority": priority,
                "due_date": item.get("due_date"),
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            state["todos"].append(todo)
            created.append(todo)
            summaries[priority].append(todo["title"])
       
        return {
            "success": True,
            "action": "created_multiple_todos",
            "count": len(created),
            "todos": created,
            "by_priority": summaries,
            "summary": f"Created {len(created)} tasks"
        }
   
    @staticmethod
    def update_todo(state: AgentState, todo_id: str = None, title_match: str = None,
                    updates: dict = None) -> dict:
        """Update an existing todo by ID or title match"""
        for todo in state["todos"]:
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                old_title = todo["title"]
                if updates:
                    todo.update(updates)
                return {
                    "success": True,
                    "action": "updated_todo",
                    "todo": todo,
                    "summary": f"Updated task '{old_title}'"
                }
        return {"success": False, "action": "update_todo_failed", "summary": "Task not found"}
   
    @staticmethod
    def complete_todo(state: AgentState, todo_id: str = None, title_match: str = None) -> dict:
        """Mark a todo as completed"""
        for todo in state["todos"]:
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                todo["completed"] = True
                return {
                    "success": True,
                    "action": "completed_todo",
                    "todo": todo,
                    "summary": f"Completed: '{todo['title']}'"
                }
        return {"success": False, "action": "complete_todo_failed", "summary": "Task not found"}
   
    @staticmethod
    def delete_todo(state: AgentState, todo_id: str = None, title_match: str = None) -> dict:
        """Delete a todo"""
        for i, todo in enumerate(state["todos"]):
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                removed = state["todos"].pop(i)
                return {
                    "success": True,
                    "action": "deleted_todo",
                    "summary": f"Deleted task: '{removed['title']}'"
                }
        return {"success": False, "action": "delete_todo_failed", "summary": "Task not found"}
   
    @staticmethod
    def create_calendar_event(state: AgentState, title: str, date: str, time: str,
                              duration_minutes: int = 60, attendees: list[str] = None,
                              description: str = "") -> dict:
        """Create a calendar event"""
        event = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "attendees": attendees or [],
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        state["calendar"].append(event)
        state["context"]["last_meeting_id"] = event["id"]
       
        # Format time for display
        try:
            time_obj = datetime.strptime(time, "%H:%M")
            formatted_time = time_obj.strftime("%I:%M %p")
        except:
            formatted_time = time
           
        # Format date for display
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = date
       
        return {
            "success": True,
            "action": "created_calendar_event",
            "event": event,
            "formatted_date": formatted_date,
            "formatted_time": formatted_time,
            "summary": f"Scheduled '{title}' on {formatted_date} at {formatted_time}"
        }
   
    @staticmethod
    def update_calendar_event(state: AgentState, event_id: str = None,
                              title_match: str = None, updates: dict = None) -> dict:
        """Update a calendar event"""
        # If no ID provided, use last meeting from context
        if not event_id and not title_match:
            event_id = state["context"].get("last_meeting_id")
       
        for event in state["calendar"]:
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                changes_made = []
                if updates:
                    # Handle attendee additions specially
                    if "add_attendees" in updates:
                        new_attendees = updates["add_attendees"]
                        event["attendees"] = list(set(event.get("attendees", []) + new_attendees))
                        changes_made.append(f"Added {', '.join(new_attendees)} to attendees")
                        del updates["add_attendees"]
                   
                    for key, value in updates.items():
                        event[key] = value
                        changes_made.append(f"Updated {key} to {value}")
               
                return {
                    "success": True,
                    "action": "updated_calendar_event",
                    "event": event,
                    "changes": changes_made,
                    "summary": f"Updated '{event['title']}': {'; '.join(changes_made)}"
                }
        return {"success": False, "action": "update_event_failed", "summary": "Event not found"}
   
    @staticmethod
    def delete_calendar_event(state: AgentState, event_id: str = None,
                              title_match: str = None) -> dict:
        """Delete a calendar event"""
        for i, event in enumerate(state["calendar"]):
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                removed = state["calendar"].pop(i)
                return {
                    "success": True,
                    "action": "deleted_calendar_event",
                    "summary": f"Cancelled event: '{removed['title']}'"
                }
        return {"success": False, "action": "delete_event_failed", "summary": "Event not found"}
   
    @staticmethod
    def save_file(state: AgentState, filename: str, content: str) -> dict:
        """Save content to a file"""
        state["files"][filename] = content
        return {
            "success": True,
            "action": "saved_file",
            "filename": filename,
            "size": len(content),
            "summary": f"Saved file: '{filename}' ({len(content)} characters)"
        }
   
    @staticmethod
    def read_file(state: AgentState, filename: str) -> dict:
        """Read a file's content"""
        if filename in state["files"]:
            content = state["files"][filename]
            return {
                "success": True,
                "action": "read_file",
                "filename": filename,
                "content": content,
                "summary": f"Read file: '{filename}'"
            }
        return {"success": False, "action": "read_file_failed", "summary": f"File not found: {filename}"}
   
    @staticmethod
    def delete_file(state: AgentState, filename: str) -> dict:
        """Delete a file"""
        if filename in state["files"]:
            del state["files"][filename]
            return {
                "success": True,
                "action": "deleted_file",
                "summary": f"Deleted file: '{filename}'"
            }
        return {"success": False, "action": "delete_file_failed", "summary": f"File not found: {filename}"}
   
    @staticmethod
    def export_todos_to_file(state: AgentState, filename: str = "tasks.txt") -> dict:
        """Export all todos to a formatted file"""
        if not state["todos"]:
            return {"success": False, "action": "export_failed", "summary": "No tasks to export"}
       
        content_lines = ["=" * 50, "MY TASKS", "=" * 50, ""]
       
        completed_count = 0
        pending_count = 0
       
        for i, todo in enumerate(state["todos"], 1):
            status = "✓" if todo["completed"] else "○"
            if todo["completed"]:
                completed_count += 1
            else:
                pending_count += 1
            content_lines.append(f"{i}. [{status}] {todo['title']}")
            if todo.get("description"):
                content_lines.append(f" Description: {todo['description']}")
            if todo.get("priority"):
                content_lines.append(f" Priority: {todo['priority']}")
            if todo.get("due_date"):
                content_lines.append(f" Due: {todo['due_date']}")
            content_lines.append("")
       
        content_lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        content = "\n".join(content_lines)
        state["files"][filename] = content
       
        return {
            "success": True,
            "action": "exported_todos",
            "filename": filename,
            "total_tasks": len(state["todos"]),
            "completed": completed_count,
            "pending": pending_count,
            "summary": f"Exported {len(state['todos'])} tasks ({pending_count} pending, {completed_count} completed) to '{filename}'"
        }