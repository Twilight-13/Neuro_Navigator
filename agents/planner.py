from langchain.agents import initialize_agent, Tool, AgentType
from tools.search_tool import get_search_tool
from config import Config

def get_planner_agent():
    """Agent that breaks user goals into actionable steps."""
    llm = Config.get_llm(provider="groq") # Planner works best with Groq/Llama3

    search_tool = Tool(
        name="Search",
        func=get_search_tool().run,
        description="Use this to look up general information online."
    )

    tools = [search_tool]

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
