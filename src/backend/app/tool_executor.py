from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

from .utils import AgentState


class ToolExecutor:
    """
    Pure state-mutating tools.
    No delegation, no LLM calls, no orchestration.
    Designed to work reliably even when the LLM uses slightly different parameter names
    (thanks to normalization in reasoning_node).
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
        todo = {
            "id": str(uuid.uuid4())[:8],
            "title": str(title).strip(),
            "description": str(description).strip(),
            "priority": str(priority).lower(),
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        state["todos"].append(todo)
        return {
            "success": True,
            "action": "created_todo",
            "todo": todo,
            "summary": f"Created task: '{todo['title']}' (Priority: {todo['priority']})"
        }

    @staticmethod
    def create_multiple_todos(state: AgentState, todos_list: List[Dict[str, Any]]) -> dict:
        """Create multiple todos at once – great for planning"""
        if not todos_list:
            return {"success": False, "action": "create_multiple_failed", "summary": "Empty task list"}

        created_count = 0
        by_priority = {"high": 0, "medium": 0, "low": 0}
        created_titles = []

        for item in todos_list:
            title = str(item.get("title") or item.get("task") or "Untitled").strip()
            if not title:
                continue
            priority = str(item.get("priority", "medium")).lower()
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
            created_count += 1
            by_priority[priority] += 1
            created_titles.append(title)

        parts = [f"{by_priority[p]} {p}" for p in by_priority if by_priority[p] > 0]
        return {
            "success": True,
            "action": "created_multiple_todos",
            "count": created_count,
            "titles": created_titles,
            "summary": f"Created {created_count} tasks: {', '.join(parts) or 'all medium'}"
        }

    @staticmethod
    def _find_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> Optional[dict]:
        """Internal helper: find first matching todo"""
        for todo in state["todos"]:
            if todo_id and todo["id"] == todo_id:
                return todo
            if title_match and title_match.lower() in todo["title"].lower():
                return todo
        return None

    @staticmethod
    def complete_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> dict:
        todo = ToolExecutor._find_todo(state, todo_id, title_match)
        if not todo:
            return {"success": False, "action": "complete_failed", "summary": "Task not found"}

        if todo["completed"]:
            return {"success": True, "action": "already_completed", "summary": f"'{todo['title']}' already completed"}

        todo["completed"] = True
        return {
            "success": True,
            "action": "completed_todo",
            "todo": todo,
            "summary": f"Completed: '{todo['title']}'"
        }

    @staticmethod
    def update_todo(
        state: AgentState,
        todo_id: Optional[str] = None,
        title_match: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None
    ) -> dict:
        todo = ToolExecutor._find_todo(state, todo_id, title_match)
        if not todo:
            return {"success": False, "action": "update_failed", "summary": "Task not found"}

        if not updates:
            return {"success": False, "action": "no_updates", "summary": "Nothing to update"}

        old_title = todo["title"]
        old_values = {k: todo.get(k) for k in updates}
        todo.update(updates)

        changes = [
            f"{k}: '{old_values[k]}' → '{todo[k]}'"
            for k in updates
            if old_values[k] != todo.get(k)
        ]

        return {
            "success": True,
            "action": "updated_todo",
            "todo": todo,
            "changes": changes,
            "summary": f"Updated '{old_title}' → '{todo['title']}' ({len(changes)} changes)"
        }

    @staticmethod
    def delete_todo(state: AgentState, todo_id: Optional[str] = None, title_match: Optional[str] = None) -> dict:
        for i, todo in enumerate(state["todos"]):
            if (todo_id and todo["id"] == todo_id) or \
               (title_match and title_match.lower() in todo["title"].lower()):
                removed = state["todos"].pop(i)
                return {
                    "success": True,
                    "action": "deleted_todo",
                    "summary": f"Deleted: '{removed['title']}'"
                }
        return {"success": False, "action": "delete_failed", "summary": "Task not found"}

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
        event = {
            "id": str(uuid.uuid4())[:8],
            "title": str(title).strip(),
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "attendees": attendees or [],
            "description": str(description).strip(),
            "created_at": datetime.now().isoformat()
        }
        state["calendar"].append(event)
        state["context"]["last_meeting_id"] = event["id"]

        # Friendly formatting
        try:
            formatted_time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")
        except:
            formatted_time = time
        try:
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
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
    def update_calendar_event(
        state: AgentState,
        event_id: Optional[str] = None,
        title_match: Optional[str] = None,
        updates: Optional[dict] = None
    ) -> dict:
        if not event_id and not title_match:
            event_id = state["context"].get("last_meeting_id")

        for event in state["calendar"]:
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                changes = []
                if updates:
                    if "add_attendees" in updates:
                        new = updates.pop("add_attendees")
                        current = event.get("attendees", [])
                        event["attendees"] = list(set(current + new))
                        changes.append(f"Added attendees: {', '.join(new)}")

                    for k, v in updates.items():
                        old = event.get(k)
                        event[k] = v
                        changes.append(f"{k}: '{old}' → '{v}'")

                return {
                    "success": True,
                    "action": "updated_calendar_event",
                    "event": event,
                    "changes": changes,
                    "summary": f"Updated '{event['title']}': {'; '.join(changes) or 'no changes'}"
                }
        return {"success": False, "action": "update_failed", "summary": "Event not found"}

    @staticmethod
    def delete_calendar_event(state: AgentState, event_id: Optional[str] = None, title_match: Optional[str] = None) -> dict:
        for i, event in enumerate(state["calendar"]):
            if (event_id and event["id"] == event_id) or \
               (title_match and title_match.lower() in event["title"].lower()):
                removed = state["calendar"].pop(i)
                return {"success": True, "action": "deleted_event", "summary": f"Cancelled: '{removed['title']}'"}
        return {"success": False, "action": "delete_failed", "summary": "Event not found"}

    @staticmethod
    def save_file(state: AgentState, filename: str, content: str) -> dict:
        state["files"][filename] = str(content)
        return {
            "success": True,
            "action": "saved_file",
            "filename": filename,
            "size": len(content),
            "summary": f"Saved '{filename}' ({len(content)} chars)"
        }

    @staticmethod
    def read_file(state: AgentState, filename: str) -> dict:
        if filename in state["files"]:
            return {
                "success": True,
                "action": "read_file",
                "content": state["files"][filename],
                "summary": f"Read '{filename}'"
            }
        return {"success": False, "action": "read_failed", "summary": "File not found"}

    @staticmethod
    def delete_file(state: AgentState, filename: str) -> dict:
        if filename in state["files"]:
            del state["files"][filename]
            return {"success": True, "action": "deleted_file", "summary": f"Deleted '{filename}'"}
        return {"success": False, "action": "delete_failed", "summary": "File not found"}

    @staticmethod
    def ls(state: AgentState) -> dict:
        files = list(state["files"].keys())
        return {
            "success": True,
            "action": "ls",
            "files": files,
            "summary": f"{len(files)} file(s): {', '.join(files) or 'none'}"
        }

    @staticmethod
    def export_todos_to_file(state: AgentState, filename: str = "my_tasks.txt") -> dict:
        if not state["todos"]:
            return {"success": False, "action": "export_failed", "summary": "No tasks to export"}

        lines = [
            "=" * 60,
            "MY TASKS",
            f"Exported: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "=" * 60,
            ""
        ]

        pending = [t for t in state["todos"] if not t["completed"]]
        completed = [t for t in state["todos"] if t["completed"]]

        def add_section(name: str, tasks: list):
            if tasks:
                lines.extend([name, "-" * 40])
                for i, t in enumerate(tasks, 1):
                    status = "Completed" if t["completed"] else "Pending"
                    lines.append(f"{i}. {status} {t['title']}")
                    if desc := t.get("description"):
                        lines.append(f"     ↳ {desc}")
                    lines.append(f"     Priority: {t['priority'].capitalize()} | Due: {t.get('due_date', 'none')}")
                    lines.append("")

        add_section("PENDING TASKS", pending)
        add_section("COMPLETED TASKS", completed)
        lines.append(f"Summary: {len(pending)} pending | {len(completed)} completed | {len(state['todos'])} total")

        content = "\n".join(lines)
        state["files"][filename] = content

        return {
            "success": True,
            "action": "exported_todos",
            "filename": filename,
            "summary": f"Exported all {len(state['todos'])} tasks to '{filename}'"
        }

    @staticmethod
    def visualize_todos(state: AgentState, chart_type: str = "pie") -> dict:
        """Create a visual chart of todo progress"""
        completed = sum(1 for t in state["todos"] if t["completed"])
        pending = len(state["todos"]) - completed

        if pending + completed == 0:
            return {"success": False, "summary": "No tasks to visualize"}

        chart = {
            "type": chart_type.lower(),
            "title": "Todo Progress",
            "data": {
                "labels": ["Pending", "Completed"],
                "datasets": [{
                    "data": [pending, completed],
                    "backgroundColor": ["#ef4444", "#22c55e"],
                    "borderColor": ["#991b1b", "#166534"],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "top"},
                    "title": {"display": True, "text": "My Todo Progress"}
                }
            }
        }

        state["visualizations"].append(chart)

        return {
            "success": True,
            "action": "visualized_todos",
            "chart": chart,
            "summary": f"Chart ready: {pending} pending, {completed} completed"
        }