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

    @app.command("/kb")
    def on_slash(ack, respond, command):
        ack()
        q = (command.get("text") or "").strip()
        if not q:
            respond("사용법: `/kb 질문내용`")
            return
        try:
            answer = assistant.ask(q)
            respond(answer)
        except Exception as e:
            respond(f"에러가 발생했습니다: {e}")
