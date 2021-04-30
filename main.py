import binascii
import dataclasses
import datetime
import time

import dataclasses_json
import httplib2
import nfc
import requests

# 学生証のサービスコード
service_code = 0x120B


class Event:
    def __init__(self, value):
        self.value = value


Register = Event("register")
Delete = Event("delete")
Entry = Event("entry")
Exit = Event("exit")
event_list = [Register, Delete, Entry, Exit]


def parse_event(source):
    for event in event_list:
        if event.value == source:
            return event

    raise TypeError


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class Member:
    student_id: str
    alias_id: str
    name: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class Access:
    student_id: str
    event: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass
class Log:
    student_id: str
    event: str
    date: str


class MemberRegisterApiClient:
    def __init__(self):
        self.__client = httplib2.Http()
        self.__base_uri = 'http://localhost:8080'

    def entry(self, student_id):
        uri = self.__base_uri + '/accesses/' + student_id
        access = Access(student_id, Entry.value)

        self.__client.request(uri, "PUT", body=access.to_json())
        self.__take_log(access)

    def exit(self, student_id):
        uri = self.__base_uri + '/accesses/' + student_id
        access = Access(student_id, Exit.value)

        self.__client.request(uri, "PUT", body=access.to_json())
        self.__take_log(access)

    def register(self, student_id):
        pass

    def delete(self, student_id):
        pass

    def get_event(self, student_id):
        uri = self.__base_uri + '/accesses/' + student_id

        (header, content) = self.__client.request(uri, "GET")
        access = Access.from_json(content)

        return parse_event(access.event)

    def get_student_id(self, idm):
        if idm is None:
            return None

        uri = self.__base_uri + '/members/' + idm

        (header, content) = self.__client.request(uri, "GET")
        member = Member.from_json(content)

        return member.student_id

    def __take_log(self, access):
        uri = self.__base_uri + '/logs'
        raw_date = datetime.datetime.now()
        date = raw_date.strftime('%Y/%m/%d-%H:%M:%S')
        print(date)

        log = Log(access.student_id, access.event, date)
        self.__client.request(uri, "POST", body=log.to_json())


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
    global global_student_id
    global global_idm

    global_student_id = None
    global_idm = ("%s" % (binascii.hexlify(tag.idm)))[2:-1]
    print("idm ", global_idm)
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc], [bc])
            sid = data[0:8].decode()
            global_student_id = sid
        except Exception as e:
            print("error: %s" % e)
    else:
        print("error: tag isn't Type3Tag")


def main():
    api_client = MemberRegisterApiClient()
    clf = nfc.ContactlessFrontend('usb')

    while True:
        dt_now = datetime.datetime.now()
        clf.connect(rdwr={
            'targets': ['212F', '424F'],
            'on-connect': on_connect_nfc
        })

        student_id = global_student_id
        idm = global_idm
        student_id = api_client.get_student_id(idm) if student_id is None else student_id
        if student_id is None:
            continue

        event = api_client.get_event(student_id)

        if event == Register or event == Exit:
            api_client.entry(student_id)
            info = "入室しました"
        elif event == Entry:
            api_client.exit(student_id)
            info = "退室しました"
        else:
            return

        # # XXXXの部分は取得したAPI keyを貼り付けてください
        # bot = LINENotifyBot(access_token='XXXX')
        # bot.send(message=student_id + info)

        print(dt_now)
        print(student_id + info)
        time.sleep(2)


if __name__ == "__main__":
    main()
