from agents.planner import get_planner_agent
from agents.researcher import get_researcher_agent
from agents.finance import get_finance_agent
from agents.execution import get_execution_agent
from memory.vector_store import add_to_vector_store
import os
from dotenv import load_dotenv

load_dotenv()

def run_neuro_navigator(goal):
    """Runs all agents in sequence and returns their outputs."""
    print("User Goal:", goal)

    # Store goal in FAISS for memory
    add_to_vector_store(goal)

    # Planning
    planner = get_planner_agent()
    plan = planner.run(f"Break this goal into steps: {goal}")
    print("\n--- PLAN ---\n", plan)

    # Research
    researcher = get_researcher_agent()
    research = researcher.run(f"Do research for: {plan}")
    print("\n--- RESEARCH ---\n", research)

    #Finance
    finance = get_finance_agent()
    budget = finance.run(f"Estimate costs for: {plan}")
    print("\n--- BUDGET ---\n", budget)

    #Execution
    execution = get_execution_agent()
    result = execution.run(f"Simulate execution for: {plan}")
    print("\n--- FINAL OUTPUT ---\n", result)

    # Return everything  Streamlit
    return plan, research, budget, result


if __name__ == "__main__":
    run_neuro_navigator("Plan a 5-day eco-friendly trip to Japan within $1,200")
