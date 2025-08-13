from openai import OpenAI
from . import settings
import time  # Add at the top of the file if not already present


class AssistantClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.ASSISTANT_ID

    def ask(self, question: str) -> str:
        """
        Handle app mention-based questions via OpenAI Assistant API.
        """

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

        # Wait for run completion with timeout
        max_attempts = 60
        for attempt in range(max_attempts):
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status in ["completed", "failed", "cancelled"]:
                break
            time.sleep(1)
        else:
            raise TimeoutError("Assistant response timed out.")

        if run_status.status != "completed":
            raise RuntimeError(f"Run failed with status: {run_status.status}")

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]

        return last_message.content[0].text.value