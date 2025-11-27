from langchain_groq import ChatGroq 
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph.message import add_messages 


from typing import Annotated, TypedDict

from dotenv import load_dotenv
import os
import sqlite3



# Message Store state
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages()]
    
    
    
## LLm call 
load_dotenv()

llm = ChatGroq(
    temperature=0,
    groq_api_key = os.getenv("GROQ_API_KEY"),
    model_name = "openai/gpt-oss-20b"
)



#  Create the chat Node

def chat_node( state: ChatState):
    # User input message
    messages = state['messages']
    # call llm 
    response = llm.invoke(messages)
    # Output 
    return { "messages": [response]}


## Store to sqlite
conn = sqlite3.connect(database = "chatbot.db", check_same_thread=False)


### Checkpointer
checkpointer = SqliteSaver(conn = conn)
# checkpointer = InMemorySaver()


# Create the Graph
graph = StateGraph(ChatState)
# Graph nodes  
graph.add_node('chat_node', chat_node)

# Graph edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=checkpointer)


# Retrieve chat history even if you restart the application
def retrieve_all_threads():
    all_threads = {}
    for checkpoint in checkpointer.list(None):
        try:
            thread_id = checkpoint.config['configurable']['thread_id']
            # Use title if available, fallback to first 8 chars of thread_id
            title = checkpoint.config['configurable'].get('title', thread_id[:8])
            all_threads[thread_id] = {'title': title}
        except (KeyError, AttributeError):
            continue
    
    return all_threads




        
