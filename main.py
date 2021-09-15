import requests
import nfc
import json
import time


# 学生証のサービスコード
service_code = 0x120B

# entry_apiのurl
base_url = "http://localhost:8080/accesses"


# 学生番号の読み取り
def on_connect_nfc(tag):
    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
            bc = nfc.tag.tt3.BlockCode(0, service=0)
            data = tag.read_without_encryption([sc],[bc])
            sid = data[0:8].decode()
            global student_id
            student_id = sid
        except Exception as e:
            print("error: %s" % e)
    else:
        print("error: tag isn't Type3Tag")


def main():
    clf = nfc.ContactlessFrontend('usb')
    url = (base_url + "/:" + student_id)
    res = requests.get(url)

    lists = json.loads(res.text)

    for list in lists:
        print(list)

    while True:
        clf.connect(rdwr={'on-connect': on_connect_nfc})

        res = requests.get(url)
        lists = json.loads(res.text)

        for list in lists:
            print(list)

        time.sleep(5)

if __name__ == "__main__":
    main()
