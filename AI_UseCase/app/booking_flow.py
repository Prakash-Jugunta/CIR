from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_groq import ChatGroq
from app.config import get_config
from app.tools import tools

app_config = get_config()

SYSTEM_PROMPT = """
You are a helpful AI Booking Assistant for {domain}. 
Your goal is to answer questions using uploaded documents (via the RAG tool) and help users book appointments.

If the user wants to book an appointment, you MUST collect the following information:
1. Customer Name
2. Email
3. Phone
4. Booking/Service Type
5. Preferred Date (must be YYYY-MM-DD format)
6. Preferred Time (must be HH:MM format)

CRITICAL INSTRUCTIONS:
- Detect if the user's intent is a general query or booking. Use the `rag_search_tool` for general questions about the business.
- Extract any known details from their prompt.
- Only ask for the missing fields. Do not repeat questions if they've provided information.
- Use conversational memory to avoid repeats.
- Once you have all 6 fields, you MUST summarize the details to the user and explicitly ask for their confirmation to book.
- ONLY call the `book_appointment_tool` AFTER the user explicitly confirmed the summarized details.
- Friendly error handling is important (e.g. if the user gives a bad date format, tell them "Please enter date as YYYY-MM-DD.")
"""

def get_agent_executor():
    if not app_config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Please configure secrets.")
        
    llm = ChatGroq(api_key=app_config.GROQ_API_KEY, model_name=app_config.MODEL_NAME, temperature=0.0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.format(domain=app_config.BOOKING_DOMAIN)),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
