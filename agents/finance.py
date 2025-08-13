import os

from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq


def get_finance_agent():
    """Agent that estimates and optimizes budget."""
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),model="llama3-70b-8192", temperature=0)

    budget_tool = Tool(
        name="BudgetCalculator",
        func=lambda details: f"Estimated total cost for '{details}' is ${(len(details) * 5) + 200}.",
        description="Calculates a very rough budget estimate for the plan."
    )

    return initialize_agent(
        [budget_tool],
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
