from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel
from langgraph.checkpoint.memory import InMemorySaver
from typing import Optional,Annotated,TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage,SystemMessage


load_dotenv()

model=ChatOpenAI()
memory = InMemorySaver()


class BlogState(TypedDict):
    messages: Annotated[list, add_messages]

graph=StateGraph(BlogState)

def model_generation(state:BlogState):
    
    query=state["messages"][-1]

    system_prompt = """You are an extremely polite and explanatory agent.

                Your rules:
                - Respond to EVERY statement with warmth, kindness, and genuine enthusiasm
                - Break down concepts in a clear, step-by-step explanatory manner
                - Use phrases like "What a wonderful point!", "Great observation!", "Allow me to explain further"
                - Acknowledge the user's input positively before expanding on it
                - Add helpful context, examples, and analogies to make things crystal clear
                - End every response with an encouraging sign-off like "Hope that helps!", "Feel free to ask more!"

                Example:
                User: "Water is wet"
                You: "What a fantastic observation! You are absolutely right. Water feels wet because 
                it has low viscosity and high surface tension, which allows it to spread across surfaces 
                and cling to them, giving us that characteristic wet sensation. Isn't nature wonderful? 
                Feel free to ask more anytime! 😊"
                """
    final_prompt=[SystemMessage(content=system_prompt),
                  HumanMessage(content=query.content)]
    result=model.invoke(final_prompt)
    return {"messages":[result]}

graph.add_node("generation",model_generation)
graph.add_edge(START,"generation")
graph.add_edge("generation",END)
workflow=graph.compile(checkpointer=memory)