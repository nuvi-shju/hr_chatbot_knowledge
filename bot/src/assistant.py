from openai import OpenAI
from . import settings


class AssistantClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.ASSISTANT_ID

    def ask(self, question: str) -> str:
        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status in ["completed", "failed", "cancelled"]:
                break

        if run_status.status != "completed":
            raise RuntimeError(f"Run failed with status: {run_status.status}")

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]

        return last_message.content[0].text.value

    def send_message(self, user_input: str) -> str:
        # Create a new thread
        thread = self.client.beta.threads.create()

        # Post a message to the thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Run the assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
        )

        # Wait for completion
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status in ["completed", "failed", "cancelled"]:
                break

        if run_status.status != "completed":
            raise RuntimeError(f"Run failed with status: {run_status.status}")

        # Fetch messages
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]

        return last_message.content[0].text.value