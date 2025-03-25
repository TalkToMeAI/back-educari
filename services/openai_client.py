import os
from openai import OpenAI
from typing import List, Dict


class OpenAIChatClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        system_prompt: str = "You're a helpful assistant.",
    ) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        completion = self.client.chat.completions.create(
            model=model,
            messages=full_messages,
        )

        return completion.choices[0].message.content
