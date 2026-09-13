class ConversationMemory:
    """
    Simple in-memory conversation history.

    Stores user questions and assistant responses
    so the agent can understand follow-up questions.
    """

    def __init__(self):
        self.messages = []

    def add_user_message(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, message):
        self.messages.append({
            "role": "assistant",
            "content": message
        })

    def get_history(self):
        return self.messages

    def get_formatted_history(self):
        if not self.messages:
            return "No previous conversation."

        history = []

        for message in self.messages:
            role = message["role"].title()
            content = message["content"]

            history.append(
                f"{role}: {content}"
            )

        return "\n".join(history)

    def clear(self):
        self.messages = []
