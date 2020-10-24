__all__ = [
    "CompiledScript",
]

from abc import ABC, abstractmethod
from typing import List, Tuple, Union, BinaryIO, TextIO

from rangers.io import Stream
from rangers.blockpar import BlockPar
from rscript.file.enums import *
from rscript.file.utils import MinMax, Status, str_to_bool


class CompiledScript:
    supported = (6, 7)

    def __init__(self):
        self.basepath: str = ""
        self.version: int = 6

        self.globalvars: List[Var] = []
        self.globalcode: str = ""
        self.localvars: List[Var] = []
        self.constellations: int = 0
        self.stars: List[Star] = []
        self.places: List[Place] = []
        self.items: List[Item] = []
        self.groups: List[Group] = []
        self.grouplinks: List[GroupLink] = []
        self.initcode: str = ""
        self.turncode: str = ""
        self.dialogbegincode: str = ""
        self.states: List[State] = []
        self.dialogs: List[Dialog] = []
        self.dialog_msgs: List[DialogMsg] = []
        self.dialog_answers: List[DialogAnswer] = []

    def save(self, f: BinaryIO):
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

    def load(self, f: BinaryIO):
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

    def dump(self, f: TextIO):
        bp = BlockPar(sort=False)

        bp.add_par("Version", str(self.version))

        nbp = bp.add_block("GlobalVars", False)
        for e in self.globalvars:
            e.dump(nbp)

        bp.add_par("GlobalCode", self.globalcode)

        nbp = bp.add_block("LocalVars", False)
        for e in self.localvars:
            e.dump(nbp)

        bp.add_par("Constellations", str(self.constellations))

        nbp = bp.add_block("Stars", False)
        for e in self.stars:
            e.dump(nbp)

        nbp = bp.add_block("Places", False)
        for e in self.places:
            e.dump(nbp)

        nbp = bp.add_block("Items", False)
        for e in self.items:
            e.dump(nbp)

        nbp = bp.add_block("Groups", False)
        for e in self.groups:
            e.dump(nbp)

        nbp = bp.add_block("GroupLinks", False)
        for e in self.grouplinks:
            e.dump(nbp)

        bp.add("InitCode", self.initcode)

        bp.add("TurnCode", self.turncode)

        bp.add("DialogBegin", self.dialogbegincode)

        nbp = bp.add_block("States", False)
        for i, e in enumerate(self.states):
            e.dump(nbp)

        nbp = bp.add_block("Dialogs")
        for e in self.dialogs:
            e.dump(nbp)

        nbp = bp.add_block("DialogMsgs", False)
        for e in self.dialog_msgs:
            e.dump(nbp)

        nbp = bp.add_block("DialogAnswers", False)
        for e in self.dialog_answers:
            e.dump(nbp)

        bp.save_txt(f)
        del bp

    def restore(self, f: TextIO):
        root = BlockPar(sort=False)
        root.load_txt(f)

        self.version = int(root.get_par("Version"))

        for name, block in root.get_block("GlobalVars"):
            e = Var(self, name)
            e.restore(block)
            self.globalvars.append(e)

        self.globalcode = root.get_par("GlobalCode")

        for name, block in root.get_block("LocalVars"):
            e = Var(self, name)
            e.restore(block)
            self.localvars.append(e)

        self.constellations = int(root.get_par("Constellations"))

        for name, block in root.get_block("Stars"):
            e = Star(self, name)
            e.restore(block)
            self.stars.append(e)

        for name, block in root.get_block("Places"):
            e = Place(self, name)
            e.restore(block)
            self.places.append(e)

        for name, block in root.get_block("Items"):
            e = Item(self, name)
            e.restore(block)
            self.items.append(e)

        for name, block in root.get_block("Groups"):
            e = Group(self, name)
            e.restore(block)
            self.groups.append(e)

        for name, block in root.get_block("GroupLinks"):
            e = GroupLink(self, name)
            e.restore(block)
            self.grouplinks.append(e)

        self.initcode = root.get_par("InitCode")
        self.turncode = root.get_par("TurnCode")
        self.dialogbegincode = root.get_par("DialogBegin")

        for name, block in root.get_block("States"):
            e = State(self, name)
            e.restore(block)
            self.states.append(e)

        for name, block in root.get_block("Dialogs"):
            e = Dialog(self, name)
            e.restore(block)
            self.dialogs.append(e)

        for name, block in root.get_block("DialogMsgs"):
            e = DialogMsg(self, name)
            e.restore(block)
            self.dialog_msgs.append(e)

        for name, block in root.get_block("DialogAnswers"):
            e = DialogAnswer(self, name)
            e.restore(block)
            self.dialog_answers.append(e)


class CompiledPoint(ABC):
    """
    Элемент скомпилированного скрипта
    """
    
    def __init__(self, script: CompiledScript, name: str = ""):
        self._script = script
        self.name = name

    @abstractmethod
    def save(self, s: Stream):
        """
        Сохраняет элемент скомпилированного скрипта в двоичном представлении

        :param s: файловый поток родительского скрипта
        """
        pass

    @abstractmethod
    def load(self, s: Stream):
        """
        Восстанавливает элемент скомпилированного скрипта из двоичного представления
        
        :param s: файловый поток родительского скрипта
        """
        pass

    @abstractmethod
    def dump(self, root: BlockPar):
        """
        Сохраняет элемент скомпилированного скрипта в дамп в формате блокпар

        :param root: родительский блок дампа
        """
        pass

    @abstractmethod
    def restore(self, source: BlockPar):
        """
        Восстанавливает элемент скомпилированного скрипта из дампа в формате блокпар

        :param source: блок дампа с содержимым элемента
        """
        pass


class Var(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type: var_ = var_(0)
        self.value: Union[int, float, str] = 0

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Type", str(self.type))
        bp.add_par("Value", str(self.value))

    def restore(self, source):
        self.type = var_.from_str(source.get_par("Type"))
        if self.type is var_.INTEGER:
            self.value = int(source.get_par("Value"))
        elif self.type is var_.DWORD:
            self.value = int(source.get_par("Value"))
        elif self.type is var_.FLOAT:
            self.value = float(source.get_par("Value"))
        elif self.type is var_.STRING:
            self.value = source.get_par("Value")
        elif self.type is var_.ARRAY:
            self.value = int(source.get_par("Value"))


class Star(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.constellation: int = 0
        self.is_subspace: bool = False
        self.no_kling: bool = False
        self.no_come_kling: bool = False
        self.starlinks: List[StarLink] = []
        self.planets: List[Planet] = []
        self.ships: List[Ship] = []

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Constellation", str(self.constellation))
        if self._script.version < 7:
            bp.add_par("IsSubspace", str(self.is_subspace))
        bp.add_par("NoKling", str(self.no_kling))
        bp.add_par("NoComeKling", str(self.no_come_kling))

        nbp = bp.add_block("StarLinks", False)
        for sl in self.starlinks:
            sl.dump(nbp)

        nbp = bp.add_block("Planets", False)
        for p in self.planets:
            p.dump(nbp)

        nbp = bp.add_block("Ships", False)
        for s in self.ships:
            s.dump(nbp)

    def restore(self, source):
        self.constellation = int(source.get_par("Constellation"))
        if self._script.version < 7:
            self.is_subspace = str_to_bool(source.get_par("IsSubspace"))
        self.no_kling = str_to_bool(source.get_par("NoKling"))
        self.no_come_kling = str_to_bool(source.get_par("NoComeKling"))

        for name, block in source.get_block("StarLinks"):
            e = StarLink(self._script, name)
            e.restore(block)
            self.starlinks.append(e)

        for name, block in source.get_block("Planets"):
            e = Planet(self._script, name)
            e.restore(block)
            self.planets.append(e)

        for name, block in source.get_block("Ships"):
            e = Ship(self._script, name)
            e.restore(block)
            self.ships.append(e)


class StarLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.end_star: int = 0
        self.angle: int = 0
        self.distance: MinMax[int] = MinMax(0, 0)
        self.relation: MinMax[int] = MinMax(0, 0)
        self.deviation: int = 0
        self.is_hole: bool = False

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("EndStar", str(self._script.stars[self.end_star].name) + \
                              '(' + str(self.end_star) + ')')
        if self._script.version < 7:
            bp.add_par("Angle", str(self.angle))
        bp.add_par("Distance", str(self.distance))
        if self._script.version < 7:
            bp.add_par("Relation", str(self.relation))
            bp.add_par("Deviation", str(self.deviation))
        bp.add_par("IsHole", str(self.is_hole))

    def restore(self, source):
        end_star = source.get_par("EndStar")
        start = end_star.find('(') + 1
        end = end_star.find(')')
        self.end_star = int(end_star[start:end])
        if self._script.version < 7:
            self.angle = int(source.get_par("Angle"))
        self.distance = MinMax.from_str(source.get_par("Distance"), int)
        if self._script.version < 7:
            self.relation = MinMax.from_str(source.get_par("Relation"), int)
            self.deviation = int(source.get_par("Deviation"))
        self.is_hole = str_to_bool(source.get_par("IsHole"))


class Planet(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.race: Race = Race(0)
        self.owner: o_ = o_(0)
        self.economy: e_ = e_(0)
        self.government: g_ = g_(0)
        self.range: MinMax[int] = MinMax(0, 0)
        self.dialog: str = ""

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Race", str(self.race))
        bp.add_par("Owner", str(self.owner))
        bp.add_par("Economy", str(self.economy))
        bp.add_par("Government", str(self.government))
        bp.add_par("Range", str(self.range))
        bp.add_par("Dialog", str(self.dialog))

    def restore(self, source):
        self.race = r_.from_str(source.get_par("Race"))
        self.owner = o_.from_str(source.get_par("Owner"))
        self.economy = e_.from_str(source.get_par("Economy"))
        self.government = g_.from_str(source.get_par("Government"))
        self.range = MinMax.from_str(source.get_par("Range"), int)
        self.dialog = source.get_par("Dialog")


class Ship(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.count: int = 0
        self.owner: o_ = o_(0)
        self.type: t_ = t_(0)
        self.is_player: bool = False
        self.speed: MinMax[int] = MinMax(0, 0)
        self.weapon: w_ = w_(0)
        self.cargohook: int = 0
        self.emptyspace: int = 0
        self.rating: MinMax[int] = MinMax(0, 0)
        self.status: Status = Status(MinMax(0, 0),
                                     MinMax(0, 0),
                                     MinMax(0, 0),)
        self.score: MinMax[int] = MinMax(0, 0)
        self.strength: MinMax[float] = MinMax(0.0, 0.0)
        self.ruins: str = ""

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Count", str(self.count))
        bp.add_par("Owner", str(self.owner))
        bp.add_par("Type", str(self.type))
        bp.add_par("IsPlayer", str(self.is_player))
        bp.add_par("Speed", str(self.speed))
        bp.add_par("Weapon", str(self.weapon))
        bp.add_par("CargoHook", str(self.cargohook))
        bp.add_par("EmptySpace", str(self.emptyspace))
        if self._script.version < 7:
            bp.add_par("Rating", str(self.rating))
        st = bp.add_block("Status", False)
        st.add_par("Trader", str(self.status.trader))
        st.add_par("Warrior", str(self.status.warrior))
        st.add_par("Pirate", str(self.status.pirate))
        if self._script.version < 7:
            bp.add_par("Score", str(self.score))
        bp.add_par("Strength", str(self.strength))
        bp.add_par("Ruins", str(self.ruins))

    def restore(self, source):
        self.count = int(source.get_par("Count"))
        self.owner = o_.from_str(source.get_par("Owner"))
        self.type = t_.from_str(source.get_par("Type"))
        self.is_player = str_to_bool(source.get_par("IsPlayer"))
        self.speed = MinMax.from_str(source.get_par("Speed"), int)
        self.weapon = w_.from_str(source.get_par("Weapon"))
        self.cargohook = int(source.get_par("CargoHook"))
        self.emptyspace = int(source.get_par("EmptySpace"))
        if self._script.version < 7:
            self.rating = MinMax.from_str(source.get_par("Rating"), int)
        status = source.get_block("Status")
        self.status = Status(MinMax.from_str(status.get_par("Trader"), int),
                             MinMax.from_str(status.get_par("Warrior"), int),
                             MinMax.from_str(status.get_par("Pirate"), int))
        del status
        if self._script.version < 7:
            self.score = MinMax.from_str(source.get_par("Score"), int)
        self.strength = MinMax.from_str(source.get_par("Strength"), float)
        self.ruins = source.get_par("Ruins")


class Place(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.star: str = ""
        self.type: pt_ = pt_(0)
        self.object: str = ""
        self.angle: float = 0.0
        self.distance: float = 0.0
        self.radius: int = 0

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Star", str(self.star))
        bp.add_par("Type", str(self.type))
        if self.type is not pt_.FREE:
            bp.add_par("Object", str(self.object))
        if self.type is pt_.FREE:
            bp.add_par("Angle", str(self.angle))
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            bp.add_par("Distance", str(self.distance))
        if self.type is not pt_.IN_PLANET:
            bp.add_par("Radius", str(self.radius))
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            bp.add_par("Angle", str(self.angle))

    def restore(self, source):
        self.star = source.get_par("Star")
        self.type = pt_.from_str(source.get_par("Type"))
        if self.type is not pt_.FREE:
            self.object = source.get_par("Object")
        if self.type is pt_.FREE:
            self.angle = float(source.get_par("Angle"))
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            self.distance = float(source.get_par("Distance"))
        if self.type is not pt_.IN_PLANET:
            self.radius = int(source.get_par("Radius"))
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            self.angle = float(source.get_par("Angle"))


class Item(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.place: str = ""
        self.kind: ic_ = ic_(0)
        self.type: int = 0
        self.size: int = 0
        self.level: int = 0
        self.radius: int = 0
        self.owner: Race = Race(0)
        self.useless: str = ""

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Place", str(self.place))
        bp.add_par("Class", str(self.kind))
        bp.add_par("Type", str(self.type))
        bp.add_par("Size", str(self.size))
        bp.add_par("Level", str(self.level))
        bp.add_par("Radius", str(self.radius))
        bp.add_par("Owner", str(self.owner))
        bp.add_par("Useless", str(self.useless))

    def restore(self, source):
        self.place = source.get_par("Place")
        self.kind = ic_.from_str(source.get_par("Class"))
        self.type = int(source.get_par("Type"))
        self.size = int(source.get_par("Size"))
        self.level = int(source.get_par("Level"))
        self.radius = int(source.get_par("Radius"))
        self.owner = Race.from_str(source.get_par("Owner"))
        self.useless = source.get_par("Useless")


class Group(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.planet: str = ""
        self.state: int = 0
        self.owner: o_ = o_(0)
        self.type: t_ = t_(0)
        self.count: MinMax[int] = MinMax(0, 0)
        self.speed: MinMax[int] = MinMax(0, 0)
        self.weapon: w_ = w_(0)
        self.cargohook: int = 0
        self.emptyspace: int = 0
        self.friendship: f_ = f_(0)
        self.add_player: bool = False
        self.rating: MinMax[int] = MinMax(0, 0)
        self.score: MinMax[int] = MinMax(0, 0)
        self.status: Status = Status(MinMax(0, 0),
                                     MinMax(0, 0),
                                     MinMax(0, 0), )
        self.search_distance: int = 0
        self.dialog: str = ""
        self.strength: MinMax[float] = MinMax(0.0, 0.0)
        self.ruins: str = ""

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Planet", str(self.planet))
        bp.add_par("State", str(self._script.states[self.state].name) + \
                        '(' + str(self.state) + ')')
        bp.add_par("Owner", str(self.owner))
        bp.add_par("Type", str(self.type))
        bp.add_par("Count", str(self.count))
        bp.add_par("Speed", str(self.speed))
        bp.add_par("Weapon", str(self.weapon))
        bp.add_par("CargoHook", str(self.cargohook))
        bp.add_par("EmptySpace", str(self.emptyspace))
        if self._script.version < 7:
            bp.add_par("Friendship", str(self.friendship))
        bp.add_par("AddPlayer", str(self.add_player))
        if self._script.version < 7:
            bp.add_par("Rating", str(self.rating))
            bp.add_par("Score", str(self.score))
        st = bp.add_block("Status", False)
        st.add_par("Trader", str(self.status.trader))
        st.add_par("Warrior", str(self.status.warrior))
        st.add_par("Pirate", str(self.status.pirate))
        bp.add_par("SearchDist", str(self.search_distance))
        bp.add_par("Dialog", str(self.dialog))
        bp.add_par("Strength", str(self.strength))
        bp.add_par("Ruins", str(self.ruins))

    def restore(self, source):
        self.planet = source.get_par("Planet")
        state = source.get_par("State")
        start = state.find('(') + 1
        end = state.find(')')
        self.state = int(state[start:end])
        self.owner = o_.from_str(source.get_par("Owner"))
        self.type = t_.from_str(source.get_par("Type"))
        self.count = MinMax.from_str(source.get_par("Count"), int)
        self.speed = MinMax.from_str(source.get_par("Speed"), int)
        self.weapon = w_.from_str(source.get_par("Weapon"))
        self.cargohook = int(source.get_par("CargoHook"))
        self.emptyspace = int(source.get_par("EmptySpace"))
        if self._script.version < 7:
            self.friendship = f_.from_str(source.get_par("Friendship"))
        self.add_player = str_to_bool(source.get_par("AddPlayer"))
        if self._script.version < 7:
            self.rating = MinMax.from_str(source.get_par("Rating"), int)
            self.score = MinMax.from_str(source.get_par("Score"), int)
        status = source.get_block("Status")
        self.status = Status(MinMax.from_str(status.get_par("Trader"), int),
                             MinMax.from_str(status.get_par("Warrior"), int),
                             MinMax.from_str(status.get_par("Pirate"), int))
        del status
        self.search_distance = int(source.get_par("SearchDist"))
        self.dialog = source.get_par("Dialog")
        self.strength = MinMax.from_str(source.get_par("Strength"), float)
        self.ruins = source.get_par("Ruins")


class GroupLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.begin: int = 0
        self.end: int = 0
        self.relations: Tuple[rel_, rel_] = (rel_(0), rel_(0))
        self.war_weight: MinMax[float] = MinMax(0.0, 0.0)

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Begin", str(self.begin))
        bp.add_par("End", str(self.end))
        bp.add_par("Relations", str(self.relations))
        bp.add_par("WarWeight", str(self.war_weight))

    def restore(self, source):
        self.begin = int(source.get_par("Begin"))
        self.end = int(source.get_par("End"))
        relations = source.get_par("Relations").strip('()').split(',')
        self.relations = (rel_.from_str(relations[0].strip()),
                          rel_.from_str(relations[1].strip()))
        self.war_weight = MinMax.from_str(source.get_par("WarWeight"), float)


class State(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type: mt_ = mt_(0)
        self.object = ""
        self.attack: List[str] = []
        self.take_item: str = ""
        self.take_all: bool = False
        self.out_msg: str = ""
        self.in_msg: str = ""
        self.ether: str = ""
        self.code: str = ""

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

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Type", str(self.type))
        if self.type not in (mt_.NONE, mt_.FREE):
            bp.add_par("Object", str(self.object))
        attack = bp.add_block("Attack", False)
        for i, a in enumerate(self.attack):
            attack.add_par(str(i), str(a))
        bp.add_par("TakeItem", str(self.take_item))
        bp.add_par("TakeAll", str(self.take_all))
        bp.add_par("OutMsg", str(self.out_msg))
        bp.add_par("InMsg", str(self.in_msg))
        bp.add_par("Ether", str(self.ether))
        bp.add_par("Code", self.code)

    def restore(self, source):
        self.type = mt_.from_str(source.get_par("Type"))
        if self.type not in (mt_.NONE, mt_.FREE):
            self.object = source.get_par("Object")
        for par in source.get_block("Attack"):
            self.attack.append(par.content)
        self.take_item = source.get_par("TakeItem")
        self.take_all = str_to_bool(source.get_par("TakeAll"))
        self.out_msg = source.get_par("OutMsg")
        self.in_msg = source.get_par("InMsg")
        self.ether = source.get_par("Ether")

        self.code = source.get_par("Code")


class Dialog(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.code: str = ""

    def save(self, s):
        s.add_widestr(self.code)

    def load(self, s):
        self.code = s.get_widestr()

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Code", self.code)

    def restore(self, source):
        self.code = source.get_par("Code")


class DialogMsg(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command: str = ""
        self.code: str = ""

    def save(self, s):
        s.add_widestr(self.command)
        s.add_widestr(self.code)

    def load(self, s):
        self.command = s.get_widestr()
        self.code = s.get_widestr()

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Name", str(self.command))
        bp.add_par("Code", self.code)

    def restore(self, source):
        self.command = source.get_par("Name")
        self.code = source.get_par("Code")


class DialogAnswer(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command: str = ""
        self.answer: str = ""
        self.code: str = ""

    def save(self, s):
        s.add_widestr(self.command)
        s.add_widestr(self.answer)
        s.add_widestr(self.code)

    def load(self, s):
        self.command = s.get_widestr()
        self.answer = s.get_widestr().strip()
        self.code = s.get_widestr()

    def dump(self, root):
        bp = root.add_block(str(self.name), False)
        bp.add_par("Command", str(self.command))
        bp.add_par("Answer", str(self.answer))
        bp.add_par("Code", self.code)

    def restore(self, source):
        self.command = source.get_par("Command")
        self.answer = source.get_par("Answer")
        self.code = source.get_par("Code")
