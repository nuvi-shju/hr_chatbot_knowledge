from slack_bolt import App
from .assistant import AssistantClient
import concurrent.futures
from concurrent.futures import wait, FIRST_COMPLETED

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
        thread_ts = body.get("event", {}).get("ts")
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(assistant.ask, q)
                done, not_done = wait([future], timeout=5, return_when=FIRST_COMPLETED)

                if future in done:
                    answer = future.result()
                else:
                    say("_⏳ 신중하게 답변하기 위해 고민 중이에요… 조금만 기다려 주세요!_", thread_ts=thread_ts)
                    answer = future.result()

                say(answer, thread_ts=thread_ts)
        except Exception as e:
            say(f"에러가 발생했습니다: {e}", thread_ts=thread_ts)

    @app.command("/누비봇")
    def on_slash(ack, command, client, logger):
        q = command.get("text", "").strip()
        if not q:
            client.chat_postMessage(
                channel=command["channel_id"],
                text="무엇을 도와드릴까요? 예) 연차 반차 규정 알려줘"
            )
            return

        thread_ts = command.get("thread_ts") or command.get("message_ts") or command.get("ts")

        # 질문 내용을 먼저 스레드의 시작점으로 기록
        posted = client.chat_postMessage(
            channel=command["channel_id"],
            text=f"<@{command['user_id']}> 님의 질문: {q}"
        )
        thread_ts = posted["ts"]

        # GPT 응답 생성
        answer = assistant.send_message(q)

        client.chat_postMessage(
            channel=command["channel_id"],
            text=answer,
            thread_ts=thread_ts
        )
