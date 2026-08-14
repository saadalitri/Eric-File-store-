import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE_NAME = "bot.log"
PORT = 8091
URL = ""
OWNER_ID = 8516933880,8516933880      # <-- apna Telegram user ID daalo (number, quotes ke bina)
MSG_EFFECT = 0

DEFAULT_MESSAGES = {
    "START": "<b><blockquote>𝖧𝖾𝗒 {mention}!</blockquote></b>\n\n𝖨 𝖺𝗆 𝖺 𝖿𝗂𝗅𝖾 𝗌𝗍𝗈𝗋𝖾 𝖻𝗈𝗍.\n𝖨 𝖼𝖺𝗇 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗉𝗋𝗂𝗏𝖺𝗍𝖾 𝖿𝗂𝗅𝖾𝗌 𝗍𝗁𝗋𝗈𝗎𝗀𝗁 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝗅𝗂𝗇𝗄.\n\n<b><blockquote>➤ 𝖯𝗈𝗐𝖾𝗋𝖾𝚍 𝖻𝗒 @Eric_Realm</blockquote></b>",
    "FSUB": "<b><blockquote>✗ 𝖠𝖼𝖼𝖾𝗌𝗌 𝖣𝖾𝗇𝗂𝖾𝖽!</blockquote></b>\n\n𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗃𝗈𝗂𝗇 𝗈𝗎𝗋 𝗈𝖿𝖿𝗂𝖼𝗂𝖺𝗅 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝗍𝗈 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖻𝗈𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗃𝗈𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖻𝖾𝗅𝗈𝗐.",
    "ABOUT": "<b><blockquote>𝖠𝖻𝗈𝗎𝗍 𝖳𝗁𝗂𝗌 𝖡𝗈𝗍\n╭────[  𝖳𝖾𝖼𝗁𝗇𝗂𝖼𝖺𝗅 𝖲𝗍𝖺𝖼𝗄 ]────⍟\n➠ 𝖡𝗈𝗍 𝖭𝖺𝗆𝖾 : {bot_name}\n➠ 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋 : Eric Realm\n➠ 𝖫𝗂𝖻𝗋𝖺𝗋𝗒 : 𝖯𝗒𝗋𝗈𝗀𝗋𝖺𝗆 𝖠𝗌𝗒𝗇𝖼\n➠ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 : 𝖯𝗒𝗍𝗁𝗈𝗇 𝟥.𝟣𝟣+\n➠ 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾 : 𝖬𝗈𝗇𝗀𝗈𝖣𝖡 𝖠𝗍𝗅𝖺𝗌 𝖢𝗅𝗎𝗌𝗍𝖾𝗋\n➠ 𝖵𝖾𝗋𝗌𝗂𝗈𝗇 : 𝖹𝖾𝗍𝗂𝖺𝗇 𝟤.𝟨.𝟥 [ 𝖫𝖺𝗍𝖾𝗌𝗍 ]\n➠ 𝖧𝗈𝗌𝗍𝗂𝗇𝗀 : 𝖣𝖾𝖽𝗂𝖼𝖺𝗍𝖾𝖽 𝖧𝗂𝗀𝗁-𝖲𝗉𝖾𝖾𝖽 𝖵𝖯𝖲\n╰───────────────⍟</blockquote></b>",
    "REPLY": "✓ 𝖨 𝖺𝗆 𝖽𝖾𝖽𝗂𝖼𝖺𝗍𝖾𝖽 𝗍𝗈 𝗆𝗒 𝗆𝖺𝗌𝗍𝖾𝗋. 𝖣𝗈𝗇'𝗍 𝖺𝖻𝗎𝗌𝖾 𝗆𝖾.",
    "START_PHOTO": "https://graph.org/file/00daf970f7c8b9282cc5c-7d62ceac5da0423a44.jpg",
    "ABOUT_PHOTO": "https://graph.org/file/00daf970f7c8b9282cc5c-7d62ceac5da0423a44.jpg",
    "FSUB_PHOTO": "https://graph.org/file/00daf970f7c8b9282cc5c-7d62ceac5da0423a44.jpg",
    "SETTINGS_PHOTO": "https://graph.org/file/00daf970f7c8b9282cc5c-7d62ceac5da0423a44.jpg",
    "AUTO_DEL_TEXT": "<b>⚠️ 𝖣𝗎𝖾 𝖳𝗈 𝖢𝗈𝗉𝗒𝗋𝗂𝗀𝗁𝗍 𝖨𝗌𝗌𝗎𝖾𝗌....\n<blockquote>𝖸𝗈𝗎𝗋 𝖥𝗂𝗅𝖾𝗌 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖶𝗂𝗍𝗁𝗂𝗇 {time}. 𝖲𝗈 𝖯𝗅𝖾𝖺𝗌𝖾 𝖥𝗈𝗋𝗐𝖺𝗋𝖽 𝖳𝗁𝖾𝗆 𝖳𝗈 𝖠𝗇𝗒 𝖮𝗍𝗁𝖾𝗋 𝖯𝗅𝖺𝖼𝖾 𝖥𝗈𝗋 𝖥𝗎𝗍𝗎𝗋𝖾 𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗂𝗅𝗂𝗍𝗒.</blockquote>\n<blockquote>𝖭𝗈𝗍𝖾 : 𝖴𝗌𝖾 𝖵𝗅𝖼 𝖮𝗋 𝖠𝗇𝗒 𝖮𝗍𝗁𝖾𝗋 𝖦𝗈𝗈𝖽 𝖵𝗂𝖽𝖾𝗈 𝖯𝗅𝖺𝗒𝖾𝗋 𝖠𝗉𝗉 𝖳𝗈 𝖶𝖺𝗍𝖼𝗁 𝖳𝗁𝖾 𝖤𝗉𝗂𝗌𝗈𝖽𝖾𝗌 𝖶𝗂𝗍𝗁 𝖦𝗈𝗈𝖽 𝖤𝗑𝗉𝖾𝗋𝗂𝖾𝗇𝖼𝖾!</blockquote></b>",
    "AUTO_DEL_PHOTO": ""
}

BOTS = [
    {
        "session": "mybot",                                       # <-- session name (koi bhi unique naam, e.g. "mainbot")
        "token": "8893037363:AAE3XjVghhRgQRQuI5pC1J075xahShpNt4o",  # <-- @BotFather se mila token
        "api_id": 4216194,                                        # <-- my.telegram.org se mila API ID (number)
        "api_hash": "bcb1507e45dcc4ce24444d824b4cf48d",            # <-- my.telegram.org se mila API HASH
        "workers": 8,
        "db_uri": "mongodb+srv://Eratri:eratri@cluster0.zippnsi.mongodb.net/?appName=Cluster0",  # <-- MongoDB Atlas connection URI
        "db_uri_2": "",
        "db_uri_3": "",
        "db_uri_4": "",
        "db_name": "Eratri",                                    # <-- MongoDB database ka naam
        "fsubs": [],
        "databases": {
            "primary": -1004431888767,   # <-- DB channel ki ID (bot us channel mein admin hona chahiye)
            "secondary": [],
            "backup": None
        },
        "auto_del": 600,
        "messages": DEFAULT_MESSAGES,
        "admins": [8516933880],                    # <-- extra admin Telegram user IDs, e.g. [111111111, 222222222]
        "disable_btn": True,
        "protect": False
    }
]

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(stream_handler)

    return logger
