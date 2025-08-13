from langchain_community.utilities import SerpAPIWrapper
import os

def get_search_tool():
    return SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))
