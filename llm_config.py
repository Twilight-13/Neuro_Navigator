from langchain_community.chat_models import ChatOllama
from langchain_community.chat_models import ChatHuggingFace
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Toggle here
USE_OLLAMA = True  # True = use local Ollama, False = use HuggingFace

def get_fast_llm():
    """Returns a fast LLM for researcher, finance, and execution agents."""
    if USE_OLLAMA:
        return ChatOllama(model="mistral", temperature=0.2)
    else:
        model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        return ChatHuggingFace(model=model, tokenizer=tokenizer)
