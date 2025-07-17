# app/simple_groq.py

import os
from groq import Groq
from agno.models.base import Model
from agno.agent import RunResponse, Message
from typing import Any, Iterator

class SimpleGroqModel(Model):
    """
    A flat Model wrapper sending a single-user message
    to Groq's chat API and returning the assistant content.
    Implements all abstract Model methods so Agno can instantiate it.
    """
    def __init__(self, model_id: str):
        super().__init__(id=model_id)
        # Initialize Groq client with API key; model specified per-call :contentReference[oaicite:0]{index=0}
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # --- Synchronous interface ---

    def invoke(self, prompt: str, **kwargs: Any) -> RunResponse:
        """
        Non-streaming call: sends one user message, returns full RunResponse.
        """
        return self._call_groq(prompt, stream=False)

    def invoke_stream(self, prompt: str, **kwargs: Any) -> Iterator[RunResponse]:
        """
        Streaming call: yields one RunResponse per chunk.
        """
        chat_iter = self.client.chat.completions.create(
            model=self.id,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in chat_iter:
            content = chunk.choices[0].message.content
            yield RunResponse(
                content=content,
                content_type="str",
                messages=[Message(role="assistant", content=content)]
            )

    # --- Asynchronous interface ---

    async def ainvoke(self, prompt: str, **kwargs: Any) -> RunResponse:
        return self.invoke(prompt, **kwargs)

    async def ainvoke_stream(self, prompt: str, **kwargs: Any) -> Iterator[RunResponse]:
        for resp in self.invoke_stream(prompt, **kwargs):
            yield resp

    # --- Internal helper & response parsing ---

    def _call_groq(self, prompt: str, stream: bool) -> RunResponse:
        chat = self.client.chat.completions.create(
            model=self.id,
            messages=[{"role": "user", "content": prompt}],
            stream=stream,
        )
        if stream:
            raise ValueError("stream=True not supported in _call_groq")
        content = chat.choices[0].message.content
        return RunResponse(
            content=content,
            content_type="str",
            messages=[Message(role="assistant", content=content)]
        )

    def parse_provider_response(self, response: Any) -> RunResponse:
        content = response.choices[0].message.content
        return RunResponse(
            content=content,
            content_type="str",
            messages=[Message(role="assistant", content=content)]
        )

    def parse_provider_response_delta(self, delta: Any) -> RunResponse:
        content = delta.choices[0].message.content
        return RunResponse(
            content=content,
            content_type="str",
            messages=[Message(role="assistant", content=content)]
        )
