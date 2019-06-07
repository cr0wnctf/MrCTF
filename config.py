import logging
import os

# This is a minimal configuration to get you started with the Text mode.
# If you want to connect Errbot to chat services, checkout
# the options in the more complete config-template.py from here:
# https://raw.githubusercontent.com/errbotio/errbot/master/errbot/config-template.py

BACKEND = 'Discord'  # Errbot will start in text mode (console only mode) and will answer commands from there.

BOT_DATA_DIR = r'./data'
BOT_EXTRA_PLUGIN_DIR = r'./plugins'
BOT_EXTRA_BACKEND_DIR = r'./backends'

BOT_LOG_FILE = r'./errbot.log'
BOT_LOG_LEVEL = logging.DEBUG
AUTOINSTALL_DEPS = False

BOT_ADMINS = ('@CHANGE_ME', )  # !! Don't leave that to "@CHANGE_ME" if you connect your errbot to a chat system !!

try:
    TOKEN = os.environ["DISCORD_TOKEN"]
except KeyError as e:
    raise ValueError("We need a Discord Token to connect!")

BOT_IDENTITY = {
    'token': TOKEN  # Discord Application Token
}
