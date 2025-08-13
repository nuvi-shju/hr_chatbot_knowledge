from slack_bolt import App
from .assistant import AssistantClient
import concurrent.futures
from concurrent.futures import wait, FIRST_COMPLETED

assistant = AssistantClient()

def register_routes(app: App):
    @app.event("app_mention")
    def on_mention(body, say):
        text = body.get("event", {}).get("text", "")
        import re
        channel_type = body.get("event", {}).get("channel_type")

        if channel_type == "im" and not text.startswith("<@"):
            q = text.strip()
            if not q:
                say("무엇을 도와드릴까요? 예) 연차 반차 규정 알려줘")
                return
        else:
            q = re.sub(r"<@[^>]+>", "", text).strip()
            if not q:
                say("무엇을 도와드릴까요? 예) 연차 반차 규정 알려줘")
                return

        if channel_type == "im":
            say(":hourglass_flowing_sand: 신중하게 답변하기 위해 고민 중이에요… 조금만 기다려 주세요!")
        else:
            thread_ts = body.get("event", {}).get("ts")
            say(":hourglass_flowing_sand: 신중하게 답변하기 위해 고민 중이에요… 조금만 기다려 주세요!", thread_ts=thread_ts)

        thread_ts = None if channel_type == "im" else body.get("event", {}).get("ts")

        event_ts = body.get("event", {}).get("event_ts")
        client_msg_id = body.get("event", {}).get("client_msg_id")
        cache_key = f"{event_ts}_{client_msg_id}"
        if hasattr(app, "seen_messages") and cache_key in app.seen_messages:
            return
        if not hasattr(app, "seen_messages"):
            app.seen_messages = set()
        app.seen_messages.add(cache_key)

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(assistant.ask, q)
                done, _ = wait([future], timeout=60, return_when=FIRST_COMPLETED)
                if future in done:
                    answer = future.result()
                    say(answer, thread_ts=thread_ts)
                else:
                    say(":warning: GPT 응답이 지연되고 있어요. 다시 시도해 주세요!", thread_ts=thread_ts)
        except Exception as e:
            say(f"에러가 발생했습니다: {e}", thread_ts=thread_ts)
