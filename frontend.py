import streamlit as st
from Chatbot_backend import workflow
from langchain_core.messages import HumanMessage,AIMessage
from uuid import uuid4

st.title('Your Daily Help : ChatBot')

l=[]

if "thread_id" not in st.session_state:
    first_id = str(uuid4())
    st.session_state.thread_id = first_id
    st.session_state.threads= [first_id]
    st.session_state.all_messages = {st.session_state.thread_id: []}

# Sidebar
with st.sidebar:
    if st.button("New Chat"):
        new_id = str(uuid4())
        st.session_state.thread_id = new_id
        st.session_state.threads.append(new_id)
        st.session_state.all_messages[new_id] = []  # clear chat for new thread
        st.rerun()

    st.title("History")
    for t in st.session_state.threads:
        if st.button(t[:8] + "...",key=t):  # show short ID
            st.session_state.thread_id = t
            st.rerun()


# ✅ Always get messages for current thread
current_thread = st.session_state.thread_id
current_messages = st.session_state.all_messages[current_thread]

conf = {
    "configurable": {
        "thread_id": current_thread
    }
}

# ✅ Display all previous messages
for message in current_messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)


user_input= st.chat_input("Type Here")
if user_input:
    st.session_state.all_messages[current_thread].append(HumanMessage(content=user_input))
    with st.chat_message("User"):
        st.write(user_input)

    with st.chat_message("Assistant"):
        ai_response=workflow.invoke({"messages":[HumanMessage(user_input)]},config=conf)["messages"][-1]
        
        st.write(ai_response.content)
        st.session_state.all_messages[current_thread].append(ai_response)

