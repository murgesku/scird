__all__ = [
    "CompiledScript",
]

import blockpar
import stream
from enums import *
from utils import MinMax


class CompiledScript:
    version = 6

    def __init__(self):
        self.globalvars = []
        self.globalcode = ""
        self.localvars = []
        self.constellations = 0
        self.stars = []
        self.places = []
        self.items = []
        self.groups = []
        self.grouplinks = []
        self.initcode = ""
        self.turncode = ""
        self.dialogbegincode = ""
        self.states = []
        self.dialogs = []
        self.dialog_msgs = []
        self.dialog_answers = []

    def load(self, f):
        s = stream.from_io(f)

        s.seek(0)

        if s.read_uint() != self.version:
            s.close()
            return

        s.read_uint()

        for i in range(s.read_uint()):
            e = Var(self, s.read_widestr())

            e.type = var_(s.read_byte())
            if e.type is var_.INTEGER:
                e.value = s.read_int()
            elif e.type is var_.DWORD:
                e.value = s.read_uint()
            elif e.type is var_.FLOAT:
                e.value = s.read_double()
            elif e.type is var_.STRING:
                e.value = s.read_widestr()

            self.globalvars.append(e)

        self.globalcode = s.read_widestr()

        for i in range(s.read_uint()):
            e = Var(self, s.read_widestr())

            e.type = var_(s.read_byte())
            if e.type is var_.INTEGER:
                e.value = s.read_int()
            elif e.type is var_.DWORD:
                e.value = s.read_uint()
            elif e.type is var_.FLOAT:
                e.value = s.read_double()
            elif e.type is var_.STRING:
                e.value = s.read_widestr()

            self.localvars.append(e)

        self.constellations = s.read_uint()

        for i in range(s.read_uint()):
            e = Star(self, s.read_widestr())

            e.constellation = s.read_int()
            e.is_subspace = s.read_bool()
            e.no_kling = s.read_bool()
            e.no_come_kling = s.read_bool()

            for j in range(s.read_uint()):
                ee = StarLink(self, str(j))
                ee.end_star = s.read_int()
                ee.angle = s.read_int()
                ee.distance = MinMax(s.read_int(), s.read_int())
                ee.relation = MinMax(s.read_int(), s.read_int())
                ee.deviation = s.read_int()
                ee.is_hole = s.read_bool()
                e.starlinks.append(ee)

            for j in range(s.read_uint()):
                ee = Planet(self, s.read_widestr())
                ee.race = r_(s.read_uint())
                ee.owner = o_(s.read_uint())
                ee.economy = e_(s.read_uint())
                ee.government = g_(s.read_uint())
                ee.range = MinMax(s.read_int(), s.read_int())
                ee.dialog = s.read_widestr()
                e.planets.append(ee)

            for j in range(s.read_uint()):
                ee = Ship(self, str(j))
                ee.count = s.read_uint()
                ee.owner = o_(s.read_uint())
                ee.type = t_(s.read_uint())
                ee.is_player = s.read_bool()
                ee.speed = MinMax(s.read_int(), s.read_int())
                ee.weapon = w_(s.read_uint())
                ee.cargohook = s.read_uint()
                ee.emptyspace = s.read_int()
                ee.rating = MinMax(s.read_int(), s.read_int())
                ee.status = Status(MinMax(s.read_int(), s.read_int()),
                                   MinMax(s.read_int(), s.read_int()),
                                   MinMax(s.read_int(), s.read_int()))
                ee.score = MinMax(s.read_int(), s.read_int())
                ee.strength = MinMax(s.read_single(), s.read_single())
                ee.ruins = s.read_widestr()
                e.ships.append(ee)

            self.stars.append(e)

        for i in range(s.read_uint()):
            e = Place(self, s.read_widestr())

            e.star = s.read_widestr()
            e.type = pt_(s.read_uint())
            if e.type is not pt_.FREE:
                e.object = s.read_widestr()
            if e.type is pt_.FREE:
                e.angle = s.read_single()
            if e.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
                e.distance = s.read_single()
            if e.type is not pt_.IN_PLANET:
                e.radius = s.read_int()
            if e.type in (pt_.TO_STAR, pt_.FROM_SHIP):
                e.angle = s.read_single()

            self.places.append(e)

        for i in range(s.read_uint()):
            e = Item(self, s.read_widestr())

            e.place = s.read_widestr()
            e.kind = ic_(s.read_uint())
            e.type = s.read_uint()
            e.size = s.read_int()
            e.level = s.read_int()
            e.radius = s.read_int()
            e.owner = Race(s.read_uint())
            e.useless = s.read_widestr()

            self.items.append(e)

        for i in range(s.read_uint()):
            e = Group(self, s.read_widestr())

            e.planet = s.read_widestr()
            e.state = s.read_int()
            e.owner = o_(s.read_uint())
            e.type = t_(s.read_uint())
            e.count = MinMax(s.read_int(), s.read_int())
            e.speed = MinMax(s.read_int(), s.read_int())
            e.weapon = w_(s.read_uint())
            e.cargohook = s.read_uint()
            e.emptyspace = s.read_int()
            e.friendship = f_(s.read_uint())
            e.add_player = s.read_bool()
            e.rating = MinMax(s.read_int(), s.read_int())
            e.score = MinMax(s.read_int(), s.read_int())
            e.status = Status(MinMax(s.read_int(), s.read_int()),
                              MinMax(s.read_int(), s.read_int()),
                              MinMax(s.read_int(), s.read_int()))
            e.search_distance = s.read_int()
            e.dialog = s.read_widestr()
            e.strength = MinMax(s.read_single(), s.read_single())
            e.ruins = s.read_widestr()

            self.groups.append(e)

        for i in range(s.read_uint()):
            e = GroupLink(self, str(i))

            e.begin = s.read_int()
            e.end = s.read_int()
            e.relations = (rel_(s.read_uint()), rel_(s.read_uint()))
            e.war_weight = MinMax(s.read_single(), s.read_single())

            self.grouplinks.append(e)

        self.initcode = s.read_widestr()
        self.turncode = s.read_widestr()
        self.dialogbegincode = s.read_widestr()

        for i in range(s.read_uint()):
            e = State(self, s.read_widestr())

            e.type = mt_(s.read_uint())
            if e.type not in (mt_.NONE, mt_.FREE):
                e.object = s.read_widestr()
            for j in range(s.read_uint()):
                e.attack.append(s.read_widestr())
            e.take_item = s.read_widestr()
            e.take_all = s.read_bool()
            e.out_msg = s.read_widestr()
            e.int_msg = s.read_widestr()
            e.ether = s.read_widestr()
            e.code = s.read_widestr()

            self.states.append(e)

        for i in range(s.read_uint()):
            e = Dialog(self, s.read_widestr())

            e.code = s.read_widestr()

            self.dialogs.append(e)

        for i in range(s.read_uint()):
            e = DialogMsg(self, str(i))

            e.command = s.read_widestr()
            e.code = s.read_widestr()

            self.dialog_msgs.append(e)

        for i in range(s.read_uint()):
            e = DialogAnswer(self, str(i))

            e.command = s.read_widestr()
            e.answer = s.read_widestr().strip()
            e.code = s.read_widestr()

            self.dialog_answers.append(e)

    def dump(self, f):
        bp = blockpar.BlockPar(sort=False)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.globalvars:
            e.dump(nbp)
        bp["globalvars"] = nbp

        bp["globalcode"] = blockpar.from_code(self.globalcode)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.localvars:
            e.dump(nbp)
        bp["localvars"] = nbp

        bp["constellations"] = str(self.constellations)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.stars:
            e.dump(nbp)
        bp["stars"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.places:
            e.dump(nbp)
        bp["places"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.items:
            e.dump(nbp)
        bp["items"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.groups:
            e.dump(nbp)
        bp["groups"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.grouplinks:
            e.dump(nbp)
        bp["grouplinks"] = nbp

        bp["initcode"] = blockpar.from_code(self.initcode)
        bp["turncode"] = blockpar.from_code(self.turncode)
        bp["dialogbegincode"] = blockpar.from_code(self.dialogbegincode)

        nbp = blockpar.BlockPar(sort=False)
        for e in self.states:
            e.dump(nbp)
        bp["states"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialogs:
            e.dump(nbp)
        bp["dialogs"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialog_msgs:
            e.dump(nbp)
        bp["dialog_msgs"] = nbp

        nbp = blockpar.BlockPar(sort=False)
        for e in self.dialog_answers:
            e.dump(nbp)
        bp["dialog_answers"] = nbp

        bp.save_txt(f)
        del bp


class Status:
    __slots__ = "trader", "warrior", "pirate"

    def __init__(self, trader, warrior, pirate):
        self.trader = trader
        self.warrior = warrior
        self.pirate = pirate

    def to_blockpar(self):
        bp = blockpar.BlockPar(sort=False)
        bp["trader"] = str(self.trader)
        bp["warrior"] = str(self.warrior)
        bp["pirate"] = str(self.pirate)
        return bp


class CompiledPoint:
    def __init__(self, script, name=""):
        """
        :type script: CompiledScript
        """
        self._script = script
        self.name = name

    def dump(self, bp):
        """
        :type bp: blockpar.BlockPar
        """
        pass


class Var(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type = None
        self.value = None

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["type"] = str(self.type)
        nbp["value"] = str(self.value)
        bp[str(self.name)] = nbp


class Star(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.constellation = 0
        self.is_subspace = False
        self.no_kling = False
        self.no_come_kling = False
        self.starlinks = []
        self.planets = []
        self.ships = []

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["constellation"] = str(self.constellation)
        nbp["is_subspace"] = str(self.is_subspace)
        nbp["no_kling"] = str(self.no_kling)
        nbp["no_come_kling"] = str(self.no_come_kling)

        nnbp = blockpar.BlockPar(sort=False)
        for sl in self.starlinks:
            sl.dump(nnbp)
        nbp["starlinks"] = nnbp

        nnbp = blockpar.BlockPar(sort=False)
        for p in self.planets:
            p.dump(nnbp)
        nbp["planets"] = nnbp

        nnbp = blockpar.BlockPar(sort=False)
        for s in self.ships:
            s.dump(nnbp)
        nbp["ships"] = nnbp

        bp[str(self.name)] = nbp


class StarLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.end_star = 0
        self.angle = 0
        self.distance = None
        self.relation = None
        self.deviation = None
        self.is_hole = None

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["end_star"] = str(self._script.stars[self.end_star].name) + \
                          '(' + str(self.end_star) + ')'
        nbp["angle"] = str(self.angle)
        nbp["distance"] = str(self.distance)
        nbp["relation"] = str(self.relation)
        nbp["deviation"] = str(self.deviation)
        nbp["is_hole"] = str(self.is_hole)
        bp[str(self.name)] = nbp


class Planet(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.race = None
        self.owner = None
        self.economy = None
        self.government = None
        self.range = None
        self.dialog = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["race"] = str(self.race)
        nbp["owner"] = str(self.owner)
        nbp["economy"] = str(self.economy)
        nbp["government"] = str(self.government)
        nbp["range"] = str(self.range)
        nbp["dialog"] = str(self.dialog)
        bp[str(self.name)] = nbp


class Ship(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.count = 0
        self.owner = None
        self.type = None
        self.is_player = False
        self.speed = None
        self.weapon = None
        self.cargohook = 0
        self.emptyspace = 0
        self.rating = None
        self.status = None
        self.score = None
        self.strength = None
        self.ruins = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["count"] = str(self.count)
        nbp["owner"] = str(self.owner)
        nbp["type"] = str(self.type)
        nbp["is_player"] = str(self.is_player)
        nbp["speed"] = str(self.speed)
        nbp["weapon"] = str(self.weapon)
        nbp["cargohook"] = str(self.cargohook)
        nbp["emptyspace"] = str(self.emptyspace)
        nbp["rating"] = str(self.rating)
        nbp["status"] = self.status.to_blockpar()
        nbp["score"] = str(self.score)
        nbp["strength"] = str(self.strength)
        nbp["ruins"] = str(self.ruins)
        bp[str(self.name)] = nbp


class Place(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.star = ""
        self.type = None
        self.object = ""
        self.angle = 0.0
        self.distance = 0.0
        self.radius = 0

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["star"] = str(self.star)
        nbp["type"] = str(self.type)
        if self.type is not pt_.FREE:
            nbp["object"] = str(self.object)
        if self.type is pt_.FREE:
            nbp["angle"] = str(self.angle)
        if self.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            nbp["distance"] = str(self.distance)
        if self.type is not pt_.IN_PLANET:
            nbp["radius"] = str(self.radius)
        if self.type in (pt_.TO_STAR, pt_.FROM_SHIP):
            nbp["angle"] = str(self.angle)
        bp[str(self.name)] = nbp


class Item(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.place = ""
        self.kind = None
        self.type = None
        self.size = 0
        self.level = 0
        self.radius = 0
        self.owner = None
        self.useless = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["place"] = str(self.place)
        nbp["class"] = str(self.kind)
        nbp["type"] = str(self.type)
        nbp["size"] = str(self.size)
        nbp["level"] = str(self.level)
        nbp["radius"] = str(self.radius)
        nbp["owner"] = str(self.owner)
        nbp["useless"] = str(self.useless)
        bp[str(self.name)] = nbp


class Group(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.planet = ""
        self.state = 0
        self.owner = None
        self.type = None
        self.count = None
        self.speed = None
        self.weapon = None
        self.cargohook = 0
        self.emptyspace = 0
        self.friendship = None
        self.add_player = False
        self.rating = None
        self.score = None
        self.status = None
        self.search_distance = 0
        self.dialog = ""
        self.strength = None
        self.ruins = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["planet"] = str(self.planet)
        nbp["state"] = str(self._script.states[self.state].name) + \
                       '(' + str(self.state) + ')'
        nbp["owner"] = str(self.owner)
        nbp["type"] = str(self.type)
        nbp["count"] = str(self.count)
        nbp["speed"] = str(self.speed)
        nbp["weapon"] = str(self.weapon)
        nbp["cargohook"] = str(self.cargohook)
        nbp["emptyspace"] = str(self.emptyspace)
        nbp["friendship"] = str(self.friendship)
        nbp["add_player"] = str(self.add_player)
        nbp["rating"] = str(self.rating)
        nbp["score"] = str(self.score)
        nbp["status"] = self.status.to_blockpar()
        nbp["search_distance"] = str(self.search_distance)
        nbp["dialog"] = str(self.dialog)
        nbp["strength"] = str(self.strength)
        nbp["ruins"] = str(self.ruins)
        bp[str(self.name)] = nbp


class GroupLink(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.begin = 0
        self.end = 0
        self.relations = None
        self.war_weight = None

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["begin"] = str(self.begin)
        nbp["end"] = str(self.end)
        nbp["relations"] = str(self.relations)
        nbp["war_weight"] = str(self.war_weight)
        bp[str(self.name)] = nbp


class State(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.type = None
        self.object = ""
        self.attack = []
        self.take_item = ""
        self.take_all = False
        self.out_msg = ""
        self.in_msg = ""
        self.ether = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["type"] = str(self.type)
        if self.type not in (mt_.NONE, mt_.FREE):
            nbp["object"] = str(self.object)
        attack = blockpar.BlockPar(sort=False)
        for i, a in enumerate(self.attack):
            attack[str(i)] = str(a)
        nbp["attack"] = attack
        nbp["take_item"] = str(self.take_item)
        nbp["take_all"] = str(self.take_all)
        nbp["out_msg"] = str(self.out_msg)
        nbp["in_msg"] = str(self.in_msg)
        nbp["ether"] = str(self.ether)
        nbp["code"] = blockpar.from_code(self.code)
        bp[str(self.name)] = nbp


class Dialog(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["code"] = blockpar.from_code(self.code)
        bp[str(self.name)] = nbp


class DialogMsg(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["command"] = str(self.command)
        nbp["code"] = blockpar.from_code(self.code)
        bp[str(self.name)] = nbp


class DialogAnswer(CompiledPoint):
    def __init__(self, script, name):
        super().__init__(script, name)
        self.command = ""
        self.answer = ""
        self.code = ""

    def dump(self, bp):
        nbp = blockpar.BlockPar(sort=False)
        nbp["command"] = str(self.command)
        nbp["answer"] = str(self.answer)
        nbp["code"] = blockpar.from_code(self.code)
        bp[str(self.name)] = nbp
