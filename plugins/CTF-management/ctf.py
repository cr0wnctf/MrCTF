import re
from typing import Tuple

from errbot import BotPlugin, botcmd, re_botcmd, Message
from errbot.backends.base import Room


CTF_KEY = "CTFS"


class Challenge:
    def __init__(self, name: str, category: str, room_id: str):
        self.name = name
        self.category = category
        self.room = room_id
        self.solved = False
        self.solvers = ()

    def solve(self, solvers: Tuple[str]):
        self.solved = True
        self.solvers = solvers

    def unsolve(self):
        self.solved = False
        self.solvers = ()


class CTF:
    def __init__(self, name: str, category: Room, general_room: Room):
        self.name = name
        self.challenges = []
        self.general_room = general_room
        self.category = category

    @property
    def solves(self):
        solves = 0

        for challenge in self.challenges:
            solves += 1 if challenge.solved else 0

        return solves


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

        ctf_values = []
        for ctf in self[CTF_KEY]:
            key = ctf.name
            value = f"<#{ctf.general_room.id}> [{ctf.solves} solves / {len(ctf.challenges)} unsolved]"
            ctf_values.append((key, value))

        self.send_card(title="CTF Status",
                       body="Active CTFs",
                       fields=tuple(ctf_values),
                       in_reply_to=msg)

    botcmd(ctf_status, name="s")  # Alias

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

        with self.mutable(CTF_KEY) as d:
            d.append(CTF(ctf_name, category, general_room))

        # Do not remove this. This was one annoying bug. Essentially the "shelf" library
        # used for the storage backing contains a .dat file and a .dir file. The dat
        # file contains packed pickle data, and the dir file has (offset, size) pairs. Issue
        # is that these aren't guaranteed to be in sync and on Windows the __del__ magic method
        # is more a suggestion. So the db could contain a ton of pickle data, but the dir lists it as
        # only being 6 bytes long and causes a "truncated pickle data error".
        #
        # TL;DR NEEDED TO PREVENT PICKLE ERRORS

        # noinspection PyProtectedMember
        self._store.shelf.dict._commit()  # This was a bug and a half to track down.

    @botcmd
    def addchallenge(self, msg, args):
        if msg is None:
            return "!addchallange <name> <category>"

    @re_botcmd(pattern=r"(^| )rarf( |$)", prefixed=False, flags=re.IGNORECASE)
    def rarf2reef(self, msg: Message, match):
        """Replaces a word with a better one"""
        return msg.body.replace("rarf", "reef")
