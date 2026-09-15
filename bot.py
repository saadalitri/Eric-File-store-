
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, BotCommand
from pyrogram.enums import ParseMode
import sys
import functools
from datetime import datetime, timezone
from config import LOGGER, PORT, OWNER_ID, URL
from helper import MongoDB
from helper.helper_func import weilai_style
version = "v1.0.0"

class Bot(Client):
    def __init__(self, config):
        session = config["session"]
        workers = config["workers"]
        if session.startswith("clone_"):
            workers = min(workers, 4)
        databases = config.get("databases", {"primary": config.get("db"), "secondary": [], "backup": None})
        fsub = config["fsubs"]
        token = config["token"]
        admins = config["admins"]
        messages = config.get("messages", {})
        auto_del = config["auto_del"]
        db_uri = config["db_uri"]
        db_uri_2 = config.get("db_uri_2", "")
        db_uri_3 = config.get("db_uri_3", "")
        db_uri_4 = config.get("db_uri_4", "")
        db_name = config["db_name"]
        api_id = int(config["api_id"])
        api_hash = config["api_hash"]
        protect = config.get("protect", False)
        disable_btn = config.get("disable_btn", True)

        super().__init__(
    name=session,
    api_hash=api_hash,
    api_id=api_id,
    plugins={"root": "plugins"},
    workers=workers,
    bot_token=token,
    in_memory=True
        )
        self.LOGGER = LOGGER
        self.raw_config = config
        self.name = session
        self.databases = databases
        self.db = databases.get('primary')
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get('REPLY', 'Do not send any useless message in the bot.')
        self.mongodb = MongoDB(db_uri, db_name, db_uri_2, db_uri_3, db_uri_4)
        self.all_db_ids = []
        self.db_usernames = {}
        self.protect = protect
        self.redirector_username = None
        self.link_gen_bot = None
        self.redirector_log = None
        self.autobatch_template = ""
        self.hide_caption = False
        self.channel_button_enabled = False
        self.button_name = "Join Updates"
        self.button_url = "https://t.me/realm_bots"
        self.robot_check = False
        self.is_support = True
        self.channel_link_expiry = 0
    def get_current_settings(self):
        """Returns the dictionary for the legacy settings system."""
        return {
            "admins": self.admins,
            "messages": self.messages,
            "auto_del": self.auto_del,
            "disable_btn": self.disable_btn,
            "reply_text": self.reply_text,
            "fsub": self.fsub,
            "databases": self.databases,
            "robot_check": self.robot_check
        }

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now(timezone.utc)

        from plugins.autobatch_settings import DEFAULT_AUTOBATCH_TEMPLATE
        self.autobatch_template = await self.mongodb.load_bot_setting('autobatch_template', DEFAULT_AUTOBATCH_TEMPLATE)
        self.redirector_username = await self.mongodb.load_bot_setting('redirector_username')
        self.link_gen_bot = await self.mongodb.load_bot_setting('link_gen_bot')
        self.redirector_log = await self.mongodb.load_bot_setting('redirector_log')
        if not self.redirector_username:
            self.redirector_username = []
        elif isinstance(self.redirector_username, str):
            self.redirector_username = [self.redirector_username]
        self.protect = await self.mongodb.load_bot_setting('protect_content', self.protect)
        self.hide_caption = await self.mongodb.load_bot_setting('hide_caption', False)
        self.channel_button_enabled = await self.mongodb.load_bot_setting('channel_button_enabled', False)
        self.button_name = await self.mongodb.load_bot_setting('button_name', self.button_name)
        self.button_url = await self.mongodb.load_bot_setting('button_url', self.button_url)
        self.robot_check = await self.mongodb.load_bot_setting('robot_check', False)
        self.channel_link_expiry = await self.mongodb.load_bot_setting('channel_link_expiry', 0)
        self.LOGGER(__name__, self.name).info("All modern settings loaded and validated.")
        saved_settings = await self.mongodb.load_settings(self.name)
        if saved_settings:
            self.LOGGER(__name__, self.name).info("Found legacy saved settings, merging them.")
            base_messages = self.messages.copy()
            saved_messages = saved_settings.get("messages", {})
            for key, value in saved_messages.items():
                if value: base_messages[key] = value
            self.messages = base_messages
            saved_admins = saved_settings.get("admins", [])
            self.admins = list(set(self.admins + saved_admins + [OWNER_ID]))
            if saved_fsub := saved_settings.get("fsub"): self.fsub = saved_fsub
            if saved_databases := saved_settings.get("databases"):
                self.databases = saved_databases
                self.db = self.databases.get('primary')
            self.auto_del = saved_settings.get("auto_del", self.auto_del)
            self.disable_btn = saved_settings.get("disable_btn", self.disable_btn)
            self.reply_text = saved_settings.get("reply_text", self.reply_text)
        self.fsub_dict = {}
        if self.fsub:
            for channel_id, needs_request, timer in self.fsub:
                try:
                    chat = await self.get_chat(channel_id)
                    invite_link = chat.invite_link
                    if not invite_link and timer <= 0:
                        invite_link = (await self.create_chat_invite_link(channel_id, creates_join_request=needs_request)).invite_link
                    self.fsub_dict[channel_id] = [chat.title, invite_link, needs_request, timer]
                except Exception as e:
                    self.LOGGER(__name__, self.name).error(f"Error processing FSub channel {channel_id}: {e}.")

        if not self.db:
            self.LOGGER(__name__, self.name).warning("No Primary Database channel is set!")
        else:
            try:
                db_channel = await self.get_chat(self.db)
                self.db_channel = db_channel
                if not self.name.startswith("clone_"):
                    test = await self.send_message(chat_id=db_channel.id, text="𝖡𝗈𝗍 𝗂𝗌 𝗈𝗇𝗅𝗂𝗇𝖾.")
                    await test.delete()
            except Exception as e:
                self.LOGGER(__name__, self.name).warning(e)
                self.LOGGER(__name__, self.name).warning(f"Make sure bot is Admin in Primary DB Channel. Current Value {self.db}")

        self.all_db_ids = [db_id for db_id in [self.databases.get('primary')] + self.databases.get('secondary', []) if db_id]
        await self.refresh_db_usernames()

        try:
            await self.mongodb.verifications.drop_index("created_at_1")
        except Exception:
            pass

        self.LOGGER(__name__, self.name).info(f"Bot Started on @{usr_bot_me.username} !!")
        self.username = usr_bot_me.username
        self.bot_name = usr_bot_me.first_name

        try:
            commands = [
                BotCommand("start", weilai_style("Start The Bot")),
                BotCommand("settings", weilai_style("Bot Settings")),
                BotCommand("broadcast", weilai_style("Broadcast Message")),
                BotCommand("pbroadcast", weilai_style("Pin Broadcast")),
                BotCommand("dbroadcast", weilai_style("Deletable Broadcast")),
                BotCommand("batch", weilai_style("Generate Batch Link")),
                BotCommand("genlink", weilai_style("Generate Single Link")),
                BotCommand("autobatch", weilai_style("Auto Batch Range")),
                BotCommand("usage", weilai_style("System Usage Stats")),
                BotCommand("users", weilai_style("Bot User Statistics")),
                BotCommand("database", weilai_style("Database Channel Settings")),
                BotCommand("ban", weilai_style("Ban Users")),
                BotCommand("unban", weilai_style("Unban Users"))
            ]
            await self.set_bot_commands(commands)
            self.LOGGER(__name__, self.name).info("Bot commands set successfully.")
        except Exception as e:
            self.LOGGER(__name__, self.name).error(f"Failed to set bot commands: {e}")

    async def refresh_db_usernames(self):
        """Refreshes the database channel username cache."""
        self.db_usernames = {}
        for db_id in self.all_db_ids:
            try:
                chat = await self.get_chat(db_id)
                if chat.username:
                    self.db_usernames[chat.username.lower()] = db_id
            except Exception:
                continue
        self.LOGGER(__name__, self.name).info(f"Refreshed DB usernames: {len(self.db_usernames)} found.")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")
