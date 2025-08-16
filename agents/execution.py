from langchain_community.llms import Ollama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_execution_agent():
    """Agent that simulates execution with structured JSON itinerary."""
    llm = Ollama(model="mistral", temperature=0)

    schemas = [
        ResponseSchema(name="itinerary", description="List of objects with day and activities")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "You are an execution planner. "
            "Generate a realistic day-by-day itinerary for this plan.\n\n"
            "Return only valid JSON.\n\n"
            "Plan:\n{plan}\n\n"
            "{format_instructions}"
        ),
        input_variables=["plan"],
        partial_variables={"format_instructions": format_instructions}
    )

    return LLMChain(llm=llm, prompt=prompt, output_parser=output_parser)
