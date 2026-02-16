import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration management."""
    
    # Environment
    ENV = os.getenv("ENV", "development")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
    NUMBEO_API_KEY = os.getenv("NUMBEO_API_KEY")

    # LLM Settings
    DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq, openai, ollama, huggingface
    MODEL_NAME = os.getenv("LLM_MODEL", "llama3-70b-8192")
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    @staticmethod
    def validate_keys():
        """Check for critical API keys."""
        missing = []
        if Config.DEFAULT_LLM_PROVIDER == "groq" and not Config.GROQ_API_KEY:
            missing.append("GROQ_API_KEY")
        if Config.DEFAULT_LLM_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if missing:
            print(f"WARNING: Missing API keys: {', '.join(missing)}")
            return False
        return True

    @staticmethod
    def get_llm(provider: Optional[str] = None):
        """Factory method to get LLM instance based on provider."""
        provider = provider or Config.DEFAULT_LLM_PROVIDER
        
        try:
            if provider == "groq":
                from langchain_groq import ChatGroq
                return ChatGroq(
                    groq_api_key=Config.GROQ_API_KEY,
                    model_name=Config.MODEL_NAME,
                    temperature=Config.TEMPERATURE
                )
            
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    model_name=os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
                    temperature=Config.TEMPERATURE
                )
                
            elif provider == "ollama":
                from langchain_community.chat_models import ChatOllama
                return ChatOllama(
                    model=os.getenv("OLLAMA_MODEL", "mistral"),
                    temperature=Config.TEMPERATURE
                )
                
            elif provider == "huggingface":
                from langchain_huggingface import ChatHuggingFace
                from langchain.llms import HuggingFaceHub
                return HuggingFaceHub(
                    repo_id=os.getenv("HF_REPO_ID", "mistralai/Mistral-7B-Instruct-v0.2"),
                    huggingfacehub_api_token=Config.HUGGINGFACEHUB_API_TOKEN,
                    model_kwargs={"temperature": Config.TEMPERATURE, "max_length": 512}
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except ImportError as e:
            raise ImportError(f"Missing dependency for provider {provider}. Error: {e}")
        except Exception as e:
            raise Exception(f"Failed to initialize LLM: {e}")
