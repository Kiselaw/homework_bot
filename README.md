## YPHW bot

A simple telegram bot that informs me (as a student) about the status of my homework.

### Overview

The bot can interact with the Yandex.Praсtiсum website API and the Telegram messenger API. Thus, if there is a request to the bot and there is a response on the status of homework, the bot will send a result text message to the appropriate chat.

### Technologies

- Python 3.9.5

### Installation and launch

IMPORTAT NOTE!

This bot is designed to work specifically with my homework, so if you want to test the bot in practice, then you firtsly need to do the following:

- create your own bot via @botfather and get a token
- receive your own token via [Yandex.Practicum](https://practicum.yandex.ru/) website (you have to be the student)
- put the data in the variables PRACTICUM_TOKEN, TELEGRAM_TOKEN and TELEGRAM_CHAT_ID

Clone the repository and go to it using the command line:

```bash
git clone 
```

```bash
cd homework_bot
```

Create and activate a virtual environment:

Windows:

```bash
py -3 -m venv env
```

```bash
. venv/Scripts/activate 
```

```bash
py -m pip install --upgrade pip
```

macOS/Linux:

```bash
python3 -m venv .venv
```

```bash
source env/bin/activate
```

```bash
python3 -m pip install --upgrade pip
```

Install dependencies from a file requirements.txt:

```bash
pip install -r requirements.txt
```

Launch:

Windows:

```bash
py homework.py 
```

macOS/Linux:

```bash
python3 homework.py 
```

### License

MIT