__all__ = [
    "SourceScript",
    "Star", "StarLink", "Planet", "Ship",
    "Item", "Place", "Group", "GroupLink",
    "State", "StateLink", "Ether",
    "ExprIf", "ExprOp", "ExprVar", "ExprWhile",
    "Dialog", "DialogMsg", "DialogAnswer",
]

import stream
from blockpar import BlockPar
from enums import *
from utils import *
from rscript.file.scr import Status


class SourceScript:
    version = 6

    def __init__(self):
        self.viewpos = Point(0, 0)
        self.name = ""
        self.filename = ""

        self.textfilenames = BlockPar(sort=False)
        self.textfilenames["rus"] = ""
        self.translations = BlockPar(sort=False)
        self.translations_id = BlockPar(sort=False)

        self.graphpoints = []
        self.graphlinks = []
        self.graphrects = []

    def add(self, cls, pos=None):
        if not pos:
            pos = random_point()
        gp = cls(self, pos)
        self.graphpoints.append(gp)
        return gp

    def link(self, begin, end):
        if isinstance(begin, Star) and isinstance(end, Star):
            gl = StarLink(self, begin, end)
        elif isinstance(begin, Group) and isinstance(end, Group):
            gl = GroupLink(self, begin, end)
        elif isinstance(begin, State) and isinstance(end, State):
            gl = StateLink(self, begin, end)
        else:
            gl = GraphLink(self, begin, end)
        self.graphlinks.append(gl)
        # end.pos = near_point(begin.pos)
        return gl

    def find(self, name):
        if name == "": return None
        for gp in self.graphpoints:
            if gp.text == name:
                return gp
        return None

    def index(self, gp):
        if isinstance(gp, str):
            gp = self.find(gp)
        if not gp:
            return -1
        return self.graphpoints.index(gp)

    def save(self, f):
        s = stream.from_io(f)

        s.write(b'\x55\x44\x33\x22')
        s.write_uint(self.version)
        s.write_int(self.viewpos.x)
        s.write_int(self.viewpos.y)
        s.write_widestr(self.name)
        s.write_widestr(self.filename)
        self.textfilenames.save(s)
        self.translations.save(s)
        self.translations_id.save(s)
        s.write_uint(len(self.graphpoints))
        for gp in self.graphpoints:
            gp.save(s)
        s.write_uint(len(self.graphlinks))
        for gl in self.graphlinks:
            gl.save(s)
        s.write_uint(len(self.graphrects))
        for gr in self.graphrects:
            gr.dump(s)


def save_to(source, path=''):
    if not path:
        if source.filename:
            path = source.filename
        else:
            path = "Source.svr"
    with open(path, 'wb') as f:
        source.save(f)


class GraphPoint(object):
    classname = "TGraphPoint"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        self._script = script
        self.pos = pos
        self.text = text
        self.parent = parent

    def save(self, s):
        s.write_widestr(self.classname)
        s.write_int(self.pos.x)
        s.write_int(self.pos.y)
        s.write_widestr(self.text)
        s.write_int(-1)


class GraphLink(object):
    classname = "TGraphLink"

    def __init__(self, script, begin=None, end=None, ord_num=0, has_arrow=True):
        self._script = script
        self.begin = begin  # graphpoint
        self.end = end  # graphpoint
        self.ord_num = ord_num
        self.has_arrow = has_arrow

    def save(self, s):
        s.write_widestr(self.classname)
        s.write_int(self._script.index(self.begin))
        s.write_int(self._script.index(self.end))
        s.write_uint(self.ord_num)
        s.write_bool(self.has_arrow)


class GraphRect(object):
    classname = "TGraphRectText"

    def __init__(self, script, rect=Rect(0,0,0,0), text=""):
        self._script = script
        self.rect = rect
        self.fill_style = 0  # bsSolid
        self.fill_color = rgb_to_dword(34, 111, 163)
        self.border_style = 0  # psSolid
        self.border_color = rgb_to_dword(220, 220, 220)
        self.border_size = 1
        self.border_coef = 0.3
        self.text_align_x = 0
        self.text_align_y = 0
        self.text_align_rect = False
        self.text = text
        self.text_color = rgb_to_dword(255, 255, 255)
        self.font = "Arial"
        self.font_size = 10
        self.is_bold = False
        self.is_italic = False
        self.is_underline = False

    def save(self, s):
        s.write_widestr(self.classname)
        s.write_int(self.rect.top)
        s.write_int(self.rect.left)
        s.write_int(self.rect.right)
        s.write_int(self.rect.bottom)
        s.write_byte(self.fill_style)
        s.write_uint(self.fill_color)
        s.write_byte(self.border_style)
        s.write_uint(self.border_color)
        s.write_uint(self.border_size)
        s.write_single(self.border_coef)
        s.write_uint(self.text_align_x)
        s.write_uint(self.text_align_y)
        s.write_bool(self.text_align_rect)
        s.write_widestr(self.text)
        s.write_uint(self.text_color)
        s.write_widestr(self.font)
        s.write_uint(self.font_size)
        s.write_bool(self.is_bold)
        s.write_bool(self.is_italic)
        s.write_bool(self.is_underline)


class Star(GraphPoint):
    classname = "TStar"

    def __init__(self, script, pos=Point(0, 0), text="StarNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.constellation = 0
        self.priority = 0
        self.is_subspace = False
        self.no_kling = False
        self.no_come_kling = False

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(self.constellation)
        s.write_uint(self.priority)
        s.write_bool(self.is_subspace)
        s.write_bool(self.no_kling)
        s.write_bool(self.no_come_kling)


class Planet(GraphPoint):
    classname = "TPlanet"

    def __init__(self, script, pos=Point(0, 0), text="PlanetNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.race = r_(0b00111110)  # r
        self.owner = o_(0b00111110)  # o
        self.economy = e_(0b00001110)  # e
        self.government = g_(0b00111110)  # g
        self.range = MinMax(0, 100)
        self.dialog = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(int(self.race))
        s.write_uint(int(self.owner))
        s.write_uint(int(self.economy))
        s.write_uint(int(self.government))
        s.write_int(self.range.min)
        s.write_int(self.range.max)
        s.write_int(self._script.index(self.dialog))


class Ship(GraphPoint):
    classname = "TStarShip"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.count = 1
        self.owner = o_(0b00111110)  # o
        self.type = t_(0b01111110)  # t
        self.is_player = False
        self.speed = MinMax(0, 10000)
        self.weapon = 0
        self.cargohook = 0
        self.emptyspace = 0
        self.rating = MinMax(0, 1000)
        self.status = Status(MinMax(0, 100),
                             MinMax(0, 100),
                             MinMax(0, 100))
        self.score = MinMax(0, 1000000)
        self.strength = MinMax(0, 0)
        self.ruins = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_int(self.count)
        s.write_uint(int(self.owner))
        s.write_uint(int(self.type))
        s.write_bool(self.is_player)
        s.write_int(self.speed.min)
        s.write_int(self.speed.max)
        s.write_uint(self.weapon)
        s.write_uint(self.cargohook)
        s.write_int(self.emptyspace)
        s.write_int(self.rating.min)
        s.write_int(self.rating.max)
        s.write_int(self.status.trader.min)
        s.write_int(self.status.trader.max)
        s.write_int(self.status.warrior.min)
        s.write_int(self.status.warrior.max)
        s.write_int(self.status.pirate.min)
        s.write_int(self.status.pirate.max)
        s.write_int(self.score.min)
        s.write_int(self.score.max)
        s.write_single(self.strength.min)
        s.write_single(self.strength.max)
        s.write_widestr(self.ruins)


class Item(GraphPoint):
    classname = "TItem"

    def __init__(self, script, pos=Point(0, 0), text="ItemNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.kind = 0  # ic
        self.type = 0  # Equipment, Weapon, Goods, Artefact
        self.size = 10
        self.level = 1
        self.radius = 150
        self.owner = Race.MALOC
        self.useless = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(self.kind)
        s.write_uint(self.type)
        s.write_int(self.size)
        s.write_uint(self.level)
        s.write_int(self.radius)
        s.write_uint(int(self.owner))
        s.write_widestr(self.useless)


class Place(GraphPoint):
    classname = "TPlace"

    def __init__(self, script, pos=Point(0, 0), text="PlaceNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.type = 0  # pt
        self.angle = 0  # 0..360
        self.dist = 0.5  # 0..1
        self.radius = 300  # in pixels
        self.obj = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(self.type)
        s.write_single(self.angle)
        s.write_single(self.dist)
        s.write_int(self.radius)
        s.write_int(self._script.index(self.obj))


class Group(GraphPoint):
    classname = "TGroup"

    def __init__(self, script, pos=Point(0, 0), text="GroupNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.owner = o_(0b00111110)  # o
        self.type = t_(0b01111110)  # t
        self.count = MinMax(2, 3)
        self.speed = MinMax(100, 10000)
        self.weapon = w_.UNDEF  # w
        self.cargohook = 0
        self.emptyspace = 0
        self.friendship = f_.FREE  # f
        self.add_player = False
        self.rating = MinMax(0, 1000)
        self.status = Status(MinMax(0, 100),
                             MinMax(0, 100),
                             MinMax(0, 100))
        self.score = MinMax(0, 1000000)
        self.search_dist = 10000
        self.dialog = ""
        self.strength = MinMax(0, 0)
        self.ruins = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(int(self.owner))
        s.write_uint(int(self.type))
        s.write_int(self.count.min)
        s.write_int(self.count.max)
        s.write_int(self.speed.min)
        s.write_int(self.speed.max)
        s.write_uint(int(self.weapon))
        s.write_uint(self.cargohook)
        s.write_int(self.emptyspace)
        s.write_uint(int(self.friendship))
        s.write_bool(self.add_player)
        s.write_int(self.rating.min)
        s.write_int(self.rating.max)
        s.write_int(self.status.trader.min)
        s.write_int(self.status.trader.max)
        s.write_int(self.status.warrior.min)
        s.write_int(self.status.warrior.max)
        s.write_int(self.status.pirate.min)
        s.write_int(self.status.pirate.max)
        s.write_int(self.score.min)
        s.write_int(self.score.max)
        s.write_int(self.search_dist)
        s.write_int(self._script.index(self.dialog))
        s.write_single(self.strength.min)
        s.write_single(self.strength.max)
        s.write_widestr(self.ruins)


class State(GraphPoint):
    classname = "TState"

    def __init__(self, script, pos=Point(0, 0), text="StateNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.type = mt_.NONE  # mt
        self.obj = ""
        self.attack_groups = []
        self.item = ""
        self.take_all = False
        self.out_msg = ""
        self.in_msg = ""
        self.ether_type = et_.GALAXY  # et, 0 or 1
        self.ether_uid = ""
        self.ether_msg = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(self.type)
        s.write_int(self._script.index(self.obj))
        s.write_uint(len(self.attack_groups))
        for ag in self.attack_groups:
            s.write_int(self._script.index(ag))
        s.write_int(self._script.index(self.item))
        s.write_bool(self.take_all)
        s.write_widestr(self.out_msg)
        s.write_widestr(self.in_msg)
        s.write_uint(int(self.ether_type))
        s.write_widestr(self.ether_uid)
        s.write_widestr(self.ether_msg)


class ExprOp(GraphPoint):
    classname = "Top"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_widestr(self.expression)
        s.write_byte(int(self.type))


class ExprIf(GraphPoint):
    classname = "Tif"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_widestr(self.expression)
        s.write_byte(int(self.type))


class ExprWhile(GraphPoint):
    classname = "Twhile"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_widestr(self.expression)
        s.write_byte(int(self.type))


class ExprVar(GraphPoint):
    classname = "TVar"

    def __init__(self, script, pos=Point(0, 0), text="VarNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.type = svar_.UNKNOWN  # svar
        self.init_value = ""
        self.is_global = False

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(int(self.type))
        s.write_widestr(self.init_value)
        s.write_bool(self.is_global)


class Ether(GraphPoint):
    classname = "TEther"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.type = et_.ETHER  # et
        self.uid = ""
        self.msg = ""
        self.focus = ["", "", ""]

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_uint(int(self.type))
        s.write_widestr(self.uid)
        s.write_widestr(self.msg)
        for f in self.focus:
            s.write_widestr(f)


class Dialog(GraphPoint):
    classname = "TDialog"

    def __init__(self, script, pos=Point(0, 0), text="DialogNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)

    def save(self, s):
        GraphPoint.save(self, s)


class DialogMsg(GraphPoint):
    classname = "TDialogMsg"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.msg = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_widestr(self.msg)


class DialogAnswer(GraphPoint):
    classname = "TDialogAnswer"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.msg = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.write_widestr(self.msg)


class StarLink(GraphLink):
    classname = "TStarLink"

    def __init__(self, script, begin=None, end=None, ord_num=0,
                 has_arrow=False):
        GraphLink.__init__(self, script, begin, end, ord_num, has_arrow)
        self.dist = MinMax(0, 150)
        self.deviation = 25
        self.relation = MinMax(0, 100)
        self.is_hole = False

    def save(self, s):
        GraphLink.save(self, s)
        s.write_int(self.dist.min)
        s.write_int(self.dist.max)
        s.write_int(self.deviation)
        s.write_int(self.relation.min)
        s.write_int(self.relation.max)
        s.write_bool(self.is_hole)


class GroupLink(GraphLink):
    classname = "TGroupLink"

    def __init__(self, script, begin=None, end=None, ord_num=0,
                 has_arrow=True):
        GraphLink.__init__(self, script, begin, end, ord_num, has_arrow)
        self.relations = (rel_.NOCHANGE, rel_.NOCHANGE)
        self.war_weight = MinMax(0.0, 1000.0)

    def save(self, s):
        GraphLink.save(self, s)
        for r in self.relations:
            s.write_uint(int(r))
        s.write_single(self.war_weight.min)
        s.write_single(self.war_weight.max)


class StateLink(GraphLink):
    classname = "TStateLink"

    def __init__(self, script, begin=None, end=None, ord_num=0,
                 has_arrow=True):
        GraphLink.__init__(self, script, begin, end, ord_num, has_arrow)
        self.expression = ""
        self.priority = 0

    def save(self, s):
        GraphLink.save(self, s)
        s.write_widestr(self.expression)
        s.write_int(self.priority)
