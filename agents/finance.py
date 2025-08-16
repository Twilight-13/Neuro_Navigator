from langchain_community.llms import Ollama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_finance_agent():
    """Agent that produces structured budget estimates (JSON only)."""
    llm = Ollama(model="mistral", temperature=0)

    schemas = [
        ResponseSchema(name="daily_budget", description="List of objects with day, category, and cost"),
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

    return LLMChain(llm=llm, prompt=prompt, output_parser=output_parser)
