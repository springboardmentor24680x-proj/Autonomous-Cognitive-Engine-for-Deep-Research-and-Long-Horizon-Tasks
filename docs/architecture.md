# Architecture Overview
The system uses a **Hierarchical Multi-Agent** pattern.

- **Supervisor**: The main brain that uses `write_todos` to plan.
- **Sub-Agents**: Specialized workers like the `Search Agent`.
- **VFS (Virtual File System)**: A state-based dictionary that mimics a hard drive for the agent to save context.