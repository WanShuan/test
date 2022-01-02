import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message, send_button_message

load_dotenv()


machine = TocMachine(
    states=["user", "main", "menu",  "pls_ans", "name", "phone", "people", "date", "time",
            "success", "kong_rou", "fish", "bye_good", "chicken"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "main",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "main",
            "conditions": "is_going_to_main_for_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "kong_rou",
            "conditions": "is_going_to_kong_rou",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "fish",
            "conditions": "is_going_to_fish",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "bye_good",
            "conditions": "is_going_to_bye_good",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "chicken",
            "conditions": "is_going_to_chicken",
        },
        {
            "trigger": "advance",
            "source": "main",
            "dest": "pls_ans",
            "conditions": "is_going_to_pls_ans",
        },
        {
            "trigger": "advance",
            "source": "pls_ans",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "pls_ans",
            "dest": "name",
            "conditions": "is_going_to_name",
        },
        {
            "trigger": "advance",
            "source": "name",
            "dest": "pls_ans",
            "conditions": "is_going_to_write_again",
        },
        {
            "trigger": "advance",
            "source": "name",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "name",
            "dest": "phone",
            "conditions": "is_going_to_phone",
        },
        {
            "trigger": "advance",
            "source": "phone",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "phone",
            "dest": "name",
            "conditions": "is_going_to_write_again",
        },
        {
            "trigger": "advance",
            "source": "phone",
            "dest": "people",
            "conditions": "is_going_to_people",
        },
        {
            "trigger": "advance",
            "source": "people",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "people",
            "dest": "phone",
            "conditions": "is_going_to_write_again",
        },
        {
            "trigger": "advance",
            "source": "people",
            "dest": "date",
            "conditions": "is_going_to_date",
        },
        {
            "trigger": "advance",
            "source": "date",
            "dest": "people",
            "conditions": "is_going_to_write_again",
        },
        {
            "trigger": "advance",
            "source": "date",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "date",
            "dest": "time",
            "conditions": "is_going_to_time",
        },
        {
            "trigger": "advance",
            "source": "time",
            "dest": "main",
            "conditions": "is_going_to_main",
        },
        {
            "trigger": "advance",
            "source": "time",
            "dest": "date",
            "conditions": "is_going_to_write_again",
        },
        {
            "trigger": "advance",
            "source": "time",
            "dest": "success",
            "conditions": "is_going_to_success",
        },
        {"trigger": "go_back", "source": ["success"], "dest": "user"},
        {"trigger": "go_to_menu", "source": ["kong_rou", "fish", "bye_good", "chicken"], "dest": "menu"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if ((response == False) and (machine.state == "phone")):
            send_text_message(event.reply_token, "請輸入正確電話號碼")
        elif ((response == False) and (machine.state == "people")):
            send_text_message(event.reply_token, "請輸入正確人數(1~3位)")
        
        elif response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
