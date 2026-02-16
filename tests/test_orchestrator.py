import unittest
import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import MagicMock, patch
from orchestrator import NeuroOrchestrator

class TestOrchestrator(unittest.IsolatedAsyncioTestCase):

    @patch("orchestrator.get_planner_agent")
    @patch("orchestrator.get_researcher_agent")
    @patch("orchestrator.get_finance_agent")
    @patch("orchestrator.get_execution_agent")
    async def test_run_flow(self, mock_exec, mock_fin, mock_res, mock_plan):
        # Setup Mocks
        mock_plan.return_value.run.return_value = '{"destination": "Tokyo", "duration": "5 days", "steps": ["Visit Tokyo Tower"]}'
        # Note: _arun_compat handles sync agents by running in executor if they don't have ainvoke/arun
        # We'll mock 'run' which is the fallback
        
        # Planner
        planner_instance = MagicMock()
        planner_instance.run.return_value = '{"destination": "Tokyo", "duration": "5 days", "steps": ["Visit Tokyo Tower"]}'
        mock_plan.return_value = planner_instance

        # Researcher
        res_instance = MagicMock()
        res_instance.run.return_value = '{"insights": ["Tokyo is big"], "sources": ["wiki"]}'
        mock_res.return_value = res_instance

        # Finance
        fin_instance = MagicMock()
        # Mocking finance tool methods called inside the async function
        fin_instance.get_flight_price.return_value = 1000
        fin_instance.get_hotel_price.return_value = 500
        fin_instance.get_city_cost.return_value = {"meal": 20, "transport": 10}
        fin_instance.convert_currency.return_value = 83000
        mock_fin.return_value = fin_instance

        # Execution
        exec_instance = MagicMock()
        exec_instance.run.return_value = '{"itinerary": [{"day": "Day 1", "activities": ["Tokyo Tower"]}]}'
        mock_exec.return_value = exec_instance

        # Run Orchestrator
        orch = NeuroOrchestrator()
        results = {}
        async for label, data in orch.run("Plan a trip to Tokyo"):
            results[label] = data

        # Assertions
        self.assertIn("plan", results)
        self.assertEqual(results["plan"]["destination"], "Tokyo")
        
        self.assertIn("research", results)
        self.assertIn("budget", results)
        self.assertIn("execution", results)
        
        # Check budget calculation
        # Flight 1000 + Hotel 500*5 + Daily (30)*5 = 1000 + 2500 + 150 = 3650
        self.assertEqual(results["budget"]["total_budget"], 3650.0)

if __name__ == '__main__':
    unittest.main()
