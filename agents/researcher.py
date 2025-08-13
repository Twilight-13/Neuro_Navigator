import os

from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq
from tools.search_tool import get_search_tool
from tools.weather_tool import get_weather_tool
from memory.vector_store import get_vector_store

def get_researcher_agent():
    """Agent that gathers in-depth details using tools."""
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),model="llama3-70b-8192", temperature=0)

    search_tool = Tool(
        name="Search",
        func=get_search_tool().run,
        description="Search online for detailed info."
    )

    weather_tool = Tool(
        name="WeatherLookup",
        func=lambda loc: str(get_weather_tool()(loc)),
        description="Look up weather for a location."
    )

    memory_store = get_vector_store()

    memory_tool = Tool(
        name="MemorySearch",
        func=lambda query: str(memory_store.similarity_search(query, k=2)),
        description="Search stored user preferences or past data."
    )

    tools = [search_tool, weather_tool, memory_tool]

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
