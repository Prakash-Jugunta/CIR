from langchain_core.messages import HumanMessage, AIMessage
from app.booking_flow import get_agent_executor

def process_message(user_input: str, chat_history: list) -> str:
    """Takes user text and a list of {"role": "...", "content": "..."} dicts. Returns string response."""
    
    # Restrict to last 20 messages (approx 10 turns) per rules
    memory_messages = chat_history[-20:]
    
    langchain_history = []
    for msg in memory_messages:
        if msg["role"] == "user":
            langchain_history.append(HumanMessage(content=msg["content"]))
        else:
            langchain_history.append(AIMessage(content=msg["content"]))
            
    try:
        executor = get_agent_executor()
        response = executor.invoke({
            "input": user_input,
            "chat_history": langchain_history
        })
        return response["output"]
    except ValueError as ve:
        return f"Configuration Error: {ve}"
    except Exception as e:
        return f"An unexpected error occurred processing your request: {str(e)}"
