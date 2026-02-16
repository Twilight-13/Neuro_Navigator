from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tools.finance_tool import FinanceTool
import json
from config import Config

class FinanceAgent:
    def __init__(self):
        self.tool = FinanceTool()

        # Budget planner setup
        llm = Config.get_llm()
        schemas = [
            ResponseSchema(name="daily_budget", description="List of objects with day, category, and cost in USD"),
            ResponseSchema(name="total_budget", description="Total estimated cost in USD"),
            ResponseSchema(name="remaining_balance", description="Remaining after planned budget in USD")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(schemas)
        format_instructions = output_parser.get_format_instructions()

        prompt = PromptTemplate(
            template=(
                "You are a financial planner. Estimate the budget for this plan.\n\n"
                "Return only valid JSON.\n\n"
                "Plan:\n{plan}\n\n"
                "{format_instructions}"
            ),
            input_variables=["plan"],
            partial_variables={"format_instructions": format_instructions}
        )
        self.budget_chain = LLMChain(llm=llm, prompt=prompt, output_parser=output_parser)

    # --- Budget Estimation with Currency Conversion ---
    def estimate_budget(self, plan: str, user_currency="USD"):
        raw_result = self.budget_chain.run(plan)

        # Parse JSON safely
        try:
            budget = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        except Exception:
            return {"raw_text": raw_result}

        # Add conversion USD -> user_currency
        def convert_value(val):
            if isinstance(val, (int, float)):
                if user_currency != "USD":
                    converted = self.tool.convert_currency(val, "USD", user_currency)
                    return {"USD": val, user_currency: converted}
                else:
                    return {"USD": val}
            return val

        if "total_budget" in budget:
            budget["total_budget"] = convert_value(budget["total_budget"])

        if "remaining_balance" in budget:
            budget["remaining_balance"] = convert_value(budget["remaining_balance"])

        if "daily_budget" in budget and isinstance(budget["daily_budget"], list):
            for entry in budget["daily_budget"]:
                if "cost" in entry:
                    entry["cost"] = convert_value(entry["cost"])

        return budget

    # Proxy to FinanceTool
    def get_stock_price(self, symbol: str):
        return self.tool.get_stock_price(symbol)

    def get_multiple_prices(self, symbols: list):
        return self.tool.get_multiple_prices(symbols)

    def get_flight_price(self, origin, dest, departure, return_date=None):
        return self.tool.get_flight_price(origin, dest, departure, return_date)

    def get_hotel_price(self, city, checkin, checkout):
        return self.tool.get_hotel_price(city, checkin, checkout)

    def get_city_cost(self, city):
        return self.tool.get_city_cost(city)

    def convert_currency(self, amount, from_currency="USD", to_currency="INR"):
        return self.tool.convert_currency(amount, from_currency, to_currency)


def get_finance_agent():
    return FinanceAgent()
