import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import requests

# Setup logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = os.path.join(os.path.dirname(__file__), 'out.log')
err_file = os.path.join(os.path.dirname(__file__), 'err.log')

log_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3, encoding='utf-8')
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

err_handler = RotatingFileHandler(err_file, maxBytes=10*1024*1024, backupCount=3, encoding='utf-8')
err_handler.setFormatter(log_formatter)
err_handler.setLevel(logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(err_handler)

class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def send_telegram_msg(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except:
            pass
