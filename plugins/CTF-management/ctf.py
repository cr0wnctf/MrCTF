import re

from errbot import BotPlugin, botcmd, re_botcmd, Message
from errbot.backends.base import Room

CTF_KEY = "CTFS"


class CTF:
    def __init__(self, name: str):
        self.name = name
        self.challenges = []


class CTF_Plugin(BotPlugin):
    """
    CTF Plugin to handle teams during events
    """

    def activate(self):
        super().activate()

        # initial setup
        if CTF_KEY not in self:
            self[CTF_KEY] = []

    @botcmd  # flags a command
    def ctf_status(self, msg, args):  # a command callable with !tryme
        """
        Gets the status of all active CTF's the team is competing in
        """
        return 'It *works* !'  # This string format is markdown.

    @botcmd
    def ctf_add(self, msg, ctf_name):
        """Adds an CTF to play in
        usage: !ctf add <ctf_name>
        """
        if not ctf_name:
            return "usage: !ctf add <ctf_name>"

        room = self.query_room(ctf_name)
        room.create()
        self[CTF_KEY] = CTF(ctf_name)

    @re_botcmd(pattern=r"(^| )rarf( |$)", prefixed=False, flags=re.IGNORECASE)
    def rarf2reef(self, msg: Message, match):
        """Replaces a word with a better one"""
        return msg.body.replace("rarf", "reef")
