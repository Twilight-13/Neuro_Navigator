import logging
import json
import re
import ast
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NeuroNavigator")

def get_logger(name: str):
    """Get a named logger."""
    return logging.getLogger(name)

def safe_json_parse(text: str) -> Dict[str, Any]:
    """
    Robustly parse JSON from text, handling common LLM output issues 
    like markdown code blocks, single quotes, or trailing commas.
    """
    if isinstance(text, dict):
        return text
        
    # Remove markdown code blocks
    cleaned_text = re.sub(r"```json\s*", "", text)
    cleaned_text = re.sub(r"```\s*", "", cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    # Extract JSON object if embedded in text
    match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
    if match:
        cleaned_text = match.group(0)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        try:
            # Try to fix single quotes
            fixed = cleaned_text.replace("'", '"')
            # Fix trailing commas
            fixed = re.sub(r",\s*}", "}", fixed)
            fixed = re.sub(r",\s*]", "]", fixed)
            return json.loads(fixed)
        except Exception:
            try:
                # Last resort: ast.literal_eval for python dict syntax
                return ast.literal_eval(cleaned_text)
            except Exception:
                logger.error(f"Failed to parse JSON: {text[:100]}...")
                return {"raw_text": text}

def extract_tickers_from_goal(goal: str) -> List[str]:
    """Extract known stock/crypto tickers from a goal string."""
    ticker_map = {
        "apple": "AAPL",
        "tesla": "TSLA",
        "google": "GOOG",
        "microsoft": "MSFT",
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "btc": "BTC-USD",
        "eth": "ETH-USD",
        "nvidia": "NVDA",
        "meta": "META",
        "amazon": "AMZN"
    }
    
    tickers = []
    goal_lower = goal.lower()
    for name, symbol in ticker_map.items():
        if name in goal_lower:
            tickers.append(symbol)
    
    # Also look for uppercase tickers (3-5 chars)
    # This is a basic regex, might match non-tickers, but helps for unknowns
    potential_tickers = re.findall(r'\b[A-Z]{3,5}\b', goal)
    # Filter common words if necessary, for now we just add them if not already found
    for pt in potential_tickers:
        if pt not in tickers and pt not in ["AND", "FOR", "THE", "WITH"]:
             tickers.append(pt)
             
    return list(set(tickers))
