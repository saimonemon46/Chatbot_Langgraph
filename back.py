from langchain_groq import ChatGroq 

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from dotenv import load_dotenv
import os





# Message Store state

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages()]
    
    
    
## LLm call 
load_dotenv()

llm = ChatGroq(
    temperature=0,
    groq_api_key = os.getenv("Your api key"),
    model_name = "openai/gpt-oss-20b"
)



#  Create the chat Node

def chat_node( state: ChatState):
    
    # User input message
    input = state['messages']
    
    # call llm 
    response = llm.invoke(input)
    
    # Output 
    return { "messages": [response]}



###? Checkpointer
checkpointer = InMemorySaver()


# Create the Graph


graph = StateGraph(ChatState)



# Graph nodes  

graph.add_node('chat_node', chat_node)



# Graph edges

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=checkpointer)




