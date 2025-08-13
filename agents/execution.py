import os

from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq
from tools.booking_tool import get_booking_tool

def get_execution_agent():
    """Agent that simulates final execution of the plan."""
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),model="llama3-70b-8192", temperature=0)

    booking_tool = Tool(
        name="BookingService",
        func=lambda details: get_booking_tool()(details),
        description="Simulates booking flights/hotels/activities."
    )

    return initialize_agent(
        [booking_tool],
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
