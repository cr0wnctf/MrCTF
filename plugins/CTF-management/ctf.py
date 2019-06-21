import re
from typing import Tuple

from errbot import BotPlugin, botcmd, re_botcmd, Message
from errbot.backends.base import Room, RoomOccupant

CTF_KEY = "CTFS"


class Challenge:
    def __init__(self, name: str, category: str, room: Room):
        self.name = name
        self.category = category
        self.room = room
        self.solved = False
        self.solvers = ()
        self.workers = []

    def solve(self, solvers: Tuple[str]):
        self.solved = True
        self.solvers = solvers

    def unsolve(self):
        self.solved = False
        self.solvers = ()

    def getworkers(self):
        return [worker.username for worker in self.workers]


class CTF:
    def __init__(self, name: str, category: Room, general_room: Room):
        self.name = name
        self.challenges = {}
        self.general_room = general_room
        self.category = category

    def addchallenge(self, name: str, challenge_type: str):
        room = self.category.create_subchannel(challenge_type + "-" + name)
        self.challenges[name] = Challenge(name, challenge_type, room)

        return room

    @property
    def solves(self):
        solves = 0

        for challenge in self.challenges.values():
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

    def print_challenges(self, ctf: CTF):
        ret = ["============= {} =============".format(ctf.general_room)]

        for challenge in ctf.challenges.values():
            if challenge.solved:
                ret.append(":tada: **{}** ({}) (Solved by: {})"
                           .format(challenge.name, challenge.category, ", ".join(challenge.solvers)))
            else:
                ret.append("**{}** ({}) {}"
                           .format(challenge.name,
                                   challenge.category,
                                   ",".join(challenge.getworkers())))

        return "\n".join(ret)

    @botcmd
    def ctf_status(self, msg, args):
        """
        Gets the status of all active CTF's the team is competing in
        """

        if isinstance(msg.frm, RoomOccupant):
            for ctf in self[CTF_KEY]:
                if ctf.general_room == msg.frm.room:
                    return self.print_challenges(ctf)

        ctf_values = []
        for ctf in self[CTF_KEY]:
            key = ctf.name
            value = f"{ctf.general_room} [{ctf.solves} solves / {len(ctf.challenges)} unsolved]"
            ctf_values.append((key, value))

        self.send_card(title="CTF Status",
                       body="Active CTFs",
                       fields=tuple(ctf_values),
                       in_reply_to=msg)

    @botcmd  # Alias
    def s(self, msg, args):
        return self.ctf_status(msg, args)

    @botcmd(split_args_with=None)
    def w(self, msg, args):
        if len(args) != 1:
            return "!w <challenge name>"
        if not isinstance(msg.frm, RoomOccupant):
            return "Need to workon a challenge from a room"

        from_room = msg.frm.room
        challenge_name = args[0]
        with self.mutable(CTF_KEY) as d:
            for ctf in d:
                if ctf.general_room == from_room:
                    if challenge_name not in ctf.challenges:
                        return "Challenge not found!"
                    else:
                        challenge = ctf.challenges[challenge_name]
                        challenge.workers.append(msg.frm)
        self._store.shelf.dict._commit()

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

    @botcmd(split_args_with=None)
    def solve(self, msg, args):
        if not isinstance(msg.frm, RoomOccupant):
            return "Need to solve a challenge from a room"

        msg_room = msg.frm.room

        with self.mutable(CTF_KEY) as d:
            for ctf in d:
                for challenge in ctf.challenges.values():
                    if challenge.room == msg_room:
                        if challenge.solved:
                            return "Challenge already solved!"

                        solvers = [str(msg.frm.username)]
                        solvers.extend(args)
                        challenge.solve(solvers)

                        self.send(ctf.general_room, "@everyone {} had been solved!".format(challenge.room))
                        break
                return "Not in a challenge room!"

        self._store.shelf.dict._commit()

    @botcmd
    def unsolve(self, msg, args):
        if not isinstance(msg.frm, RoomOccupant):
            return "Need to solve a challenge from a room"

        msg_room = msg.frm.room
        with self.mutable(CTF_KEY) as d:
            for ctf in d:
                for challenge in ctf.challenges.values():
                    if challenge.room == msg_room:
                        if not challenge.solved:
                            return "Challenge isn't solved!"

                        challenge.unsolve()

        self._store.shelf.dict._commit()
        return "Unsolved!"

    @botcmd(split_args_with=None)
    def addchallenge(self, msg, args):
        if args is None or len(args) != 2:
            return "!addchallange <name> <category>"
        if not isinstance(msg.frm, RoomOccupant):
            return "Need to add a challenge from a room"

        from_room = msg.frm.room

        with self.mutable(CTF_KEY) as d:
            for ctf in d:
                if ctf.general_room == from_room:
                    challenge_room = ctf.addchallenge(args[0], args[1])
                    return "challenge added in room {}".format(challenge_room)

        self._store.shelf.dict._commit()

        return "Need to be in an active CTF room to add a challenge!"

    @re_botcmd(pattern=r"(^| )rarf( |$)", prefixed=False, flags=re.IGNORECASE)
    def rarf2reef(self, msg: Message, match):
        """Replaces a word with a better one"""
        return msg.body.replace("rarf", "reef")
