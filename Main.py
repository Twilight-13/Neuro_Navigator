from agents.planner import get_planner_agent
from agents.researcher import get_researcher_agent
from agents.finance import get_finance_agent
from agents.execution import get_execution_agent
from memory.vector_store import add_to_vector_store
import asyncio
import json
import re
import ast # Import the 'ast' module
from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException

load_dotenv()


def extract_json(text: str):
    """
    Extracts a Python dictionary literal from a string and returns it as a dictionary.
    This is more robust than json.loads because it can handle single quotes.
    """
    try:
        # Find the dictionary-like string using regex
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            # Use ast.literal_eval to safely parse the string into a Python dict
            return ast.literal_eval(match.group(0))
    except (ValueError, SyntaxError, TypeError):
        # If parsing fails, return the original text for raw display
        pass
    return {"raw_text": text}


async def _arun_compat(agent, prompt: str):
    """Runs an agent asynchronously, handling different invocation methods."""
    try:
        # Standard way to run LangChain agents
        if hasattr(agent, "arun"):
            out = await agent.arun(prompt)
        # Newer invocation standard
        elif hasattr(agent, "ainvoke"):
            out = await agent.ainvoke(prompt)
        # Fallback for synchronous agents
        elif hasattr(agent, "run"):
            loop = asyncio.get_running_loop()
            out = await loop.run_in_executor(None, lambda: agent.run(prompt))
        else:
            raise TypeError(f"Unsupported agent type: {type(agent)}")
    except OutputParserException as e:
        # Handle cases where the AI output doesn't match the expected format
        return {"error": f"Output parsing error: {str(e)}"}
    except Exception as e:
        # Catch other potential errors during agent execution
        return {"error": f"Agent execution error: {str(e)}"}

    # If the agent already returned a dictionary, use it directly.
    # Otherwise, parse the string output.
    if isinstance(out, dict):
        return out
    return extract_json(out)


async def run_neuro_navigator(goal: str):
    """
    Async generator that runs the AI agent pipeline.
    Each agent is prompted to return a strict JSON object.
    """
    print(f"Received Goal: {goal}")
    add_to_vector_store(goal)

    # --- 1. Planner Agent ---
    planner = get_planner_agent()
    plan_prompt = f"""
    Create a travel plan for the user's goal.
    Respond with JSON in this exact schema:
    {{
      "destination": "string",
      "duration": "string",
      "steps": ["step1", "step2", ...]
    }}

    Goal: {goal}
    """
    plan = await _arun_compat(planner, plan_prompt)
    yield "plan", plan

    # If the initial plan fails, stop the process.
    if "error" in plan or not isinstance(plan, dict):
        return

    # --- 2. Parallel Agents (Research, Finance, Execution) ---
    async def run_research():
        agent = get_researcher_agent()
        prompt = f"""
        Based on the plan, provide research insights and sources.
        Respond with JSON in this exact schema:
        {{
          "insights": ["insight1", "insight2", ...],
          "sources": ["url1", "url2", ...]
        }}

        Plan: {plan}
        """
        return "research", await _arun_compat(agent, prompt)

    async def run_finance(user_goal: str):
        agent = get_finance_agent()
        # --- UPDATED PROMPT ---
        # The AI is now only responsible for creating the daily breakdown.
        prompt = f"""
        Based on the provided travel plan, create a daily cost breakdown for the entire duration of the trip.

        Respond with JSON in this exact schema. Do not add any narration.
        {{
          "daily_budget": [
            {{"day": "Day 1", "cost": <cost>}},
            {{"day": "Day 2", "cost": <cost>}}
          ]
        }}

        Plan: {plan}
        """
        result = await _arun_compat(agent, prompt)

        # --- NEW: Perform calculations in Python for accuracy ---
        if isinstance(result, dict) and "daily_budget" in result and result["daily_budget"]:
            try:
                # Calculate total_budget by summing costs from the generated list
                total_budget = sum(item.get('cost', 0) for item in result['daily_budget'])
                result['total_budget'] = total_budget

                # Extract the user's overall budget from their goal string
                user_budget_match = re.search(r'\$(\d+)', user_goal)
                user_budget = int(user_budget_match.group(1)) if user_budget_match else 0

                # Calculate the remaining balance
                remaining_balance = user_budget - total_budget
                result['remaining_balance'] = remaining_balance
            except (TypeError, ValueError) as e:
                # Fallback in case of unexpected data types
                print(f"Error during budget calculation: {e}")
                result['total_budget'] = "N/A"
                result['remaining_balance'] = "N/A"

        return "budget", result


    async def run_execution():
        agent = get_execution_agent()
        prompt = f"""
        Based on the plan, create a structured itinerary.
        Respond with JSON in this exact schema:
        {{
          "itinerary": [
            {{
              "day": "Day 1",
              "activities": ["activity1", "activity2"]
            }},
            {{
              "day": "Day 2",
              "activities": ["activity1", "activity2"]
            }}
          ]
        }}

        Plan: {plan}
        """
        return "execution", await _arun_compat(agent, prompt)

    # Create and run tasks concurrently
    tasks = [
        asyncio.create_task(run_research()),
        asyncio.create_task(run_finance(goal)), # Pass the user's goal to the finance agent
        asyncio.create_task(run_execution()),
    ]

    for finished_task in asyncio.as_completed(tasks):
        label, result = await finished_task
        yield label, result


# Command-line interface for quick testing
if __name__ == "__main__":
    async def test():
        test_goal = "Plan a 5-day eco-friendly trip to Korea within $1,000"
        print(f"--- Running Test with Goal: {test_goal} ---")
        async for label, content in run_neuro_navigator(test_goal):
            print(f"\n[{label.upper()}]\n{json.dumps(content, indent=2)}")
        print("\n--- Test Complete ---")

    asyncio.run(test())
