from transitions.extensions import GraphMachine

import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, ImageSendMessage

from utils import send_text_message
load_dotenv()
import message_template

name = ""
phone = ""
people = 0
date = ""
time = ""
mode = 0

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_main(self, event):
        text = event.message.text
        return text == "主選單"

    def is_going_to_menu(self, event):
        text = event.message.text
        mode = 0
        return text == "美味菜單"

    def is_going_to_main_for_menu(self, event):
        text = event.message.text
        mode = 0
        return text == "主選單"

    def is_going_to_kong_rou(self, event):
        text = event.message.text
        mode = 2
        return text == "控肉飯"

    def is_going_to_fish(self, event):
        text = event.message.text
        mode = 2
        return text == "虱目魚飯"

    def is_going_to_bye_good(self, event):
        text = event.message.text
        mode = 3
        return text == "排骨飯"

    def is_going_to_chicken(self, event):
        text = event.message.text
        mode = 4
        return text == "雞腿飯"

    def is_going_to_pls_ans(self, event):
        text = event.message.text
        return text == "我要訂位"
    
    def is_going_to_name(self, event):
        text = event.message.text
        return text == "開始填寫"

    def is_going_to_write_again(self, event):
        text = event.message.text
        return text == "重新填寫"

    def is_going_to_phone(self, event):
        text = event.message.text
        name = text
        return True

    def is_going_to_people(self, event):
        phone = event.message.text
        if ((len(phone) != 10) or (phone[0:2] != "09")):
            return False
        return True

    def is_going_to_date(self, event):
        text = event.message.text
        if text.isnumeric():
            people = int(text)
            if ((people > 3) or (people < 1)):
                return False
            return True
        return False

    def is_going_to_time(self, event):
        text = event.message.text
        date = text
        return True
        

    def is_going_to_success(self, event):
        text = event.message.text
        time = text
        return True

    def is_going_to_check_reservation(self, event):
        text = event.message.text
        return text == "訂位查詢"

    

    def on_enter_main(self, event):
        reply_token = event.reply_token
        message = message_template.main_menu
        message_to_reply = FlexSendMessage("開啟主選單", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_menu(self, event):
        reply_token = event.reply_token
        print("mode = " + str(mode))
        if mode == 0:
            message = message_template.menu
            message_to_reply = FlexSendMessage("開啟美味菜單", message)
            line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
            line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_kong_rou(self, event):
        reply_token = event.reply_token
        message = event.message.text
        message_to_reply = ImageSendMessage(
            original_content_url = "https://live.staticflickr.com/65535/50061697076_87ae2e9e27_c.jpg",
            preview_image_url = "https://live.staticflickr.com/65535/50061697076_87ae2e9e27_c.jpg"
        )
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_to_menu()

    def on_enter_fish(self, event):
        reply_token = event.reply_token
        message = event.message.text
        message_to_reply = ImageSendMessage(
            original_content_url = "https://aniseblog.tw/wp-content/uploads/2019/12/1575346769-9eebab52df966db945bf937886e312a8.jpg",
            preview_image_url = "https://aniseblog.tw/wp-content/uploads/2019/12/1575346769-9eebab52df966db945bf937886e312a8.jpg"
        )
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_to_menu()

    def on_enter_bye_good(self, event):
        reply_token = event.reply_token
        message = event.message.text
        message_to_reply = ImageSendMessage(
            original_content_url = "https://pic.pimg.tw/nikki20100403/1554306234-1932808141.jpg",
            preview_image_url = "https://pic.pimg.tw/nikki20100403/1554306234-1932808141.jpg"
        )
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_to_menu()

    def on_enter_chicken(self, event):
        reply_token = event.reply_token
        message = event.message.text
        message_to_reply = ImageSendMessage(
            original_content_url = "https://foodpicks.tw/wp-content/uploads/1558614229-1716493942_n.jpg",
            preview_image_url = "https://foodpicks.tw/wp-content/uploads/1558614229-1716493942_n.jpg"
        )
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_to_menu()

    def on_enter_pls_ans(self, event):
        reply_token = event.reply_token
        message = message_template.information
        message_to_reply = FlexSendMessage("請填寫基本資料", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_name(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "請問貴姓?")

    def on_enter_phone(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "請問電話號碼?")

    def on_enter_people(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "請問幾位? (1~3位)")

    def on_enter_date(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入日期 Ex:12月25日")

    def on_enter_time(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入時間(營業時間11:00~20:00)")

    def on_enter_success(self, event):
        reply_token = event.reply_token
        message = message_template.reservation_success_information
        message_to_reply = FlexSendMessage("訂位成功了", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        self.go_back()

