from slack_bolt import App
from .assistant import AssistantClient

assistant = AssistantClient()

def register_routes(app: App):
    @app.event("app_mention")
    def on_mention(body, say):
        text = body.get("event", {}).get("text", "")
        # 멘션 토큰 제거
        import re
        q = re.sub(r"<@[^>]+>", "", text).strip()
        if not q:
            say("무엇을 도와드릴까요? 예) 연차 반차 규정 알려줘")
            return
        say("_질문 이해 중…_")
        try:
            answer = assistant.ask(q)
            say(answer)
        except Exception as e:
            say(f"에러가 발생했습니다: {e}")

    @app.command("/누비봇")
    def on_slash(ack, client, command):
        ack()
        q = (command.get("text") or "").strip()
        if not q:
            client.chat_postMessage(
                channel=command["channel_id"],
                thread_ts=command.get("thread_ts") or command["ts"],
                text="사용법: `/누비봇 질문내용`"
            )
            return
        try:
            answer = assistant.ask(q)
            client.chat_postMessage(
                channel=command["channel_id"],
                thread_ts=command.get("thread_ts") or command["ts"],
                text=answer
            )
        except Exception as e:
            client.chat_postMessage(
                channel=command["channel_id"],
                thread_ts=command.get("thread_ts") or command["ts"],
                text=f"에러가 발생했습니다: {e}"
            )
