from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import Type

class LsInput(BaseModel):
    # No arguments needed for listing files
    pass

class Ls(BaseTool):
    name: str = "ls"
    description: str = "Lists all virtual files"
    args_schema: Type[BaseModel] = LsInput

    def _run(self):
        # Placeholder logic
        return ["todo_1.txt", "todo_2.txt", "todo_3.txt"]

ls = Ls()