import re

from errbot import BotPlugin, botcmd, re_botcmd, Message
from errbot.backends.base import Room


CTF_KEY = "CTFS"


class CTF:
    def __init__(self, name: str, category: Room, general_room: Room):
        self.name = name
        self.challenges = []
        self.general_room = general_room
        self.category = category


class CTF_Plugin(BotPlugin):
    """
    CTF Plugin to handle teams during events
    """

    def activate(self):
        super().activate()

        # initial setup
        if CTF_KEY not in self:
            self[CTF_KEY] = []

    @botcmd
    def ctf_status(self, msg, args):
        """
        Gets the status of all active CTF's the team is competing in
        """
        for ctf in self[CTF_KEY]:
            pass

        return 'It *works* ! <#585874178989752321>'

    @botcmd
    def addctf(self, msg, ctf_name):
        """Adds an CTF to play in
        usage: !ctf add <ctf_name>
        """
        if not ctf_name:
            return "usage: !ctf add <ctf_name>"

        category = self.query_room("##" + ctf_name)
        category.create()

        try:
            general_room = category.create_subchannel(ctf_name + "-general")
        except AttributeError as e:
            raise RuntimeError(e, "We need an object that supports creating sub-channels")

        self[CTF_KEY].append(CTF(ctf_name, category, general_room))

    @re_botcmd(pattern=r"(^| )rarf( |$)", prefixed=False, flags=re.IGNORECASE)
    def rarf2reef(self, msg: Message, match):
        """Replaces a word with a better one"""
        return msg.body.replace("rarf", "reef")
