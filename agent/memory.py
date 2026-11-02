from agent.prompt import build_system_prompt
from agent.loop import run_agent


class Conversation:
    def __init__(self):
        # The system prompt is always the first message and never dropped.
        self.messages = [{"role": "system", "content": build_system_prompt()}]

    def ask(self, user_message):
        """Add the user's message, run the agent, keep the updated history."""
        self.messages.append({"role": "user", "content": user_message})
        answer, self.messages = run_agent(self.messages)
        return answer
