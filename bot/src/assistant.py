import time
from typing import Optional
from openai import OpenAI
from . import settings

class AssistantClient:
    """
    OpenAI Assistants v2 래퍼.
    - 기존에 생성한 Assistant(파일검색 연결)를 사용.
    - 질문을 받아 Thread + Run 실행 후 최종 답변 텍스트를 반환.
    """
    def __init__(self):
        if not settings.OPENAI_API_KEY or not settings.ASSISTANT_ID:
            raise RuntimeError("OPENAI_API_KEY 또는 ASSISTANT_ID가 설정되지 않았습니다.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.ASSISTANT_ID

    def ask(self, question: str, timeout_s: int = 90) -> str:
        # 1) 스레드 생성
        thread = self.client.beta.threads.create()

        # 2) 사용자 메시지 추가
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # 3) Run 실행
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
            temperature=settings.TEMPERATURE,
            top_p=settings.TOP_P
        )

        # 4) 폴링
        start = time.time()
        status = "queued"
        while True:
            r = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            status = r.status
            if status in ("completed", "failed", "requires_action", "cancelled", "expired"):
                break
            if time.time() - start > timeout_s:
                return "응답 시간 초과(Timeout). 잠시 후 다시 시도해 주세요."
            time.sleep(0.8)

        if status != "completed":
            return f"Assistant 실행 실패: {status}"

        # 5) 최신 메시지(assistant 출력) 읽기
        msgs = self.client.beta.threads.messages.list(thread_id=thread.id)
        for m in msgs.data:
            if m.role == "assistant" and m.content:
                # 텍스트 조각을 모아 합치기
                parts = []
                for c in m.content:
                    if c.type == "text":
                        parts.append(c.text.value)
                if parts:
                    return "\n".join(parts).strip()

        return "출력된 답변이 없습니다."
