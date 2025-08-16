import os
from langchain_community.llms import Ollama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_researcher_agent():
    """Agent that gathers structured research details (JSON only)."""
    llm = Ollama(model="mistral", temperature=0)

    # --- JSON schema ---
    schemas = [
        ResponseSchema(name="insights", description="List of 3–5 research insights as short bullets"),
        ResponseSchema(name="sources", description="List of sources in [title + link] format")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "You are a research assistant. "
            "Use available knowledge and tools (search, weather, memory). "
            "Answer strictly in JSON format.\n\n"
            "Goal/Plan:\n{plan}\n\n"
            "{format_instructions}"
        ),
        input_variables=["plan"],
        partial_variables={"format_instructions": format_instructions}
    )

    # ✅ Return chain, not dict
    return LLMChain(llm=llm, prompt=prompt, output_parser=output_parser)
