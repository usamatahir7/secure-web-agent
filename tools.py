from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

def search_web(query: str, max_results: int = 3) -> list[dict]:
    """
    Searches DuckDuckGo for the given query and returns a list of results 
    containing the title, URL, and a brief snippet.
    """
    try:
        # Initialize the DuckDuckGo search client
        results = DDGS().text(query, max_results=max_results, region = "us-en")
        
        formatted_results = []
        for res in results:
            formatted_results.append({
                "title": res.get("title", ""),
                "url": res.get("href", ""),
                "snippet": res.get("body", "") # The brief text preview
            })
            
        return formatted_results
        
    except Exception as e:
        
        return [{"error": f"Search failed: {str(e)}"}]

def fetch_page(url: str, max_chars: int = 5000) -> str:
    """
    Fetches a web page and heavily sanitizes the content to prevent 
    indirect prompt injections. Returns clean, truncated plaintext.
    """
    try:
        # Guardrail 1: Timeout to prevent the agent from hanging indefinitely
        headers = {"User-Agent": "ResearchAgent/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Guardrail 2: Strip dangerous and noisy tags
        # Attackers may hide malicious instructions in scripts, CSS, and image alt-texts
        for tag in soup(['script', 'style', 'iframe', 'img', 'noscript', 'head']):
            tag.decompose()

        # Extract only the visible human-readable text
        text = soup.get_text(separator=' ', strip=True)

        # Guardrail 3: Context Truncation
        # Prevents an attacker from overflowing the LLM's memory with a massive payload
        if len(text) > max_chars:
            text = text[:max_chars] + "... [Content Truncated for Safety]"

        return text

    except Exception as e:
        return f"Error fetching {url}: {str(e)}"


# The Tools Schema
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for current events, news, or specific information not available in the pretraining data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought_process": {
                        "type": "string",
                        "description": "Briefly explain why you need to search the web and what you are looking for."
                    },
                    "query": {
                        "type": "string",
                        "description": "The exact search query."
                    }
                },
                "required": ["thought_process", "query"] 
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Fetches the text content of a specific webpage URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought_process": {
                        "type": "string",
                        "description": "Explain why you chose this specific URL over the others."
                    },
                    "url": {
                        "type": "string",
                        "description": "The exact URL to fetch."
                    }
                },
                "required": ["thought_process", "url"] 
            }
        }
    }
]