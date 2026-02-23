import os
import json
from openai import OpenAI
from datetime import datetime
from tools import search_web, fetch_page, AGENT_TOOLS_SCHEMA

client = OpenAI() 

def run_research_agent(user_query: str, max_steps: int = 7):
    """The main loop that connects OpenAI to our local tools."""

    today_date = datetime.now().strftime("%A, %B %d, %Y")
    
    
    system_instruction = (
        f"You are a helpful research assistant. Today's date is {today_date}.\n"
        f"Follow these steps strictly:\n"
        f"1. Use 'search_web' to find information.\n"
        f"2. Read the snippets. Reason about which URL looks the most credible to answer the user's goal. **You MUST explain your reasoning in your text response before calling the fetch_page tool.**\n"
        f"3. Use 'fetch_page' to read the full content of the chosen URL.\n"
        f"4. If you have enough context, summarize your findings. If not, fetch another URL."
    )
    
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_query}
    ]

    print("\n" + "="*50)
    print(f"USER GOAL: {user_query}")
    print("="*50 + "\n")

    step = 0
    while step < max_steps:
        print(f"\n{'='*20} STEP {step + 1} {'='*20}")
        print("Agent is thinking...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=AGENT_TOOLS_SCHEMA,
            tool_choice="auto" 
        )
        
        assistant_message = response.choices[0].message
        messages.append(assistant_message)
        
        # Check which specific tool OpenAI decided to call
        if assistant_message.tool_calls:
            
            # --- PRINT THE AGENT'S INTERNAL REASONING ---
            if assistant_message.content:
                print(f"\nAGENT'S THOUGHTS:\n{assistant_message.content.strip()}\n")
        
            for tool_call in assistant_message.tool_calls:
                
                # --- HANDLE SEARCH WEB ---
                if tool_call.function.name == "search_web":
                    args = json.loads(tool_call.function.arguments)
                    
                    # Grab the thoughts from the JSON!
                    thoughts = args.get("thought_process", "No thoughts provided.")
                    print(f"\nAGENT'S THOUGHTS:\n{thoughts}\n")
                    
                    search_query = args.get("query")
                    print(f"ACTION: Agent triggered 'search_web' with keyword: '{search_query}'")
                    
                    search_results = search_web(search_query)
                    
                    # Print the exact data the agent is receiving
                    print(f"OBSERVATION: search_web returned {len(search_results)} results:")
                    for i, res in enumerate(search_results):
                        if "error" in res:
                            print(f"   [!] Error: {res['error']}")
                        else:
                            print(f"   [{i+1}] Title: {res.get('title')}")
                            print(f"       URL: {res.get('url')}")
                            # Truncate snippet for clean terminal output
                            snippet_preview = res.get('snippet', '')[:100].replace('\n', ' ')
                            print(f"       Snippet: {snippet_preview}...\n")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(search_results)
                    })
                
                # --- HANDLE FETCH PAGE ---
                elif tool_call.function.name == "fetch_page":
                    args = json.loads(tool_call.function.arguments)
                    
                    # Grab the thoughts from the JSON!
                    thoughts = args.get("thought_process", "No thoughts provided.")
                    print(f"\nAGENT'S THOUGHTS:\n{thoughts}\n")
                    
                    url_to_fetch = args.get("url")
                    print(f"ACTION: Agent triggered 'fetch_page' for URL: '{url_to_fetch}'")

                    page_content = fetch_page(url_to_fetch)
                    
                    # Print the first 500 characters of the scraped content
                    preview = page_content[:500].replace('\n', ' ')
                    print(f"OBSERVATION: fetch_page successful. First 500 characters scraped:\n")
                    print(f"   \"{preview}... [content truncated for display]\"\n")
                    print(f"   (Total length: {len(page_content)} characters passed to agent memory)")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"page_text": page_content})
                    })
        else:
            print(f"\n{'='*20} FINAL OUTPUT {'='*20}")
            print("Agent has decided it has enough information to finish.")
            print("\n--- Summary ---\n")
            print(assistant_message.content)
            break 
            
        step += 1

if __name__ == "__main__":
    test_query = "How to tie shoe laces?"
    run_research_agent(test_query)