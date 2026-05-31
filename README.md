# Chatbot

A conversational AI chatbot built with LangGraph and OpenAI, featuring persistent in-memory conversation history and a polite, explanatory assistant persona.

## Features

- **Stateful conversations** — uses LangGraph's `InMemorySaver` to maintain message history across turns
- **Custom assistant persona** — warm, enthusiastic, and explanatory responses with step-by-step breakdowns
- **LangGraph workflow** — clean state machine graph with a single generation node

## Project Structure

```
Chatbot/
└── Assistance/
    ├── Chatbot_backend.py   # Core backend: LangGraph graph, state, and model logic
    ├── chatbot.ipynb        # Jupyter notebook for interactive usage
    └── .env                 # Environment variables (API keys)
```

## Prerequisites

- Python 3.11+
- An OpenAI API key

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd Chatbot/Assistance
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv myenv
   myenv\Scripts\activate   # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install langchain-openai langgraph python-dotenv pydantic
   ```

4. **Configure environment variables**

   Create a `.env` file in the `Assistance/` directory:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### As a module

```python
from Chatbot_backend import workflow
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "session-1"}}

response = workflow.invoke(
    {"messages": [HumanMessage(content="Hello!")]},
    config=config
)
print(response["messages"][-1].content)
```

### In Jupyter

Open `chatbot.ipynb` and run the cells to chat interactively.

## How It Works

1. User input is added to the `BlogState` message list.
2. The `model_generation` node prepends a system prompt that enforces the polite assistant persona, then calls the OpenAI model.
3. The response is appended to the message history via LangGraph's `add_messages` reducer.
4. `InMemorySaver` persists the conversation for the duration of the process, keyed by `thread_id`.

## Tech Stack

| Library | Purpose |
|---|---|
| `langchain-openai` | OpenAI chat model integration |
| `langgraph` | Stateful graph-based workflow |
| `python-dotenv` | Environment variable management |
| `pydantic` | State schema validation |
