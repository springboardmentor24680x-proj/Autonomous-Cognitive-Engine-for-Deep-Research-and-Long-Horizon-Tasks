from llm_factory import make_llm
from vfs_tools import vfs
from langchain_core.messages import AIMessage

class ResearchAgent:
    @staticmethod
    def invoke(state):
        llm = make_llm()
        response = llm.invoke(state["messages"])

        if response and response.content.strip():
            vfs.write_file(
                "research.txt",
                state["messages"][-1].content,
                response.content
            )

        state["messages"].append(
            AIMessage(content=response.content)
        )
        return state
