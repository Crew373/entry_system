import datetime
import time

import nfc
import requests

# 学生証のサービスコード
service_code = 0x120B


# LINENotifyのBot
class LINENotifyBot:
    API_URL = 'https://notify-api.line.me/api/notify'

    def __init__(self, access_token):
        self.__headers = {'Authorization': 'Bearer ' + access_token}

    def send(self, message):
        payload = {'message': message}

        response = requests.post(
            LINENotifyBot.API_URL,
            headers=self.__headers,
            data=payload,
        )


# 学生番号の読み取り
def on_connect_nfc(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])
            sid = data[0:8].decode()
            global student_id
            student_id = sid
        except Exception as e:
            print("error: %s" % e)
    else:
        print("error: tag isn't Type3Tag")


def main():
    students = []
    clf = nfc.ContactlessFrontend('usb')

    while True:
        dt_now = datetime.datetime.now()
        clf.connect(rdwr={'on-connect': on_connect_nfc})

        if student_id in students:
            info = "退室しました"
            students.remove(student_id)
        else:
            info = "入室しました"
            students.append(student_id)
        # XXXXの部分は取得したAPI keyを貼り付けてください
        bot = LINENotifyBot(access_token='XXXX')
        bot.send(message=student_id + info)

        print(dt_now)
        print(student_id + info)
        time.sleep(5)


if __name__ == "__main__":
    main()
