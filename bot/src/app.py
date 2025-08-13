from flask import Flask, request, make_response
from slack_bolt import App as SlackBoltApp
from slack_bolt.adapter.flask import SlackRequestHandler
from . import settings
from .router import register_routes

# Slack Bolt 앱 생성
bolt_app = SlackBoltApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
)

# 핸들러 등록
register_routes(bolt_app)

# Flask 래핑 (Cloud Run 등에서 사용)
app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)

@flask_app.post("/slack/events")
def slack_events():
    # --- Slack URL verification fast-path ---
    data = request.get_json(silent=True) or {}
    if data.get("type") == "url_verification":
        # Slack은 plain text 또는 {"challenge": "..."} 모두 허용
        return make_response(data.get("challenge", ""), 200, {"Content-Type": "text/plain"})
     # 나머지는 Bolt에 위임
    return handler.handle(request)

@flask_app.get("/healthz")
def healthz():
    return make_response("ok", 200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.PORT)
