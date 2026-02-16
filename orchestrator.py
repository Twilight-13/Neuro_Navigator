import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any

from config import Config
from utils import safe_json_parse, extract_tickers_from_goal, get_logger
from memory.vector_store import add_to_vector_store

# Import agents (will be refactored to classes later, for now using existing factories)
from agents.planner import get_planner_agent
from agents.researcher import get_researcher_agent
from agents.finance import get_finance_agent
from agents.execution import get_execution_agent

logger = get_logger("Orchestrator")

class NeuroOrchestrator:
    """
    Orchestrates the multi-agent workflow:
    1. Plan
    2. Parallel Execution (Research, Finance, Execution strategy)
    3. Aggregate Results
    """

    def __init__(self):
        self.config = Config()

    async def run(self, goal: str) -> AsyncGenerator[tuple[str, Any], None]:
        """
        Main entry point to run the agents against a goal.
        Yields (label, data) tuples for real-time UI updates.
        """
        logger.info(f"Starting mission for goal: {goal}")
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
        plan = await self._arun_compat(planner, plan_prompt)
        yield "plan", plan

        if "error" in plan or not isinstance(plan, dict):
            logger.error(f"Planning failed: {plan}")
            return

        # --- 2. Parallel Agents ---
        # We define them here to capture 'plan' from scope
        
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
            return "research", await self._arun_compat(agent, prompt)

        async def run_finance():
            agent = get_finance_agent()
            tickers = extract_tickers_from_goal(goal)

            # --- Case 1: Stocks/Crypto ---
            if tickers:
                return "market", agent.get_multiple_prices(tickers)

            # --- Case 2: Trip budgeting ---
            destination = plan.get("destination", "Unknown")
            duration_str = plan.get("duration", "0")
            # Simple digit extraction
            digits = re.findall(r"\d+", str(duration_str))
            duration = int(digits[0]) if digits else 0

            # --- API Prices ---
            def safe_call(func, fallback_msg):
                try:
                    value = func
                    return value if value not in [None, "N/A", {}] else fallback_msg
                except Exception as e:
                    logger.warning(f"API call failed: {e}")
                    return f"{fallback_msg} (Error: {e})"

            # Note: Hardcoded dates/cities for demo purposes in original logic
            # In a real app, these should be extracted from the plan
            api_prices = {
                "flight": safe_call(agent.get_flight_price("NYC", "LON", "2025-09-01"),
                                    "Flight price unavailable"),
                "hotel": safe_call(agent.get_hotel_price(destination, "2025-09-01", "2025-09-07"),
                                   f"Hotel price unavailable for {destination}"),
                "daily_costs": safe_call(agent.get_city_cost(destination),
                                         f"City costs unavailable for {destination}"),
                # We assume conversion from USD to INR for now as in original
                "currency_conversion": safe_call(agent.convert_currency(100, "USD", "INR"),
                                                 "Currency conversion unavailable")
            }

            # --- Compute Budget ---
            total_budget = 0.0
            try:
                # Flight
                f_price = api_prices["flight"]
                if isinstance(f_price, (int, float)) or (isinstance(f_price, str) and f_price.replace('.', '').isdigit()):
                     total_budget += float(f_price)

                # Hotel
                h_price = api_prices["hotel"]
                if isinstance(h_price, (int, float)) or (isinstance(h_price, str) and h_price.replace('.', '').isdigit()):
                    total_budget += float(h_price) * max(duration, 1)

                # Daily
                daily = api_prices["daily_costs"]
                if isinstance(daily, dict):
                    meal = daily.get("meal", 0)
                    transport = daily.get("transport", 0)
                    if isinstance(meal, (int, float)) and isinstance(transport, (int, float)):
                        total_budget += (meal + transport) * max(duration, 1)
            except Exception as e:
                logger.error(f"Budget calculation error: {e}")

            # User budget parse
            user_budget_match = re.search(r'\$(\d+)', goal)
            user_budget = int(user_budget_match.group(1)) if user_budget_match else 0
            
            remaining = "N/A"
            if user_budget > 0:
                remaining = user_budget - total_budget

            result = {
                "daily_budget": [{"day": f"Day {i+1}", "cost": (total_budget / max(duration, 1))} for i in range(duration)],
                "total_budget": round(total_budget, 2) if total_budget else "N/A",
                "remaining_balance": remaining,
                "api_prices": api_prices,
                "sources": ["Amadeus API", "Booking.com API", "Numbeo API", "Yahoo Finance"]
            }
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
            raw_result = await self._arun_compat(agent, prompt)
            return "execution", safe_json_parse(raw_result)

        # Run concurrent tasks
        tasks = [
            asyncio.create_task(run_research()),
            asyncio.create_task(run_finance()),
            asyncio.create_task(run_execution()),
        ]

        for finished_task in asyncio.as_completed(tasks):
            try:
                label, result = await finished_task
                yield label, result
            except Exception as e:
                logger.error(f"Task failed: {e}")
                yield "error", str(e)

    async def _arun_compat(self, agent, prompt: str) -> Any:
        """Helper to run agents compatible with different LangChain versions."""
        try:
            if hasattr(agent, "arun"):
                out = await agent.arun(prompt)
            elif hasattr(agent, "ainvoke"):
                out = await agent.ainvoke(prompt)
                if hasattr(out, 'content'): # Chat result
                    out = out.content
            elif hasattr(agent, "run"):
                loop = asyncio.get_running_loop()
                out = await loop.run_in_executor(None, lambda: agent.run(prompt))
            else:
                raise TypeError(f"Unsupported agent type: {type(agent)}")
            
            return safe_json_parse(out)
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"error": str(e)}
