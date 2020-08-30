__all__ = [
    "CompiledScript",
]

from abc import ABC, abstractmethod

from rangers.io import Stream
from rangers.blockpar import BlockPar
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
        s = Stream.from_io(f)

        s.add_uint(self.version)

        pos = s.pos()
        s.add_uint(0)

        s.add_int(len(self.globalvars))
        for e in self.globalvars:
            s.add_widestr(e.name)
            e.save(s)

        s.add_widestr(self.globalcode)

        offset = s.pos()
        s.seek(pos)
        s.add_uint(offset)
        s.seek(offset)

        s.add_int(len(self.localvars))
        for e in self.localvars:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(self.constellations)

        s.add_int(len(self.stars))
        for e in self.stars:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.places))
        for e in self.places:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.items))
        for e in self.items:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.groups))
        for e in self.groups:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.grouplinks))
        for e in self.grouplinks:
            e.save(s)

        s.add_widestr(self.initcode)
        s.add_widestr(self.turncode)
        s.add_widestr(self.dialogbegincode)

        s.add_int(len(self.states))
        for e in self.states:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.dialogs))
        for e in self.dialogs:
            s.add_widestr(e.name)
            e.save(s)

        s.add_int(len(self.dialog_msgs))
        for e in self.dialog_msgs:
            e.save(s)

        s.add_int(len(self.dialog_answers))
        for e in self.dialog_answers:
            e.save(s)

    def load(self, f):
        """
        :type f: io.BinaryIO
        """
        s = Stream.from_io(f)

        self.version = s.get_uint()

        if self.version not in CompiledScript.supported:
            s.close()
            raise Exception("CompiledScript.load. Unsupported version")

        s.get_uint()

        for i in range(s.get_int()):
            e = Var(self, s.get_widestr())
            e.load(s)
            self.globalvars.append(e)

        self.globalcode = s.get_widestr()

        for i in range(s.get_int()):
            e = Var(self, s.get_widestr())
            e.load(s)
            self.localvars.append(e)

        self.constellations = s.get_int()

        for i in range(s.get_int()):
            e = Star(self, s.get_widestr())
            e.load(s)
            self.stars.append(e)

        for i in range(s.get_int()):
            e = Place(self, s.get_widestr())
            e.load(s)
            self.places.append(e)

        for i in range(s.get_int()):
            e = Item(self, s.get_widestr())
            e.load(s)
            self.items.append(e)

        for i in range(s.get_int()):
            e = Group(self, s.get_widestr())
            e.load(s)
            self.groups.append(e)

        for i in range(s.get_int()):
            e = GroupLink(self, str(i))
            e.load(s)
            self.grouplinks.append(e)

        self.initcode = s.get_widestr()
        self.turncode = s.get_widestr()
        self.dialogbegincode = s.get_widestr()

        for i in range(s.get_int()):
            e = State(self, s.get_widestr())
            e.load(s)
            self.states.append(e)

        for i in range(s.get_int()):
            e = Dialog(self, s.get_widestr())
            e.load(s)
            self.dialogs.append(e)

        for i in range(s.get_int()):
            e = DialogMsg(self, str(i))
            e.load(s)
            self.dialog_msgs.append(e)

        for i in range(s.get_int()):
            e = DialogAnswer(self, str(i))
            e.load(s)
            self.dialog_answers.append(e)

    def dump(self, f):
        """
        :type f: io.TextIO
        """
        bp = BlockPar(sort=False)

        bp.add("Version", str(self.version))

        nbp = BlockPar(sort=False)
        for e in self.globalvars:
            e.dump(nbp)
        bp.add("GlobalVars", nbp)

        bp.add("GlobalCode", self.globalcode)

        nbp = BlockPar(sort=False)
        for e in self.localvars:
            e.dump(nbp)
        bp.add("LocalVars", nbp)

        bp.add("Constellations", str(self.constellations))

        nbp = BlockPar(sort=False)
        for e in self.stars:
            e.dump(nbp)
        bp.add("Stars", nbp)

        nbp = BlockPar(sort=False)
        for e in self.places:
            e.dump(nbp)
        bp.add("Places", nbp)

        nbp = BlockPar(sort=False)
        for e in self.items:
            e.dump(nbp)
        bp.add("Items", nbp)

        nbp = BlockPar(sort=False)
        for e in self.groups:
            e.dump(nbp)
        bp.add("Groups", nbp)

        nbp = BlockPar(sort=False)
        for e in self.grouplinks:
            e.dump(nbp)
        bp.add("GroupLinks", nbp)

        bp.add("InitCode", self.initcode)

        bp.add("TurnCode", self.turncode)

        bp.add("DialogBegin", self.dialogbegincode)

        nbp = BlockPar(sort=False)
        for i, e in enumerate(self.states):
            e.dump(nbp)
        bp.add("States", nbp)

        nbp = BlockPar(sort=False)
        for e in self.dialogs:
            e.dump(nbp)
        bp.add("Dialogs", nbp)

        nbp = BlockPar(sort=False)
        for e in self.dialog_msgs:
            e.dump(nbp)
        bp.add("DialogMsgs", nbp)

        nbp = BlockPar(sort=False)
        for e in self.dialog_answers:
            e.dump(nbp)
        bp.add("DialogAnswers", nbp)

        bp.save_txt(f)
        del bp

    def restore(self, f):
        """
        :type f: io.TextIO
        """
        root = BlockPar(sort=False)
        root.load_txt(f)

        self.version = int(root.get_par("Version"))

        for block in root.get_block("GlobalVars"):
            e = Var(self, block.name)
            e.restore(block.content)
            self.globalvars.append(e)

        self.globalcode = root.get_par("GlobalCode")

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

        self.initcode = root.get_par("InitCode")
        self.turncode = root.get_par("TurnCode")
        self.dialogbegincode = root.get_par("DialogBegin")

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
        nbp = BlockPar(sort=False)
        nbp.add("Type", str(self.type))
        nbp.add("Value", str(self.value))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_byte(int(self.type))
        if self.type is var_.INTEGER:
            s.add_int(self.value)
        elif self.type is var_.DWORD:
            s.add_uint(self.value)
        elif self.type is var_.FLOAT:
            s.add_double(self.value)
        elif self.type is var_.STRING:
            s.add_widestr(self.value)
        elif self.type is var_.ARRAY:
            s.add_int(self.value)
            for i in range(self.value):
                s.add_widestr('')
                s.add_byte(0)

    def load(self, s):
        self.type = var_(s.get_byte())
        if self.type is var_.INTEGER:
            self.value = s.get_int()
        elif self.type is var_.DWORD:
            self.value = s.get_uint()
        elif self.type is var_.FLOAT:
            self.value = s.get_double()
        elif self.type is var_.STRING:
            self.value = s.get_widestr()
        elif self.type is var_.ARRAY:
            self.value = s.get_int()
            for i in range(self.value):
                s.get_widestr()
                s.get_byte()

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
        nbp = BlockPar(sort=False)
        nbp.add("Constellation", str(self.constellation))
        if self._script.version < 7:
            nbp.add("IsSubspace", str(self.is_subspace))
        nbp.add("NoKling", str(self.no_kling))
        nbp.add("NoComeKling", str(self.no_come_kling))

        nnbp = BlockPar(sort=False)
        for sl in self.starlinks:
            sl.dump(nnbp)
        nbp.add("StarLinks", nnbp)

        nnbp = BlockPar(sort=False)
        for p in self.planets:
            p.dump(nnbp)
        nbp.add("Planets", nnbp)

        nnbp = BlockPar(sort=False)
        for s in self.ships:
            s.dump(nnbp)
        nbp.add("Ships", nnbp)

        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_int(self.constellation)
        if self._script.version < 7:
            s.add_bool(self.is_subspace)
        s.add_bool(self.no_kling)
        s.add_bool(self.no_come_kling)

        s.add_uint(len(self.starlinks))
        for e in self.starlinks:
            e.save(s)

        s.add_uint(len(self.planets))
        for e in self.planets:
            s.add_widestr(e.name)
            e.save(s)

        s.add_uint(len(self.ships))
        for e in self.ships:
            e.save(s)

    def load(self, s):
        self.constellation = s.get_int()
        if self._script.version < 7:
            self.is_subspace = s.get_bool()  # always false for 6?
        self.no_kling = s.get_bool()
        self.no_come_kling = s.get_bool()

        for i in range(s.get_uint()):
            e = StarLink(self._script, str(i))
            e.load(s)
            self.starlinks.append(e)

        for i in range(s.get_uint()):
            e = Planet(self._script, s.get_widestr())
            e.load(s)
            self.planets.append(e)

        for i in range(s.get_uint()):
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
        nbp =BlockPar(sort=False)
        nbp.add("EndStar", str(self._script.stars[self.end_star].name) + \
                           ' (' + str(self.end_star) + ')')
        if self._script.version < 7:
            nbp.add("Angle", str(self.angle))
        nbp.add("Distance", str(self.distance))
        if self._script.version < 7:
            nbp.add("Relation", str(self.relation))
            nbp.add("Deviation", str(self.deviation))
        nbp.add("IsHole", str(self.is_hole))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_int(self.end_star)
        if self._script.version < 7:
            s.add_int(self.angle)
        s.add_int(self.distance.min)
        s.add_int(self.distance.max)
        if self._script.version < 7:
            s.add_int(self.relation.min)
            s.add_int(self.relation.max)
            s.add_int(self.deviation)
        s.add_bool(self.is_hole)

    def load(self, s):
        self.end_star = s.get_int()
        if self._script.version < 7:
            self.angle = s.get_int()
        self.distance = MinMax(s.get_int(), s.get_int())
        if self._script.version < 7:
            self.relation = MinMax(s.get_int(), s.get_int())
            self.deviation = s.get_int()
        self.is_hole = s.get_bool()

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
        nbp = BlockPar(sort=False)
        nbp.add("Race", str(self.race))
        nbp.add("Owner", str(self.owner))
        nbp.add("Economy", str(self.economy))
        nbp.add("Government", str(self.government))
        nbp.add("Range", str(self.range))
        nbp.add("Dialog", str(self.dialog))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_uint(int(self.race))
        s.add_uint(int(self.owner))
        s.add_uint(int(self.economy))
        s.add_uint(int(self.government))
        s.add_int(self.range.min)
        s.add_int(self.range.max)
        s.add_widestr(self.dialog)

    def load(self, s):
        self.race = r_(s.get_uint())
        self.owner = o_(s.get_uint())
        self.economy = e_(s.get_uint())
        self.government = g_(s.get_uint())
        self.range = MinMax(s.get_int(), s.get_int())
        self.dialog = s.get_widestr()

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
        nbp = BlockPar(sort=False)
        nbp.add("Count", str(self.count))
        nbp.add("Owner", str(self.owner))
        nbp.add("Type", str(self.type))
        nbp.add("IsPlayer", str(self.is_player))
        nbp.add("Speed", str(self.speed))
        nbp.add("Weapon", str(self.weapon))
        nbp.add("CargoHook", str(self.cargohook))
        nbp.add("EmptySpace", str(self.emptyspace))
        if self._script.version < 7:
            nbp.add("Rating", str(self.rating))
        st = BlockPar(sort=False)
        st.add("Trader", str(self.status.trader))
        st.add("Warrior", str(self.status.warrior))
        st.add("Pirate", str(self.status.pirate))
        nbp.add("Status", st)
        if self._script.version < 7:
            nbp.add("Score", str(self.score))
        nbp.add("Strength", str(self.strength))
        nbp.add("Ruins", str(self.ruins))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_int(self.count)
        s.add_uint(int(self.owner))
        s.add_uint(int(self.type))
        s.add_bool(self.is_player)
        s.add_int(self.speed.min)
        s.add_int(self.speed.max)
        s.add_uint(int(self.weapon))
        s.add_int(self.cargohook)
        s.add_int(self.emptyspace)
        if self._script.version < 7:
            s.add_int(self.rating.min)
            s.add_int(self.rating.max)
        s.add_int(self.status.trader.min)
        s.add_int(self.status.trader.max)
        s.add_int(self.status.warrior.min)
        s.add_int(self.status.warrior.max)
        s.add_int(self.status.pirate.min)
        s.add_int(self.status.pirate.max)
        if self._script.version < 7:
            s.add_int(self.score.min)
            s.add_int(self.score.max)
        s.add_single(self.strength.min)
        s.add_single(self.strength.max)
        s.add_widestr(self.ruins)

    def load(self, s):
        self.count = s.get_int()
        self.owner = o_(s.get_uint())
        self.type = t_(s.get_uint())
        self.is_player = s.get_bool()
        self.speed = MinMax(s.get_int(), s.get_int())
        self.weapon = w_(s.get_uint())
        self.cargohook = s.get_int()
        self.emptyspace = s.get_int()
        if self._script.version < 7:
            self.rating = MinMax(s.get_int(), s.get_int())
        self.status = Status(MinMax(s.get_int(), s.get_int()),
                             MinMax(s.get_int(), s.get_int()),
                             MinMax(s.get_int(), s.get_int()))
        if self._script.version < 7:
            self.score = MinMax(s.get_int(), s.get_int())
        self.strength = MinMax(s.get_single(), s.get_single())
        self.ruins = s.get_widestr()

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
        nbp = BlockPar(sort=False)
        nbp.add("Star", str(self.star))
        nbp.add("Type", str(self.type))
        if self.type is not pt_.FREE:
            nbp.add("Object", str(self.object))
        if self.type is pt_.FREE:
            nbp.add("Angle", str(self.angle))
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            nbp.add("Distance", str(self.distance))
        if self.type is not pt_.IN_PLANET:
            nbp.add("Radius", str(self.radius))
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            nbp.add("Angle", str(self.angle))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.star)
        s.add_uint(int(self.type))
        if self.type is not pt_.FREE:
            s.add_widestr(self.object)
        if self.type is pt_.FREE:
            s.add_single(self.angle)
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            s.add_single(self.distance)
        if self.type is not pt_.IN_PLANET:
            s.add_int(self.radius)
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            s.add_single(self.angle)

    def load(self, s):
        self.star = s.get_widestr()
        self.type = pt_(s.get_uint())
        if self.type is not pt_.FREE:
            self.object = s.get_widestr()
        if self.type is pt_.FREE:
            self.angle = s.get_single()
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            self.distance = s.get_single()
        if self.type is not pt_.IN_PLANET:
            self.radius = s.get_int()
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            self.angle = s.get_single()

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
        nbp = BlockPar(sort=False)
        nbp.add("Place", str(self.place))
        nbp.add("Class", str(self.kind))
        nbp.add("Type", str(self.type))
        nbp.add("Size", str(self.size))
        nbp.add("Level", str(self.level))
        nbp.add("Radius", str(self.radius))
        nbp.add("Owner", str(self.owner))
        nbp.add("Useless", str(self.useless))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.place)
        s.add_uint(int(self.kind))
        s.add_uint(int(self.type))
        s.add_int(self.size)
        s.add_int(self.level)
        s.add_int(self.radius)
        s.add_uint(int(self.owner))
        s.add_widestr(self.useless)

    def load(self, s):
        self.place = s.get_widestr()
        self.kind = ic_(s.get_uint())
        self.type = s.get_uint()
        self.size = s.get_int()
        self.level = s.get_int()
        self.radius = s.get_int()
        self.owner = Race(s.get_uint())
        self.useless = s.get_widestr()

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
        nbp = BlockPar(sort=False)
        nbp.add("Planet", str(self.planet))
        nbp.add("State", str(self.state) + \
                         '(' + str(self._script.states[self.state].name) + ')')
        nbp.add("Owner", str(self.owner))
        nbp.add("Type", str(self.type))
        nbp.add("Count", str(self.count))
        nbp.add("Speed", str(self.speed))
        nbp.add("Weapon", str(self.weapon))
        nbp.add("CargoHook", str(self.cargohook))
        nbp.add("EmptySpace", str(self.emptyspace))
        if self._script.version < 7:
            nbp.add("Friendship", str(self.friendship))
        nbp.add("AddPlayer", str(self.add_player))
        if self._script.version < 7:
            nbp.add("Rating", str(self.rating))
            nbp.add("Score", str(self.score))
        st = BlockPar(sort=False)
        st.add("Trader", str(self.status.trader))
        st.add("Warrior", str(self.status.warrior))
        st.add("Pirate", str(self.status.pirate))
        nbp.add("Status", st)
        nbp.add("SearchDist", str(self.search_distance))
        nbp.add("Dialog", str(self.dialog))
        nbp.add("Strength", str(self.strength))
        nbp.add("Ruins", str(self.ruins))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.planet)
        s.add_int(self.state)
        s.add_uint(int(self.owner))
        s.add_uint(int(self.type))
        s.add_int(self.count.min)
        s.add_int(self.count.max)
        s.add_int(self.speed.min)
        s.add_int(self.speed.max)
        s.add_uint(int(self.weapon))
        s.add_int(self.cargohook)
        s.add_int(self.emptyspace)
        if self._script.version < 7:
            s.add_uint(int(self.friendship))
        s.add_bool(self.add_player)
        if self._script.version < 7:
            s.add_int(self.rating.min)
            s.add_int(self.rating.max)
            s.add_int(self.score.min)
            s.add_int(self.score.max)
        s.add_int(self.status.trader.min)
        s.add_int(self.status.trader.max)
        s.add_int(self.status.warrior.min)
        s.add_int(self.status.warrior.max)
        s.add_int(self.status.pirate.min)
        s.add_int(self.status.pirate.max)
        s.add_int(self.search_distance)
        s.add_widestr(self.dialog)
        s.add_single(self.strength.min)
        s.add_single(self.strength.max)
        s.add_widestr(self.ruins)

    def load(self, s):
        self.planet = s.get_widestr()
        self.state = s.get_int()
        self.owner = o_(s.get_uint())
        self.type = t_(s.get_uint())
        self.count = MinMax(s.get_int(), s.get_int())
        self.speed = MinMax(s.get_int(), s.get_int())
        self.weapon = w_(s.get_uint())
        self.cargohook = s.get_int()
        self.emptyspace = s.get_int()
        if self._script.version < 7:
            self.friendship = f_(s.get_uint())
        self.add_player = s.get_bool()
        if self._script.version < 7:
            self.rating = MinMax(s.get_int(), s.get_int())
            self.score = MinMax(s.get_int(), s.get_int())
        self.status = Status(MinMax(s.get_int(), s.get_int()),
                             MinMax(s.get_int(), s.get_int()),
                             MinMax(s.get_int(), s.get_int()))
        self.search_distance = s.get_int()
        self.dialog = s.get_widestr()
        self.strength = MinMax(s.get_single(), s.get_single())
        self.ruins = s.get_widestr()

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
        nbp = BlockPar(sort=False)
        nbp.add("Begin", str(self.begin))
        nbp.add("End", str(self.end))
        nbp.add("Relations", str(self.relations))
        nbp.add("WarWeight", str(self.war_weight))
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_int(self.begin)
        s.add_int(self.end)
        s.add_int(int(self.relations[0]))
        s.add_int(int(self.relations[1]))
        s.add_single(self.war_weight.min)
        s.add_single(self.war_weight.max)

    def load(self, s):
        self.begin = s.get_int()
        self.end = s.get_int()
        self.relations = (rel_(s.get_uint()), rel_(s.get_uint()))
        self.war_weight = MinMax(s.get_single(), s.get_single())

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
        nbp = BlockPar(sort=False)
        nbp.add("Type", str(self.type))
        if self.type not in (mt_.NONE, mt_.FREE):
            nbp.add("Object", str(self.object))
        attack = BlockPar(sort=False)
        for i, a in enumerate(self.attack):
            attack.add(str(i), str(a))
        nbp.add("Attack", attack)
        nbp.add("TakeItem", str(self.take_item))
        nbp.add("TakeAll", str(self.take_all))
        nbp.add("OutMsg", str(self.out_msg))
        nbp.add("InMsg", str(self.in_msg))
        nbp.add("Ether", str(self.ether))
        nbp.add("Code", self.code)
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_uint(int(self.type))
        if self.type not in (mt_.NONE, mt_.FREE):
            s.add_widestr(self.object)
        s.add_uint(len(self.attack))
        for e in self.attack:
            s.add_widestr(e)
        s.add_widestr(self.take_item)
        s.add_bool(self.take_all)
        s.add_widestr(self.out_msg)
        s.add_widestr(self.in_msg)
        s.add_widestr(self.ether)
        s.add_widestr(self.code)

    def load(self, s):
        self.type = mt_(s.get_uint())
        if self.type not in (mt_.NONE, mt_.FREE):
            self.object = s.get_widestr()
        for i in range(s.get_uint()):
            self.attack.append(s.get_widestr())
        self.take_item = s.get_widestr()
        self.take_all = s.get_bool()
        self.out_msg = s.get_widestr()
        self.in_msg = s.get_widestr()
        self.ether = s.get_widestr()
        self.code = s.get_widestr()

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

        self.code = bp.get_par("Code")


class Dialog(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.code = ""

    def dump(self, bp):
        nbp = BlockPar(sort=False)
        nbp.add("Code", self.code)
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.code)

    def load(self, s):
        self.code = s.get_widestr()

    def restore(self, bp):
        self.code = bp.get_par("Code")


class DialogMsg(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.code = ""

    def dump(self, bp):
        nbp = BlockPar(sort=False)
        nbp.add("Name", str(self.command))
        nbp.add("Code", self.code)
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.command)
        s.add_widestr(self.code)

    def load(self, s):
        self.command = s.get_widestr()
        self.code = s.get_widestr()

    def restore(self, bp):
        self.command = bp.get_par("Name")
        self.code = bp.get_par("Code")


class DialogAnswer(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.answer = ""
        self.code = ""

    def dump(self, bp):
        nbp = BlockPar(sort=False)
        nbp.add("Command", str(self.command))
        nbp.add("Answer", str(self.answer))
        nbp.add("Code", self.code)
        bp.add(str(self.name), nbp)

    def save(self, s):
        s.add_widestr(self.command)
        s.add_widestr(self.answer)
        s.add_widestr(self.code)

    def load(self, s):
        self.command = s.get_widestr()
        self.answer = s.get_widestr().strip()
        self.code = s.get_widestr()

    def restore(self, bp):
        self.command = bp.get_par("Command")
        self.answer = bp.get_par("Answer")
        self.code = bp.get_par("Code")

