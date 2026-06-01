# ==========================================================
# Standard Library Imports
# ==========================================================

import asyncio
# FastAPI runs on an async event loop.
# asyncio helps us execute blocking code without freezing
# the entire API server.

from concurrent.futures import ThreadPoolExecutor
# Creates a pool of worker threads.
# We will run LangGraph's blocking operations in these
# threads so FastAPI remains responsive.


# ==========================================================
# FastAPI Imports
# ==========================================================

from fastapi import FastAPI, HTTPException
# FastAPI = web framework
# HTTPException = return proper HTTP errors

from fastapi.responses import StreamingResponse
# Used for token-by-token streaming responses


# ==========================================================
# LangGraph / LangChain Imports
# ==========================================================

from langchain_core.messages import HumanMessage
# LangGraph expects messages as HumanMessage,
# AIMessage, SystemMessage objects instead of raw strings.


# ==========================================================
# Application Imports
# ==========================================================

from Chatbot_backend import workflow
# Your compiled LangGraph workflow

from schemas import ChatRequest, ChatResponse
# Pydantic request/response models


# ==========================================================
# Create FastAPI Application
# ==========================================================

app = FastAPI(
    title="LangGraph Blog Agent"
)

# Generates:
# http://localhost:8000/docs
# http://localhost:8000/redoc


# ==========================================================
# Thread Pool
# ==========================================================

executor = ThreadPoolExecutor(max_workers=2)

"""
Why do we need this?

workflow.invoke() is synchronous.

When OpenAI is called:
    User --> FastAPI --> OpenAI

the current thread waits for OpenAI.

Without a thread pool:

    Request 1 arrives
    FastAPI waits 5 sec
    Other requests are blocked

With a thread pool:

    Event Loop
        |
        +---- Worker Thread
                  |
                  +--- workflow.invoke()

The event loop remains free to handle
other incoming requests.

For production:

max_workers=10
max_workers=20

is usually more realistic.
"""


# ==========================================================
# STREAMING CHAT ENDPOINT
# ==========================================================

@app.post("/chat")
async def chat_stream(req: ChatRequest):

    """
    Streams response token-by-token.

    Instead of:

        "Hello Deepak"

    User receives:

        H
        He
        Hel
        Hell
        Hello

    progressively.
    """

    config = {
        "configurable": {
            "thread_id": req.thread_id
        }
    }

    # ------------------------------------------------------
    # Async Generator
    # ------------------------------------------------------

    async def token_generator():

        loop = asyncio.get_event_loop()

        # --------------------------------------------------
        # Worker Function
        # --------------------------------------------------

        def _stream():

            return list(
                workflow.stream(
                    {
                        "messages": [
                            HumanMessage(
                                content=req.message
                            )
                        ]
                    },
                    config=config,
                    stream_mode="messages"
                )
            )

        """
        stream_mode="messages"

        Returns:

        [
            (AIMessageChunk("H"), metadata),
            (AIMessageChunk("e"), metadata),
            (AIMessageChunk("l"), metadata)
        ]
        """

        chunks = await loop.run_in_executor(
            executor,
            _stream
        )

        # --------------------------------------------------
        # Yield Tokens
        # --------------------------------------------------

        for chunk, metadata in chunks:

            if (
                hasattr(chunk, "content")
                and chunk.content
            ):
                yield chunk.content

        """
        StreamingResponse consumes yielded chunks.

        Browser receives:

        H
        e
        l
        l
        o
        """

    return StreamingResponse(
        token_generator(),
        media_type="text/plain"
    )


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")
def health():

    """
    Used by:

    Kubernetes
    Docker
    Load Balancers
    Monitoring Tools

    to verify API is alive.
    """

    return {
        "status": "ok"
    }