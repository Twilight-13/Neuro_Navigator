import os
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq
from tools.search_tool import get_search_tool

def get_planner_agent():
    """Agent that breaks user goals into actionable steps."""
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="llama3-70b-8192",
        temperature=0
    )

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
