import streamlit as st
from back import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# -------- Utility Functions -------- #

def thread_id_generator():
    return str(uuid.uuid4())

def add_thread_session(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = thread_id_generator()
    st.session_state['thread_id'] = thread_id
    add_thread_session(thread_id)
    st.session_state['message_history'] = []
    st.session_state['thread_titles'][thread_id] = "New Chat"

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', []) if state else []

# -------- Session State Setup -------- #

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = thread_id_generator()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}

add_thread_session(st.session_state['thread_id'])

# -------- Sidebar -------- #

st.sidebar.title('💬 Ask Meee.....')

if st.sidebar.button('🆕 New Chat'):
    reset_chat()

st.sidebar.header("🧵 Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    title = st.session_state['thread_titles'].get(thread_id, thread_id[:8])
    if st.sidebar.button(title):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id) or []
        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})
        st.session_state['message_history'] = temp_messages

# -------- Main Chat Display -------- #

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input("Type Here.....")

if user_input:
    # Add the user message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    # If this is the first message in the thread, use it as title
    thread_id = st.session_state['thread_id']
    if st.session_state['thread_titles'].get(thread_id, "New Chat") == "New Chat":
        # take first few words as title
        title = user_input.strip().split('\n')[0][:50]
        st.session_state['thread_titles'][thread_id] = title if title else "New Chat"

    # Show user message
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Stream AI response
    with st.chat_message('assistant'):
        placeholder = st.empty()
        full_response = ""
        for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        ):
            if isinstance(message_chunk, AIMessage):
                full_response += message_chunk.content
                placeholder.markdown(full_response)
        st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})
