# entry_system
学生証を用いて入退出時刻をLINEで送信するbotです。

## Requirement
- Python 3.7.3
- nfcpy
- LINE Notify API
- Raspberry Pi 3
- PaSoRi RC-S380

## Installation
- pip3
```bash
sudo apt install python3-pip
```

- nfcpy
```bash
sudo pip3 install nfcpy
```

- LINE Notify APIは以下からログインし、API keyを取得してください。
	- [LINE Notify](https://notify-bot.line.me/ja/)

## Usage
- terminal
```bash
sudo python3 main.py
```
