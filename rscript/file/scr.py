__all__ = [
    "CompiledScript",
]

import os.path
from abc import ABC, abstractmethod

from rangers import stream, blockpar
from rscript.file.enums import *
from rscript.file.utils import MinMax, Status, str_to_bool


class CompiledScript:
    supported = (6, 7)

    def __init__(self):
        self.basepath = ""
        self.version = 6

        self.globalvars = []
        """:type : list[Var]"""
        self.globalcode = ""
        self.localvars = []
        """:type : list[Var]"""
        self.constellations = 0
        self.stars = []
        """:type : list[Star]"""
        self.places = []
        """:type : list[Place]"""
        self.items = []
        """:type : list[Item]"""
        self.groups = []
        """:type : list[Group]"""
        self.grouplinks = []
        """:type : list[GroupLink]"""
        self.initcode = ""
        self.turncode = ""
        self.dialogbegincode = ""
        self.states = []
        """:type : list[State]"""
        self.dialogs = []
        """:type : list[Dialog]"""
        self.dialog_msgs = []
        """:type : list[DialogMsg]"""
        self.dialog_answers = []
        """:type : list[DialogAnswer]"""

    def save(self, f):
        """
        :type f: io.BinaryIO
        """
        s = stream.from_io(f)

        s.write_uint(self.version)

        pos = s.pos()
        s.write_uint(0)

        s.write_int(len(self.globalvars))
        for e in self.globalvars:
            s.write_widestr(e.name)
            e.save(s)

        s.write_widestr(self.globalcode)

        offset = s.pos()
        s.seek(pos)
        s.write_uint(offset)
        s.seek(offset)

        s.write_int(len(self.localvars))
        for e in self.localvars:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(self.constellations)

        s.write_int(len(self.stars))
        for e in self.stars:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.places))
        for e in self.places:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.items))
        for e in self.items:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.groups))
        for e in self.groups:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.grouplinks))
        for e in self.grouplinks:
            e.save(s)

        s.write_widestr(self.initcode)
        s.write_widestr(self.turncode)
        s.write_widestr(self.dialogbegincode)

        s.write_int(len(self.states))
        for e in self.states:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.dialogs))
        for e in self.dialogs:
            s.write_widestr(e.name)
            e.save(s)

        s.write_int(len(self.dialog_msgs))
        for e in self.dialog_msgs:
            e.save(s)

        s.write_int(len(self.dialog_answers))
        for e in self.dialog_answers:
            e.save(s)

    def load(self, f):
        """
        :type f: io.BinaryIO
        """
        s = stream.from_io(f)

        self.version = s.read_uint()

        if self.version not in CompiledScript.supported:
            s.close()
            raise Exception("CompiledScript.load. Unsupported version")

        s.read_uint()

        for i in range(s.read_int()):
            e = Var(self, s.read_widestr())
            e.load(s)
            self.globalvars.append(e)

        self.globalcode = s.read_widestr()

        for i in range(s.read_int()):
            e = Var(self, s.read_widestr())
            e.load(s)
            self.localvars.append(e)

        self.constellations = s.read_int()

        for i in range(s.read_int()):
            e = Star(self, s.read_widestr())
            e.load(s)
            self.stars.append(e)

        for i in range(s.read_int()):
            e = Place(self, s.read_widestr())
            e.load(s)
            self.places.append(e)

        for i in range(s.read_int()):
            e = Item(self, s.read_widestr())
            e.load(s)
            self.items.append(e)

        for i in range(s.read_int()):
            e = Group(self, s.read_widestr())
            e.load(s)
            self.groups.append(e)

        for i in range(s.read_int()):
            e = GroupLink(self, str(i))
            e.load(s)
            self.grouplinks.append(e)

        self.initcode = s.read_widestr()
        self.turncode = s.read_widestr()
        self.dialogbegincode = s.read_widestr()

        for i in range(s.read_int()):
            e = State(self, s.read_widestr())
            e.load(s)
            self.states.append(e)

        for i in range(s.read_int()):
            e = Dialog(self, s.read_widestr())
            e.load(s)
            self.dialogs.append(e)

        for i in range(s.read_int()):
            e = DialogMsg(self, str(i))
            e.load(s)
            self.dialog_msgs.append(e)

        for i in range(s.read_int()):
            e = DialogAnswer(self, str(i))
            e.load(s)
            self.dialog_answers.append(e)

    def dump(self, f):
        """
        :type f: io.TextIO
        """
        bp = blockpar.BlockPar(sort=False)

        bp["Version"] = str(self.version)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.globalvars:
            e.dump(nbp)
        bp["GlobalVars"] = nbp

        bp["GlobalCode"] = self.globalcode

        nbp = blockpar.BlockPar(sort=False)
        for e in self.localvars:
            e.dump(nbp)
        bp["LocalVars"] = nbp

        bp["Constellations"] = str(self.constellations)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.stars:
            e.dump(nbp)
        bp["Stars"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.places:
            e.dump(nbp)
        bp["Places"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.items:
            e.dump(nbp)
        bp["Items"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.groups:
            e.dump(nbp)
        bp["Groups"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.grouplinks:
            e.dump(nbp)
        bp["GroupLinks"] = nbp

        bp["InitCode"] = self.initcode

        bp["TurnCode"] = self.turncode

        bp["DialogBegin"] = self.dialogbegincode

        nbp = blockpar.BlockPar(sort=False)
        for i, e in enumerate(self.states):
            e.dump(nbp)
        bp["States"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialogs:
            e.dump(nbp)
        bp["Dialogs"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialog_msgs:
            e.dump(nbp)
        bp["DialogMsgs"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialog_answers:
            e.dump(nbp)
        bp["DialogAnswers"] = nbp

        bp.save_txt(f)
        del bp

    def restore(self, f):
        """
        :type f: io.TextIO
        """
        root = blockpar.BlockPar(sort=False)
        root.load_txt(f)

        self.version = int(root.get_par("Version"))

        for block in root.get_block("GlobalVars"):
            e = Var(self, block.name)
            e.restore(block.content)
            self.globalvars.append(e)

        code = root["GlobalCode"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.globalcode = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.globalcode = code.content
        else:
            raise Exception("CompiledScript.restore globalcode")

        for block in root.get_block("LocalVars"):
            e = Var(self, block.name)
            e.restore(block.content)
            self.localvars.append(e)

        self.constellations = int(root.get_par("Constellations"))

        for block in root.get_block("Stars"):
            e = Star(self, block.name)
            e.restore(block.content)
            self.stars.append(e)

        for block in root.get_block("Places"):
            e = Place(self, block.name)
            e.restore(block.content)
            self.places.append(e)

        for block in root.get_block("Items"):
            e = Item(self, block.name)
            e.restore(block.content)
            self.items.append(e)

        for block in root.get_block("Groups"):
            e = Group(self, block.name)
            e.restore(block.content)
            self.groups.append(e)

        for block in root.get_block("GroupLinks"):
            e = GroupLink(self, block.name)
            e.restore(block.content)
            self.grouplinks.append(e)

        code = root["InitCode"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.initcode = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.initcode = code.content
        else:
            raise Exception("CompiledScript.restore initcode")

        code = root["TurnCode"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.turncode = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.turncode = code.content
        else:
            raise Exception("CompiledScript.restore turncode")

        code = root["DialogBegin"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.dialogbegincode = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.dialogbegincode = code.content
        else:
            raise Exception("CompiledScript.restore dialogbegin")

        for block in root.get_block("States"):
            e = State(self, block.name)
            e.restore(block.content)
            self.states.append(e)

        for block in root.get_block("Dialogs"):
            e = Dialog(self, block.name)
            e.restore(block.content)
            self.dialogs.append(e)

        for block in root.get_block("DialogMsgs"):
            e = DialogMsg(self, block.name)
            e.restore(block.content)
            self.dialog_msgs.append(e)

        for block in root.get_block("DialogAnswers"):
            e = DialogAnswer(self, block.name)
            e.restore(block.content)
            self.dialog_answers.append(e)


class Status:
    __slots__ = "trader", "warrior", "pirate"

    def __init__(self, trader, warrior, pirate):
        self.trader = trader
        self.warrior = warrior
        self.pirate = pirate


class CompiledPoint(ABC):
    def __init__(self, script, name=""):
        """
        :type script: CompiledScript
        :type name: str
        """
        self._script = script
        self.name = name

    @abstractmethod
    def save(self, s):
        """
        :type s: rangers.stream.Stream
        """
        pass

    @abstractmethod
    def load(self, s):
        """
        :type s: rangers.stream.Stream
        """
        pass

    @abstractmethod
    def dump(self, bp):
        """
        :type bp: blockpar.BlockPar
        """
        pass

    @abstractmethod
    def restore(self, bp):
        """
        :type bp: blockpar.BlockPar
        """
        pass


class Var(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type = None
        """:type : var_"""
        self.value = None
        """:type : int | float | str"""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Type"] = str(self.type)
        nbp["Value"] = str(self.value)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_byte(int(self.type))
        if self.type is var_.INTEGER:
            s.write_int(self.value)
        elif self.type is var_.DWORD:
            s.write_uint(self.value)
        elif self.type is var_.FLOAT:
            s.write_double(self.value)
        elif self.type is var_.STRING:
            s.write_widestr(self.value)
        elif self.type is var_.ARRAY:
            s.write_int(self.value)
            for i in range(self.value):
                s.write_widestr('')
                s.write_byte(0)

    def load(self, s):
        self.type = var_(s.read_byte())
        if self.type is var_.INTEGER:
            self.value = s.read_int()
        elif self.type is var_.DWORD:
            self.value = s.read_uint()
        elif self.type is var_.FLOAT:
            self.value = s.read_double()
        elif self.type is var_.STRING:
            self.value = s.read_widestr()
        elif self.type is var_.ARRAY:
            self.value = s.read_int()
            for i in range(self.value):
                s.read_widestr()
                s.read_byte()

    def restore(self, bp):
        self.type = var_.from_str(bp.get_par("Type"))
        if self.type is var_.INTEGER:
            self.value = int(bp.get_par("Value"))
        elif self.type is var_.DWORD:
            self.value = int(bp.get_par("Value"))
        elif self.type is var_.FLOAT:
            self.value = float(bp.get_par("Value"))
        elif self.type is var_.STRING:
            self.value = bp.get_par("Value")
        elif self.type is var_.ARRAY:
            self.value = int(bp.get_par("Value"))


class Star(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.constellation = 0
        self.is_subspace = False
        self.no_kling = False
        self.no_come_kling = False
        self.starlinks = []
        """:type : list[StarLink]"""
        self.planets = []
        """:type : list[Planet]"""
        self.ships = []
        """:type : list[Ship]"""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Constellation"] = str(self.constellation)
        if self._script.version < 7:
            nbp["IsSubspace"] = str(self.is_subspace)
        nbp["NoKling"] = str(self.no_kling)
        nbp["NoComeKling"] = str(self.no_come_kling)

        nnbp = blockpar.BlockPar(sort=False)
        for sl in self.starlinks:
            sl.dump(nnbp)
        nbp["StarLinks"] = nnbp

        nnbp = blockpar.BlockPar(sort=False)
        for p in self.planets:
            p.dump(nnbp)
        nbp["Planets"] = nnbp

        nnbp = blockpar.BlockPar(sort=False)
        for s in self.ships:
            s.dump(nnbp)
        nbp["Ships"] = nnbp

        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_int(self.constellation)
        if self._script.version < 7:
            s.write_bool(self.is_subspace)
        s.write_bool(self.no_kling)
        s.write_bool(self.no_come_kling)

        s.write_uint(len(self.starlinks))
        for e in self.starlinks:
            e.save(s)

        s.write_uint(len(self.planets))
        for e in self.planets:
            s.write_widestr(e.name)
            e.save(s)

        s.write_uint(len(self.ships))
        for e in self.ships:
            e.save(s)

    def load(self, s):
        self.constellation = s.read_int()
        if self._script.version < 7:
            self.is_subspace = s.read_bool()  # always false for 6?
        self.no_kling = s.read_bool()
        self.no_come_kling = s.read_bool()

        for i in range(s.read_uint()):
            e = StarLink(self._script, str(i))
            e.load(s)
            self.starlinks.append(e)

        for i in range(s.read_uint()):
            e = Planet(self._script, s.read_widestr())
            e.load(s)
            self.planets.append(e)

        for i in range(s.read_uint()):
            e = Ship(self._script, str(i))
            e.load(s)
            self.ships.append(e)

    def restore(self, bp):
        self.constellation = int(bp.get_par("Constellation"))
        if self._script.version < 7:
            self.is_subspace = str_to_bool(bp.get_par("IsSubspace"))
        self.no_kling = str_to_bool(bp.get_par("NoKling"))
        self.no_come_kling = str_to_bool(bp.get_par("NoComeKling"))

        for subblock in bp.get_block("StarLinks"):
            e = StarLink(self._script, subblock.name)
            e.restore(subblock.content)
            self.starlinks.append(e)

        for subblock in bp.get_block("Planets"):
            e = Planet(self._script, subblock.name)
            e.restore(subblock.content)
            self.planets.append(e)

        for subblock in bp.get_block("Ships"):
            e = Ship(self._script, subblock.name)
            e.restore(subblock.content)
            self.ships.append(e)


class StarLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.end_star = 0
        self.angle = 0
        self.distance = None
        """:type : MinMax[int]"""
        self.relation = None
        """:type : MinMax[int]"""
        self.deviation = 0
        self.is_hole = False

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["EndStar"] = str(self._script.stars[self.end_star].name) + \
                         ' (' + str(self.end_star) + ')'
        if self._script.version < 7:
            nbp["Angle"] = str(self.angle)
        nbp["Distance"] = str(self.distance)
        if self._script.version < 7:
            nbp["Relation"] = str(self.relation)
            nbp["Deviation"] = str(self.deviation)
        nbp["IsHole"] = str(self.is_hole)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_int(self.end_star)
        if self._script.version < 7:
            s.write_int(self.angle)
        s.write_int(self.distance.min)
        s.write_int(self.distance.max)
        if self._script.version < 7:
            s.write_int(self.relation.min)
            s.write_int(self.relation.max)
            s.write_int(self.deviation)
        s.write_bool(self.is_hole)

    def load(self, s):
        self.end_star = s.read_int()
        if self._script.version < 7:
            self.angle = s.read_int()
        self.distance = MinMax(s.read_int(), s.read_int())
        if self._script.version < 7:
            self.relation = MinMax(s.read_int(), s.read_int())
            self.deviation = s.read_int()
        self.is_hole = s.read_bool()

    def restore(self, bp):
        self.end_star = int(bp.get_par("EndStar"))
        if self._script.version < 7:
            self.angle = int(bp.get_par("Angle"))
        self.distance = MinMax.from_str(bp.get_par("Distance"), int)
        if self._script.version < 7:
            self.relation = MinMax.from_str(bp.get_par("Relation"), int)
            self.deviation = int(bp.get_par("Deviation"))
        self.is_hole = str_to_bool(bp.get_par("IsHole"))


class Planet(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.race = None
        """:type : Race"""
        self.owner = None
        """:type : o_"""
        self.economy = None
        """:type : e_"""
        self.government = None
        """:type : g_"""
        self.range = None
        """:type : MinMax[int]"""
        self.dialog = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Race"] = str(self.race)
        nbp["Owner"] = str(self.owner)
        nbp["Economy"] = str(self.economy)
        nbp["Government"] = str(self.government)
        nbp["Range"] = str(self.range)
        nbp["Dialog"] = str(self.dialog)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_uint(int(self.race))
        s.write_uint(int(self.owner))
        s.write_uint(int(self.economy))
        s.write_uint(int(self.government))
        s.write_int(self.range.min)
        s.write_int(self.range.max)
        s.write_widestr(self.dialog)

    def load(self, s):
        self.race = r_(s.read_uint())
        self.owner = o_(s.read_uint())
        self.economy = e_(s.read_uint())
        self.government = g_(s.read_uint())
        self.range = MinMax(s.read_int(), s.read_int())
        self.dialog = s.read_widestr()

    def restore(self, bp):
        self.race = r_.from_str(bp.get_par("Race"))
        self.owner = o_.from_str(bp.get_par("Owner"))
        self.economy = e_.from_str(bp.get_par("Economy"))
        self.government = g_.from_str(bp.get_par("Government"))
        self.range = MinMax.from_str(bp.get_par("Range"), int)
        self.dialog = bp.get_par("Dialog")


class Ship(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.count = 0
        self.owner = None
        """:type : o_"""
        self.type = None
        """:type : t_"""
        self.is_player = False
        self.speed = None
        """:type : MinMax[int]"""
        self.weapon = None
        """:type : w_"""
        self.cargohook = 0
        self.emptyspace = 0
        self.rating = None
        """:type : MinMax[int]"""
        self.status = None
        """:type : Status"""
        self.score = None
        """:type : MinMax[int]"""
        self.strength = None
        """:type : MinMax[float]"""
        self.ruins = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Count"] = str(self.count)
        nbp["Owner"] = str(self.owner)
        nbp["Type"] = str(self.type)
        nbp["IsPlayer"] = str(self.is_player)
        nbp["Speed"] = str(self.speed)
        nbp["Weapon"] = str(self.weapon)
        nbp["CargoHook"] = str(self.cargohook)
        nbp["EmptySpace"] = str(self.emptyspace)
        if self._script.version < 7:
            nbp["Rating"] = str(self.rating)
        st = blockpar.BlockPar(sort=False)
        st["Trader"] = str(self.status.trader)
        st["Warrior"] = str(self.status.warrior)
        st["Pirate"] = str(self.status.pirate)
        nbp["Status"] = st
        if self._script.version < 7:
            nbp["Score"] = str(self.score)
        nbp["Strength"] = str(self.strength)
        nbp["Ruins"] = str(self.ruins)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_int(self.count)
        s.write_uint(int(self.owner))
        s.write_uint(int(self.type))
        s.write_bool(self.is_player)
        s.write_int(self.speed.min)
        s.write_int(self.speed.max)
        s.write_uint(int(self.weapon))
        s.write_int(self.cargohook)
        s.write_int(self.emptyspace)
        if self._script.version < 7:
            s.write_int(self.rating.min)
            s.write_int(self.rating.max)
        s.write_int(self.status.trader.min)
        s.write_int(self.status.trader.max)
        s.write_int(self.status.warrior.min)
        s.write_int(self.status.warrior.max)
        s.write_int(self.status.pirate.min)
        s.write_int(self.status.pirate.max)
        if self._script.version < 7:
            s.write_int(self.score.min)
            s.write_int(self.score.max)
        s.write_single(self.strength.min)
        s.write_single(self.strength.max)
        s.write_widestr(self.ruins)

    def load(self, s):
        self.count = s.read_int()
        self.owner = o_(s.read_uint())
        self.type = t_(s.read_uint())
        self.is_player = s.read_bool()
        self.speed = MinMax(s.read_int(), s.read_int())
        self.weapon = w_(s.read_uint())
        self.cargohook = s.read_int()
        self.emptyspace = s.read_int()
        if self._script.version < 7:
            self.rating = MinMax(s.read_int(), s.read_int())
        self.status = Status(MinMax(s.read_int(), s.read_int()),
                             MinMax(s.read_int(), s.read_int()),
                             MinMax(s.read_int(), s.read_int()))
        if self._script.version < 7:
            self.score = MinMax(s.read_int(), s.read_int())
        self.strength = MinMax(s.read_single(), s.read_single())
        self.ruins = s.read_widestr()

    def restore(self, bp):
        self.count = int(bp.get_par("Count"))
        self.owner = o_.from_str(bp.get_par("Owner"))
        self.type = t_.from_str(bp.get_par("Type"))
        self.is_player = str_to_bool(bp.get_par("IsPlayer"))
        self.speed = MinMax.from_str(bp.get_par("Speed"), int)
        self.weapon = w_.from_str(bp.get_par("Weapon"))
        self.cargohook = int(bp.get_par("CargoHook"))
        self.emptyspace = int(bp.get_par("EmptySpace"))
        if self._script.version < 7:
            self.rating = MinMax.from_str(bp.get_par("Rating"), int)
        status = bp.get_block("Status")
        self.status = Status(MinMax.from_str(status.get_par("Trader"), int),
                             MinMax.from_str(status.get_par("Warrior"), int),
                             MinMax.from_str(status.get_par("Pirate"), int))
        del status
        if self._script.version < 7:
            self.score = MinMax.from_str(bp.get_par("Score"), int)
        self.strength = MinMax.from_str(bp.get_par("Strength"), float)
        self.ruins = bp.get_par("Ruins")


class Place(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.star = ""
        self.type = None
        """:type : pt_"""
        self.object = ""
        self.angle = 0.0
        self.distance = 0.0
        self.radius = 0

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Star"] = str(self.star)
        nbp["Type"] = str(self.type)
        if self.type is not pt_.FREE:
            nbp["Object"] = str(self.object)
        if self.type is pt_.FREE:
            nbp["Angle"] = str(self.angle)
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            nbp["Distance"] = str(self.distance)
        if self.type is not pt_.IN_PLANET:
            nbp["Radius"] = str(self.radius)
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            nbp["Angle"] = str(self.angle)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.star)
        s.write_uint(int(self.type))
        if self.type is not pt_.FREE:
            s.write_widestr(self.object)
        if self.type is pt_.FREE:
            s.write_single(self.angle)
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            s.write_single(self.distance)
        if self.type is not pt_.IN_PLANET:
            s.write_int(self.radius)
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            s.write_single(self.angle)

    def load(self, s):
        self.star = s.read_widestr()
        self.type = pt_(s.read_uint())
        if self.type is not pt_.FREE:
            self.object = s.read_widestr()
        if self.type is pt_.FREE:
            self.angle = s.read_single()
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            self.distance = s.read_single()
        if self.type is not pt_.IN_PLANET:
            self.radius = s.read_int()
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            self.angle = s.read_single()

    def restore(self, bp):
        self.star = bp.get_par("Star")
        self.type = pt_.from_str(bp.get_par("Type"))
        if self.type is not pt_.FREE:
            self.object = bp.get_par("Object")
        if self.type is pt_.FREE:
            self.angle = float(bp.get_par("Angle"))
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            self.distance = float(bp.get_par("Distance"))
        if self.type is not pt_.IN_PLANET:
            self.radius = int(bp.get_par("Radius"))
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            self.angle = float(bp.get_par("Angle"))


class Item(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.place = ""
        self.kind = None
        """:type : ic_"""
        self.type = None
        """:type : int"""
        self.size = 0
        self.level = 0
        self.radius = 0
        self.owner = None
        """:type : Race"""
        self.useless = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Place"] = str(self.place)
        nbp["Class"] = str(self.kind)
        nbp["Type"] = str(self.type)
        nbp["Size"] = str(self.size)
        nbp["Level"] = str(self.level)
        nbp["Radius"] = str(self.radius)
        nbp["Owner"] = str(self.owner)
        nbp["Useless"] = str(self.useless)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.place)
        s.write_uint(int(self.kind))
        s.write_uint(int(self.type))
        s.write_int(self.size)
        s.write_int(self.level)
        s.write_int(self.radius)
        s.write_uint(int(self.owner))
        s.write_widestr(self.useless)

    def load(self, s):
        self.place = s.read_widestr()
        self.kind = ic_(s.read_uint())
        self.type = s.read_uint()
        self.size = s.read_int()
        self.level = s.read_int()
        self.radius = s.read_int()
        self.owner = Race(s.read_uint())
        self.useless = s.read_widestr()

    def restore(self, bp):
        self.place = bp.get_par("Place")
        self.kind = ic_.from_str(bp.get_par("Class"))
        self.type = int(bp.get_par("Type"))
        self.size = int(bp.get_par("Size"))
        self.level = int(bp.get_par("Level"))
        self.radius = int(bp.get_par("Radius"))
        self.owner = Race.from_str(bp.get_par("Owner"))
        self.useless = bp.get_par("Useless")


class Group(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.planet = ""
        self.state = 0
        self.owner = None
        """:type : o_"""
        self.type = None
        """:type : t_"""
        self.count = None
        """:type : MinMax"""
        self.speed = None
        """:type : MinMax"""
        self.weapon = None
        """:type : w_"""
        self.cargohook = 0
        self.emptyspace = 0
        self.friendship = None
        """:type : f_"""
        self.add_player = False
        self.rating = None
        """:type : MinMax"""
        self.score = None
        """:type : MinMax"""
        self.status = None
        """:type : Status"""
        self.search_distance = 0
        self.dialog = ""
        self.strength = None
        """:type : MinMax"""
        self.ruins = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Planet"] = str(self.planet)
        nbp["State"] = str(self.state) + \
                       '(' + str(self._script.states[self.state].name) + ')'
        nbp["Owner"] = str(self.owner)
        nbp["Type"] = str(self.type)
        nbp["Count"] = str(self.count)
        nbp["Speed"] = str(self.speed)
        nbp["Weapon"] = str(self.weapon)
        nbp["CargoHook"] = str(self.cargohook)
        nbp["EmptySpace"] = str(self.emptyspace)
        if self._script.version < 7:
            nbp["Friendship"] = str(self.friendship)
        nbp["AddPlayer"] = str(self.add_player)
        if self._script.version < 7:
            nbp["Rating"] = str(self.rating)
            nbp["Score"] = str(self.score)
        st = blockpar.BlockPar(sort=False)
        st["Trader"] = str(self.status.trader)
        st["Warrior"] = str(self.status.warrior)
        st["Pirate"] = str(self.status.pirate)
        nbp["Status"] = st
        nbp["SearchDist"] = str(self.search_distance)
        nbp["Dialog"] = str(self.dialog)
        nbp["Strength"] = str(self.strength)
        nbp["Ruins"] = str(self.ruins)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.planet)
        s.write_int(self.state)
        s.write_uint(int(self.owner))
        s.write_uint(int(self.type))
        s.write_int(self.count.min)
        s.write_int(self.count.max)
        s.write_int(self.speed.min)
        s.write_int(self.speed.max)
        s.write_uint(int(self.weapon))
        s.write_int(self.cargohook)
        s.write_int(self.emptyspace)
        if self._script.version < 7:
            s.write_uint(int(self.friendship))
        s.write_bool(self.add_player)
        if self._script.version < 7:
            s.write_int(self.rating.min)
            s.write_int(self.rating.max)
            s.write_int(self.score.min)
            s.write_int(self.score.max)
        s.write_int(self.status.trader.min)
        s.write_int(self.status.trader.max)
        s.write_int(self.status.warrior.min)
        s.write_int(self.status.warrior.max)
        s.write_int(self.status.pirate.min)
        s.write_int(self.status.pirate.max)
        s.write_int(self.search_distance)
        s.write_widestr(self.dialog)
        s.write_single(self.strength.min)
        s.write_single(self.strength.max)
        s.write_widestr(self.ruins)

    def load(self, s):
        self.planet = s.read_widestr()
        self.state = s.read_int()
        self.owner = o_(s.read_uint())
        self.type = t_(s.read_uint())
        self.count = MinMax(s.read_int(), s.read_int())
        self.speed = MinMax(s.read_int(), s.read_int())
        self.weapon = w_(s.read_uint())
        self.cargohook = s.read_int()
        self.emptyspace = s.read_int()
        if self._script.version < 7:
            self.friendship = f_(s.read_uint())
        self.add_player = s.read_bool()
        if self._script.version < 7:
            self.rating = MinMax(s.read_int(), s.read_int())
            self.score = MinMax(s.read_int(), s.read_int())
        self.status = Status(MinMax(s.read_int(), s.read_int()),
                             MinMax(s.read_int(), s.read_int()),
                             MinMax(s.read_int(), s.read_int()))
        self.search_distance = s.read_int()
        self.dialog = s.read_widestr()
        self.strength = MinMax(s.read_single(), s.read_single())
        self.ruins = s.read_widestr()

    def restore(self, bp):
        self.planet = bp.get_par("Planet")
        state = bp.get_par("State").split('(', 1)
        self.state = int(state[0].strip())
        self.owner = o_.from_str(bp.get_par("Owner"))
        self.type = t_.from_str(bp.get_par("Type"))
        self.count = MinMax.from_str(bp.get_par("Count"), int)
        self.speed = MinMax.from_str(bp.get_par("Speed"), int)
        self.weapon = w_.from_str(bp.get_par("Weapon"))
        self.cargohook = int(bp.get_par("CargoHook"))
        self.emptyspace = int(bp.get_par("EmptySpace"))
        if self._script.version < 7:
            self.friendship = f_.from_str(bp.get_par("Friendship"))
        self.add_player = str_to_bool(bp.get_par("AddPlayer"))
        if self._script.version < 7:
            self.rating = MinMax.from_str(bp.get_par("Rating"), int)
            self.score = MinMax.from_str(bp.get_par("Score"), int)
        status = bp.get_block("Status")
        self.status = Status(MinMax.from_str(status.get_par("Trader"), int),
                             MinMax.from_str(status.get_par("Warrior"), int),
                             MinMax.from_str(status.get_par("Pirate"), int))
        del status
        self.search_distance = int(bp.get_par("SearchDist"))
        self.dialog = bp.get_par("Dialog")
        self.strength = MinMax.from_str(bp.get_par("Strength"), float)
        self.ruins = bp.get_par("Ruins")


class GroupLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.begin = 0
        self.end = 0
        self.relations = None
        """:type : tuple[int]"""
        self.war_weight = None
        """:type : MinMax"""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Begin"] = str(self.begin)
        nbp["End"] = str(self.end)
        nbp["Relations"] = str(self.relations)
        nbp["WarWeight"] = str(self.war_weight)
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_int(self.begin)
        s.write_int(self.end)
        s.write_int(int(self.relations[0]))
        s.write_int(int(self.relations[1]))
        s.write_single(self.war_weight.min)
        s.write_single(self.war_weight.max)

    def load(self, s):
        self.begin = s.read_int()
        self.end = s.read_int()
        self.relations = (rel_(s.read_uint()), rel_(s.read_uint()))
        self.war_weight = MinMax(s.read_single(), s.read_single())

    def restore(self, bp):
        self.begin = int(bp.get_par("Begin"))
        self.end = int(bp.get_par("End"))
        relations = bp.get_par("Relations").strip('()').split(',')
        self.relations = (rel_.from_str(relations[0].strip()),
                          rel_.from_str(relations[1].strip()))
        self.war_weight = MinMax.from_str(bp.get_par("WarWeight"), float)


class State(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type = None
        """:type : mt_"""
        self.object = ""
        self.attack = []
        """:type : list[str]"""
        self.take_item = ""
        self.take_all = False
        self.out_msg = ""
        self.in_msg = ""
        self.ether = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Type"] = str(self.type)
        if self.type not in (mt_.NONE, mt_.FREE):
            nbp["Object"] = str(self.object)
        attack = blockpar.BlockPar(sort=False)
        for i, a in enumerate(self.attack):
            attack[str(i)] = str(a)
        nbp["Attack"] = attack
        nbp["TakeItem"] = str(self.take_item)
        nbp["TakeAll"] = str(self.take_all)
        nbp["OutMsg"] = str(self.out_msg)
        nbp["InMsg"] = str(self.in_msg)
        nbp["Ether"] = str(self.ether)
        nbp["Code"] = self.code
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_uint(int(self.type))
        if self.type not in (mt_.NONE, mt_.FREE):
            s.write_widestr(self.object)
        s.write_uint(len(self.attack))
        for e in self.attack:
            s.write_widestr(e)
        s.write_widestr(self.take_item)
        s.write_bool(self.take_all)
        s.write_widestr(self.out_msg)
        s.write_widestr(self.in_msg)
        s.write_widestr(self.ether)
        s.write_widestr(self.code)

    def load(self, s):
        self.type = mt_(s.read_uint())
        if self.type not in (mt_.NONE, mt_.FREE):
            self.object = s.read_widestr()
        for i in range(s.read_uint()):
            self.attack.append(s.read_widestr())
        self.take_item = s.read_widestr()
        self.take_all = s.read_bool()
        self.out_msg = s.read_widestr()
        self.in_msg = s.read_widestr()
        self.ether = s.read_widestr()
        self.code = s.read_widestr()

    def restore(self, bp):
        self.type = mt_.from_str(bp.get_par("Type"))
        if self.type not in (mt_.NONE, mt_.FREE):
            self.object = bp.get_par("Object")
        for par in bp.get_block("Attack"):
            self.attack.append(par.content)
        self.take_item = bp.get_par("TakeItem")
        self.take_all = str_to_bool(bp.get_par("TakeAll"))
        self.out_msg = bp.get_par("OutMsg")
        self.in_msg = bp.get_par("InMsg")
        self.ether = bp.get_par("Ether")

        code = bp["Code"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.code = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.code = code.content
        else:
            raise Exception("State.restore")


class Dialog(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Code"] = self.code
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.code)

    def load(self, s):
        self.code = s.read_widestr()

    def restore(self, bp):
        code = bp["Code"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.code = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.code = code.content
        else:
            raise Exception("Dialog.restore")


class DialogMsg(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Name"] = str(self.command)
        nbp["Code"] = self.code
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.command)
        s.write_widestr(self.code)

    def load(self, s):
        self.command = s.read_widestr()
        self.code = s.read_widestr()

    def restore(self, bp):
        self.command = bp.get_par("Name")
        code = bp["Code"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            self.code = code.content
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.code = code.content
        else:
            raise Exception("DialogMsg.restore")


class DialogAnswer(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.answer = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["Command"] = str(self.command)
        nbp["Answer"] = str(self.answer)
        nbp["Code"] = self.code
        bp[str(self.name)] = nbp

    def save(self, s):
        s.write_widestr(self.command)
        s.write_widestr(self.answer)
        s.write_widestr(self.code)

    def load(self, s):
        self.command = s.read_widestr()
        self.answer = s.read_widestr().strip()
        self.code = s.read_widestr()

    def restore(self, bp):
        self.command = bp.get_par("Command")
        self.answer = bp.get_par("Answer")
        code = bp["Code"][0]
        if code.kind is blockpar.BlockPar.Element.Kind.PARAM:
            path = code.content
            if path == '':
                return
            with open(path, 'rt', encoding='cp1251',
                      newline='') as codefile:
                self.code = codefile.read()
        elif code.kind is blockpar.BlockPar.Element.Kind.BLOCK:
            self.code = code.content
        else:
            raise Exception("DialogMsg.restore")

