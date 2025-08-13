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
    def on_slash(ack, command, say, logger):
        ack(response_type="in_channel")

        try:
            q = command["text"]
            answer = assistant.ask(q)

            thread_ts = command.get("thread_ts")
            if thread_ts:
                say(text=answer, thread_ts=thread_ts)
            else:
                say(text=answer)

        except Exception as e:
            logger.error(f"Failed to run listener function (error: {e})")
            say(text=f"{{{e}}} 오류가 발생해 */누비봇*에 실패했습니다.")
