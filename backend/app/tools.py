from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

from .utils import AgentState, sanitize_filename


class ToolExecutor:
    """
    Pure state-mutating tools with comprehensive error handling.
    All tools return consistent result dictionaries with:
    - success: bool
    - action: str (operation performed)
    - summary: str (human-readable description)
    - Additional context-specific fields
    """

    @staticmethod
    def create_todo(
        state: AgentState,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> dict:
        """Create a single new todo"""
        if not title or not title.strip():
            return {
                "success": False,
                "action": "create_todo_failed",
                "summary": "Task title cannot be empty"
            }
        
        # Validate priority
        priority = priority.lower()
        if priority not in ["high", "medium", "low"]:
            priority = "medium"
        
        todo = {
            "id": str(uuid.uuid4())[:8],
            "title": str(title).strip(),
            "description": str(description).strip(),
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        state["todos"].append(todo)
        
        # Format due date for display
        due_str = f", due {due_date}" if due_date else ""
        
        return {
            "success": True,
            "action": "created_todo",
            "todo": todo,
            "summary": f"✅ Created task: '{todo['title']}' (Priority: {todo['priority'].upper()}{due_str})"
        }

    @staticmethod
    def create_multiple_todos(state: AgentState, todos_list: List[Dict[str, Any]]) -> dict:
        """Create multiple todos at once"""
        if not todos_list:
            return {
                "success": False,
                "action": "create_multiple_failed",
                "summary": "❌ No tasks provided"
            }

        created_todos = []
        by_priority = {"high": 0, "medium": 0, "low": 0}
        created_titles = []

        for item in todos_list:
            title = str(item.get("title") or item.get("task") or "").strip()
            if not title:
                continue
            
            priority = str(item.get("priority", "medium")).lower()
            if priority not in ["high", "medium", "low"]:
                priority = "medium"
            
            todo = {
                "id": str(uuid.uuid4())[:8],
                "title": title,
                "description": str(item.get("description", "")).strip(),
                "priority": priority,
                "due_date": item.get("due_date"),
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            state["todos"].append(todo)
            created_todos.append(todo)
            by_priority[priority] += 1
            created_titles.append(title)

        if not created_todos:
            return {
                "success": False,
                "action": "create_multiple_failed",
                "summary": "❌ No valid tasks created"
            }

        priority_summary = [f"{count} {priority}" for priority, count in by_priority.items() if count > 0]
        
        return {
            "success": True,
            "action": "created_multiple_todos",
            "count": len(created_todos),
            "todos": created_todos,
            "by_priority": by_priority,
            "summary": f"✅ Created {len(created_todos)} tasks: {', '.join(priority_summary)}"
        }

    @staticmethod
    def _find_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> Optional[dict]:
        """Internal helper: find first matching todo"""
        if not todo_id and not title_match:
            return None
        
        for todo in state["todos"]:
            if todo_id and todo["id"] == todo_id:
                return todo
            if title_match and title_match.lower() in todo["title"].lower():
                return todo
        return None

    @staticmethod
    def complete_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> dict:
        """Mark a todo as completed"""
        todo = ToolExecutor._find_todo(state, todo_id, title_match)
        
        if not todo:
            return {
                "success": False,
                "action": "complete_failed",
                "summary": "❌ Task not found"
            }

        if todo["completed"]:
            return {
                "success": True,
                "action": "already_completed",
                "todo": todo,
                "summary": f"ℹ️ Task '{todo['title']}' was already completed"
            }

        todo["completed"] = True
        todo["completed_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "action": "completed_todo",
            "todo": todo,
            "summary": f"✅ Completed: '{todo['title']}'"
        }

    @staticmethod
    def update_todo(
        state: AgentState,
        todo_id: Optional[str] = None,
        title_match: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Update an existing todo"""
        todo = ToolExecutor._find_todo(state, todo_id, title_match)
        
        if not todo:
            return {
                "success": False,
                "action": "update_failed",
                "summary": "❌ Task not found"
            }

        if not updates:
            return {
                "success": False,
                "action": "no_updates",
                "summary": "❌ No updates provided"
            }

        old_title = todo["title"]
        old_values = {k: todo.get(k) for k in updates}
        
        # Apply updates
        for key, value in updates.items():
            if key == "priority" and value.lower() in ["high", "medium", "low"]:
                todo[key] = value.lower()
            elif key != "id" and key != "created_at":  # Prevent modifying immutable fields
                todo[key] = value
        
        todo["updated_at"] = datetime.now().isoformat()

        changes = []
        for key in updates:
            if old_values.get(key) != todo.get(key):
                changes.append(f"{key}: '{old_values.get(key)}' → '{todo.get(key)}'")

        change_summary = ", ".join(changes) if changes else "no changes"
        
        return {
            "success": True,
            "action": "updated_todo",
            "todo": todo,
            "changes": changes,
            "summary": f"✅ Updated '{old_title}': {change_summary}"
        }

    @staticmethod
    def delete_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> dict:
        """Delete a todo"""
        for i, todo in enumerate(state["todos"]):
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                removed = state["todos"].pop(i)
                return {
                    "success": True,
                    "action": "deleted_todo",
                    "summary": f"🗑️ Deleted: '{removed['title']}'"
                }
        
        return {
            "success": False,
            "action": "delete_failed",
            "summary": "❌ Task not found"
        }

    @staticmethod
    def create_calendar_event(
        state: AgentState,
        title: str,
        date: str,
        time: str,
        duration_minutes: int = 60,
        attendees: Optional[List[str]] = None,
        description: str = ""
    ) -> dict:
        """Create a calendar event"""
        if not title or not title.strip():
            return {
                "success": False,
                "action": "create_event_failed",
                "summary": "❌ Event title cannot be empty"
            }
        
        if not date:
            return {
                "success": False,
                "action": "create_event_failed",
                "summary": "❌ Event date is required"
            }
        
        event = {
            "id": str(uuid.uuid4())[:8],
            "title": str(title).strip(),
            "date": date,
            "time": time or "09:00",
            "duration_minutes": duration_minutes,
            "attendees": attendees or [],
            "description": str(description).strip(),
            "created_at": datetime.now().isoformat()
        }
        state["calendar"].append(event)
        state["context"]["last_meeting_id"] = event["id"]

        # Format for display
        try:
            time_obj = datetime.strptime(event["time"], "%H:%M")
            formatted_time = time_obj.strftime("%I:%M %p")
        except:
            formatted_time = event["time"]

        try:
            date_obj = datetime.strptime(event["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")
        except:
            formatted_date = event["date"]

        attendee_str = ""
        if event["attendees"]:
            attendee_str = f" with {', '.join(event['attendees'])}"

        return {
            "success": True,
            "action": "created_calendar_event",
            "event": event,
            "formatted_date": formatted_date,
            "formatted_time": formatted_time,
            "summary": f"📅 Scheduled '{title}' on {formatted_date} at {formatted_time}{attendee_str}"
        }

    @staticmethod
    def update_calendar_event(
        state: AgentState,
        event_id: Optional[str] = None,
        title_match: Optional[str] = None,
        updates: Optional[dict] = None
    ) -> dict:
        """Update a calendar event"""
        # Use last created event if no identifier provided
        if not event_id and not title_match:
            event_id = state["context"].get("last_meeting_id")

        target_event = None
        for event in state["calendar"]:
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                target_event = event
                break
        
        if not target_event:
            return {
                "success": False,
                "action": "update_failed",
                "summary": "❌ Event not found"
            }

        if not updates:
            return {
                "success": False,
                "action": "no_updates",
                "summary": "❌ No updates provided"
            }

        changes = []
        
        # Handle special case: adding attendees
        if "add_attendees" in updates:
            new_attendees = updates.pop("add_attendees")
            if isinstance(new_attendees, list):
                current = target_event.get("attendees", [])
                target_event["attendees"] = list(set(current + new_attendees))
                changes.append(f"Added attendees: {', '.join(new_attendees)}")

        # Apply other updates
        for key, value in updates.items():
            if key != "id" and key != "created_at":
                old = target_event.get(key)
                target_event[key] = value
                changes.append(f"{key}: '{old}' → '{value}'")

        target_event["updated_at"] = datetime.now().isoformat()

        change_summary = "; ".join(changes) if changes else "no changes"
        
        return {
            "success": True,
            "action": "updated_calendar_event",
            "event": target_event,
            "changes": changes,
            "summary": f"✅ Updated '{target_event['title']}': {change_summary}"
        }

    @staticmethod
    def delete_calendar_event(
        state: AgentState,
        event_id: Optional[str] = None,
        title_match: Optional[str] = None
    ) -> dict:
        """Delete a calendar event"""
        for i, event in enumerate(state["calendar"]):
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                removed = state["calendar"].pop(i)
                return {
                    "success": True,
                    "action": "deleted_event",
                    "summary": f"🗑️ Cancelled: '{removed['title']}'"
                }
        
        return {
            "success": False,
            "action": "delete_failed",
            "summary": "❌ Event not found"
        }

    @staticmethod
    def save_file(state: AgentState, filename: str, content: str) -> dict:
        """Save content to a file"""
        if not filename or not filename.strip():
            return {
                "success": False,
                "action": "save_failed",
                "summary": "❌ Filename cannot be empty"
            }
        
        filename = sanitize_filename(filename)
        state["files"][filename] = str(content)
        
        return {
            "success": True,
            "action": "saved_file",
            "filename": filename,
            "size": len(content),
            "summary": f"💾 Saved '{filename}' ({len(content):,} characters)"
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
                "summary": f"📄 Read '{filename}' ({len(content):,} characters)"
            }
        
        return {
            "success": False,
            "action": "read_failed",
            "summary": f"❌ File '{filename}' not found"
        }

    @staticmethod
    def delete_file(state: AgentState, filename: str) -> dict:
        """Delete a file"""
        if filename in state["files"]:
            del state["files"][filename]
            return {
                "success": True,
                "action": "deleted_file",
                "summary": f"🗑️ Deleted '{filename}'"
            }
        
        return {
            "success": False,
            "action": "delete_failed",
            "summary": f"❌ File '{filename}' not found"
        }

    @staticmethod
    def ls(state: AgentState) -> dict:
        """List all saved files"""
        files = list(state["files"].keys())
        
        if not files:
            return {
                "success": True,
                "action": "ls",
                "files": [],
                "summary": "📂 No files saved"
            }
        
        return {
            "success": True,
            "action": "ls",
            "files": files,
            "summary": f"📂 {len(files)} file(s): {', '.join(files)}"
        }

    @staticmethod
    def export_todos_to_file(state: AgentState, filename: str = "my_tasks.txt") -> dict:
        """Export all todos to a formatted file"""
        if not state["todos"]:
            return {
                "success": False,
                "action": "export_failed",
                "summary": "❌ No tasks to export"
            }

        filename = sanitize_filename(filename)
        
        lines = [
            "=" * 70,
            "MY TASKS",
            f"Exported: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "=" * 70,
            ""
        ]

        pending = [t for t in state["todos"] if not t["completed"]]
        completed = [t for t in state["todos"] if t["completed"]]

        def format_section(title: str, tasks: list):
            if not tasks:
                return
            
            lines.append(title)
            lines.append("-" * 70)
            
            for i, task in enumerate(tasks, 1):
                status = "✓" if task["completed"] else "○"
                lines.append(f"{i}. [{status}] {task['title']}")
                
                if task.get("description"):
                    lines.append(f"     ↳ {task['description']}")
                
                details = []
                if task.get("priority"):
                    details.append(f"Priority: {task['priority'].upper()}")
                if task.get("due_date"):
                    details.append(f"Due: {task['due_date']}")
                
                if details:
                    lines.append(f"     {' | '.join(details)}")
                
                lines.append("")

        format_section("PENDING TASKS", pending)
        format_section("COMPLETED TASKS", completed)
        
        lines.append("=" * 70)
        lines.append(f"SUMMARY: {len(pending)} pending | {len(completed)} completed | {len(state['todos'])} total")
        lines.append("=" * 70)

        content = "\n".join(lines)
        state["files"][filename] = content

        return {
            "success": True,
            "action": "exported_todos",
            "filename": filename,
            "total": len(state["todos"]),
            "pending": len(pending),
            "completed": len(completed),
            "summary": f"💾 Exported {len(state['todos'])} tasks to '{filename}' ({len(pending)} pending, {len(completed)} completed)"
        }

    @staticmethod
    def visualize_todos(state: AgentState, chart_type: str = "pie") -> dict:
        """Create a visual chart of todo progress"""
        if not state["todos"]:
            return {
                "success": False,
                "action": "visualize_failed",
                "summary": "❌ No tasks to visualize"
            }

        completed = sum(1 for t in state["todos"] if t["completed"])
        pending = len(state["todos"]) - completed

        chart = {
            "type": chart_type.lower(),
            "title": "Todo Progress Overview",
            "data": {
                "labels": ["Pending", "Completed"],
                "datasets": [{
                    "data": [pending, completed],
                    "backgroundColor": ["#ef4444", "#22c55e"],
                    "borderColor": ["#991b1b", "#166534"],
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "top"},
                    "title": {
                        "display": True,
                        "text": f"Task Progress: {completed}/{len(state['todos'])} Complete"
                    }
                }
            }
        }

        state["visualizations"].append(chart)

        return {
            "success": True,
            "action": "visualized_todos",
            "chart": chart,
            "pending": pending,
            "completed": completed,
            "summary": f"📊 Chart created: {pending} pending, {completed} completed tasks"
        }