__all__ = [
    "SourceScript",
    "Star", "StarLink", "Planet", "Ship",
    "Item", "Place", "Group", "GroupLink",
    "State", "StateLink", "Ether",
    "ExprIf", "ExprOp", "ExprVar", "ExprWhile",
    "Dialog", "DialogMsg", "DialogAnswer",
]

from rangers.io import Stream
from rangers.blockpar import BlockPar
from rscript.file.enums import *
from rscript.file.utils import *

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

    def add(self, clsname, pos=None):
        if not pos:
            pos = random_point()
        gp = classnames[clsname](self, pos)
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

    def find_link_begin(self, gp, clsname):
        cls = classnames[clsname]
        for gl in self.graphlinks:
            # noinspection PyTypeHints
            if (gl.begin is gp) and isinstance(gl.end, cls):
                return gl

    def save(self, f):
        s = Stream.from_io(f)

        s.add(b'\x55\x44\x33\x22')
        s.add_uint(self.version)
        s.add_int(self.viewpos.x)
        s.add_int(self.viewpos.y)
        s.add_widestr(self.name)
        s.add_widestr(self.filename)
        self.textfilenames.save(s)
        self.translations.save(s)
        self.translations_id.save(s)
        s.add_uint(len(self.graphpoints))
        for gp in self.graphpoints:
            gp.save(s)
        s.add_uint(len(self.graphlinks))
        for gl in self.graphlinks:
            gl.save(s)
        s.add_uint(len(self.graphrects))
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
        s.add_widestr(self.classname)
        s.add_int(self.pos.x)
        s.add_int(self.pos.y)
        s.add_widestr(self.text)
        s.add_int(-1)


class GraphLink(object):
    classname = "TGraphLink"

    def __init__(self, script, begin=None, end=None, ord_num=0, has_arrow=True):
        self._script = script
        self.begin = begin  # graphpoint
        self.end = end  # graphpoint
        self.ord_num = ord_num
        self.has_arrow = has_arrow

    def save(self, s):
        s.add_widestr(self.classname)
        s.add_int(self._script.index(self.begin))
        s.add_int(self._script.index(self.end))
        s.add_uint(self.ord_num)
        s.add_bool(self.has_arrow)


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
        s.add_widestr(self.classname)
        s.add_int(self.rect.top)
        s.add_int(self.rect.left)
        s.add_int(self.rect.right)
        s.add_int(self.rect.bottom)
        s.add_byte(self.fill_style)
        s.add_uint(self.fill_color)
        s.add_byte(self.border_style)
        s.add_uint(self.border_color)
        s.add_uint(self.border_size)
        s.add_single(self.border_coef)
        s.add_uint(self.text_align_x)
        s.add_uint(self.text_align_y)
        s.add_bool(self.text_align_rect)
        s.add_widestr(self.text)
        s.add_uint(self.text_color)
        s.add_widestr(self.font)
        s.add_uint(self.font_size)
        s.add_bool(self.is_bold)
        s.add_bool(self.is_italic)
        s.add_bool(self.is_underline)


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
        s.add_uint(self.constellation)
        s.add_uint(self.priority)
        s.add_bool(self.is_subspace)
        s.add_bool(self.no_kling)
        s.add_bool(self.no_come_kling)


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
        s.add_uint(int(self.race))
        s.add_uint(int(self.owner))
        s.add_uint(int(self.economy))
        s.add_uint(int(self.government))
        s.add_int(self.range.min)
        s.add_int(self.range.max)
        s.add_int(self._script.index(self.dialog))


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
        s.add_int(self.count)
        s.add_uint(int(self.owner))
        s.add_uint(int(self.type))
        s.add_bool(self.is_player)
        s.add_int(self.speed.min)
        s.add_int(self.speed.max)
        s.add_uint(self.weapon)
        s.add_uint(self.cargohook)
        s.add_int(self.emptyspace)
        s.add_int(self.rating.min)
        s.add_int(self.rating.max)
        s.add_int(self.status.trader.min)
        s.add_int(self.status.trader.max)
        s.add_int(self.status.warrior.min)
        s.add_int(self.status.warrior.max)
        s.add_int(self.status.pirate.min)
        s.add_int(self.status.pirate.max)
        s.add_int(self.score.min)
        s.add_int(self.score.max)
        s.add_single(self.strength.min)
        s.add_single(self.strength.max)
        s.add_widestr(self.ruins)


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
        s.add_uint(self.kind)
        s.add_uint(self.type)
        s.add_int(self.size)
        s.add_uint(self.level)
        s.add_int(self.radius)
        s.add_uint(int(self.owner))
        s.add_widestr(self.useless)


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
        s.add_uint(self.type)
        s.add_single(self.angle)
        s.add_single(self.dist)
        s.add_int(self.radius)
        s.add_int(self._script.index(self.obj))


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
        s.add_uint(int(self.owner))
        s.add_uint(int(self.type))
        s.add_int(self.count.min)
        s.add_int(self.count.max)
        s.add_int(self.speed.min)
        s.add_int(self.speed.max)
        s.add_uint(int(self.weapon))
        s.add_uint(self.cargohook)
        s.add_int(self.emptyspace)
        s.add_uint(int(self.friendship))
        s.add_bool(self.add_player)
        s.add_int(self.rating.min)
        s.add_int(self.rating.max)
        s.add_int(self.status.trader.min)
        s.add_int(self.status.trader.max)
        s.add_int(self.status.warrior.min)
        s.add_int(self.status.warrior.max)
        s.add_int(self.status.pirate.min)
        s.add_int(self.status.pirate.max)
        s.add_int(self.score.min)
        s.add_int(self.score.max)
        s.add_int(self.search_dist)
        s.add_int(self._script.index(self.dialog))
        s.add_single(self.strength.min)
        s.add_single(self.strength.max)
        s.add_widestr(self.ruins)


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
        s.add_uint(self.type)
        s.add_int(self._script.index(self.obj))
        s.add_uint(len(self.attack_groups))
        for ag in self.attack_groups:
            s.add_int(self._script.index(ag))
        s.add_int(self._script.index(self.item))
        s.add_bool(self.take_all)
        s.add_widestr(self.out_msg)
        s.add_widestr(self.in_msg)
        s.add_uint(int(self.ether_type))
        s.add_widestr(self.ether_uid)
        s.add_widestr(self.ether_msg)


class ExprOp(GraphPoint):
    classname = "Top"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.add_widestr(self.expression)
        s.add_byte(int(self.type))


class ExprIf(GraphPoint):
    classname = "Tif"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.add_widestr(self.expression)
        s.add_byte(int(self.type))


class ExprWhile(GraphPoint):
    classname = "Twhile"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.expression = ""
        self.type = op_.NORMAL  # op

    def save(self, s):
        GraphPoint.save(self, s)
        s.add_widestr(self.expression)
        s.add_byte(int(self.type))


class ExprVar(GraphPoint):
    classname = "TVar"

    def __init__(self, script, pos=Point(0, 0), text="VarNew", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.type = svar_.UNKNOWN  # svar
        self.init_value = ""
        self.is_global = False

    def save(self, s):
        GraphPoint.save(self, s)
        s.add_uint(int(self.type))
        s.add_widestr(self.init_value)
        s.add_bool(self.is_global)


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
        s.add_uint(int(self.type))
        s.add_widestr(self.uid)
        s.add_widestr(self.msg)
        for f in self.focus:
            s.add_widestr(f)


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
        s.add_widestr(self.msg)


class DialogAnswer(GraphPoint):
    classname = "TDialogAnswer"

    def __init__(self, script, pos=Point(0, 0), text="", parent=None):
        GraphPoint.__init__(self, script, pos, text, parent)
        self.msg = ""

    def save(self, s):
        GraphPoint.save(self, s)
        s.add_widestr(self.msg)


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
        s.add_int(self.dist.min)
        s.add_int(self.dist.max)
        s.add_int(self.deviation)
        s.add_int(self.relation.min)
        s.add_int(self.relation.max)
        s.add_bool(self.is_hole)


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
            s.add_uint(int(r))
        s.add_single(self.war_weight.min)
        s.add_single(self.war_weight.max)


class StateLink(GraphLink):
    classname = "TStateLink"

    def __init__(self, script, begin=None, end=None, ord_num=0,
                 has_arrow=True):
        GraphLink.__init__(self, script, begin, end, ord_num, has_arrow)
        self.expression = ""
        self.priority = 0

    def save(self, s):
        GraphLink.save(self, s)
        s.add_widestr(self.expression)
        s.add_int(self.priority)


classnames = {v.classname: v for v in (
    Star, Planet, Ship, Item, Place, Group, State, ExprOp, ExprIf, ExprWhile,
    ExprVar, Ether, Dialog, DialogMsg, DialogAnswer
)}
