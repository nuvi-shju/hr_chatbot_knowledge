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
        say(":hourglass_flowing_sand: 신중하게 답변하기 위해 고민 중이에요… 조금만 기다려 주세요!", thread_ts=thread_ts)
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
                done, not_done = wait([future], timeout=2, return_when=FIRST_COMPLETED)

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
        client.chat_postMessage(
            channel=command["channel_id"],
            text=":hourglass_flowing_sand: 신중하게 답변하기 위해 고민 중이에요… 조금만 기다려 주세요!",
            thread_ts=posted["ts"]
        )
        thread_ts = posted["ts"]

        # GPT 응답 생성 (타임아웃 보호)
        import threading

        answer_container = {}

        def fetch_answer():
            try:
                answer = assistant.send_message(q)
                answer_container["text"] = answer
            except Exception as e:
                answer_container["error"] = str(e)

        t = threading.Thread(target=fetch_answer)
        t.start()
        t.join(timeout=30)

        if "text" in answer_container:
            client.chat_postMessage(
                channel=command["channel_id"],
                text=answer_container["text"],
                thread_ts=thread_ts
            )
        elif "error" in answer_container:
            client.chat_postMessage(
                channel=command["channel_id"],
                text=f"답변 중 오류가 발생했어요: {answer_container['error']}",
                thread_ts=thread_ts
            )
        else:
            client.chat_postMessage(
                channel=command["channel_id"],
                text="GPT 응답이 예상보다 오래 걸리고 있어요. 잠시 후 다시 시도해 주세요 🙇",
                thread_ts=thread_ts
            )
