import streamlit as st
from back import chatbot
from langchain_core.messages import HumanMessage\
    
# For checkpointer need Cinfigurable key
CONFIG = {'configurable' : {'thread_id' : 'thread-1'}}
    
# Load the message hisstory  if not present create a empty one
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


# load all message
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        


user_input = st.chat_input("Type Here ")

if user_input:
    
    # store the message in message history
    st.session_state['message_history'].append({'role':'user', 'content': user_input})
    # Display user's message
    with st.chat_message("user"):
        st.text(user_input)
    
    ##? Get chatbot response( non streaming way)
    
    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    
    # # Display AI's message
    # ai_message = response['messages'][-1].content
    
    # ## Add Ai message to message history 
    # st.session_state['message_history'].append({'role':'assistant', 'content': ai_message})
    # # Display user's message
    # with st.chat_message("assistant"):
    #     st.text(ai_message)


    ###? Show the ai message in streaming wa
    
    with st.chat_message('assistant'):
        
        ai_message = st.write_stream(
            
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {"messages" : [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )
        
    # Add Ai message to message hitory
    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})