"""The agent loop: talk to the model, run any tools it asks for, feed the
results back, and repeat until the model gives a final text answer."""

import json
import os
from groq import Groq
from dotenv import load_dotenv

from agent.prompt import build_system_prompt
from agent.tools import TOOL_SCHEMAS, TOOL_FUNCTIONS

load_dotenv()  # reads GROQ_API_KEY from the .env file

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-120b"
MAX_STEPS = 5  # safety cap so the loop can never run forever


def run_agent(messages):
    """Run the tool-calling loop.

    `messages` is the full conversation (system prompt + history + the new
    user message). Returns the assistant's final text answer and the
    updated messages list."""
    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message)  # keep the assistant turn in the history

        # No tool calls → the model produced its final answer.
        if not message.tool_calls:
            return message.content, messages

        # Otherwise, run each tool the model asked for and feed results back.
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
                result = TOOL_FUNCTIONS[name](**args)
            except Exception as e:
                result = {"error": str(e)}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False, default=str),
            })

    # Ran out of steps without a final answer.
    return "Desculpe, não consegui concluir a consulta agora.", messages
