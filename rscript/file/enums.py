__all__ = [
    "Race", "Equipment", "r_", "o_", "e_", "g_", "t_", "w_", "f_",
    "pt_", "mt_", "ic_", "op_", "et_", "rel_", "var_",  "svar_",
]

from enum import IntFlag, IntEnum


class Race(IntEnum):
    MALOC = 0
    PELENG = 1
    PEOPLE = 2
    FEI = 3
    GAAL = 4
    KLING = 5
    NONE = 6
    PIRATECLAN = 7

_map_race = {Race.MALOC: "Maloc", Race.PELENG: "Peleng", Race.PEOPLE: "People",
             Race.FEI: "Fei", Race.GAAL: "Gaal", Race.KLING: "Kling",
             Race.NONE: "None", Race.PIRATECLAN: "PirateClan"}
_rmap_race = {v: k for k, v in _map_race.items()}

def _race_str(self):
    return _map_race[self]

def _race_from_str(s):
    return _rmap_race[s]

setattr(Race, "__str__", _race_str)
setattr(Race, "from_str", staticmethod(_race_from_str))


# Race bitwise
class r_(IntFlag):
    USE = 1

    MALOC = 2
    PELENG = 4
    PEOPLE = 8
    FEI = 16
    GAAL = 32

_map_r = {r_.USE: "Use", r_.MALOC: "Maloc", r_.PELENG: "Peleng",
          r_.PEOPLE: "People", r_.FEI: "Fei", r_.GAAL: "Gaal"}
_rmap_r = {v: k for k, v in _map_r.items()}

def _r_str(self):
    flags = [_map_r[f] for f in self.__class__ if f in self]
    return ','.join(flags)

def _r_from_str(cls, s):
    flags = s.strip().split(',')
    result = cls(0)
    for l, f in _rmap_r.items():
        if l in flags:
            result |= f
    return result

setattr(r_, "__str__", _r_str)
setattr(r_, "from_str", classmethod(_r_from_str))


# Owner bitwise
class o_(IntFlag):
    USE = 1

    MALOC = 2
    PELENG = 4
    PEOPLE = 8
    FEI = 16
    GAAL = 32

    KLING = 64
    NONE = 128
    PIRATECLAN = 256

    AS_PLAYER = 512


_map_o = {o_.USE: "Use", o_.MALOC: "Maloc", o_.PELENG: "Peleng",
          o_.PEOPLE: "People", o_.FEI: "Fei", o_.GAAL: "Gaal",
          o_.KLING: "Kling", o_.NONE: "None", o_.PIRATECLAN: "PirateClan",
          o_.AS_PLAYER: "AsPlayer"}
_rmap_o = {v: k for k, v in _map_o.items()}

def _o_str(self):
    flags = [_map_o[f] for f in self.__class__ if f in self]
    return ','.join(flags)

def _o_from_str(cls, s):
    flags = s.strip().split(',')
    result = cls(0)
    for l, f in _rmap_o.items():
        if l in flags:
            result |= f
    return result

setattr(o_, "__str__", _o_str)
setattr(o_, "from_str", classmethod(_o_from_str))


# Type bitwise
class t_(IntFlag):
    USE = 1

    RANGER = 1 << 1
    WARRIOR = 1 << 2
    PIRATE = 1 << 3
    TRANSPORT = 1 << 4
    LINER = 1 << 5
    DIPLOMAT = 1 << 6

    BLAZER_K0 = 1 << 7
    BLAZER_K1 = 1 << 8
    BLAZER_K2 = 1 << 9
    BLAZER_K3 = 1 << 10
    BLAZER_K4 = 1 << 11
    BLAZER_K5 = 1 << 12
    BLAZER_K6 = 1 << 26
    BLAZER_K7 = 1 << 27

    KELLER_K0 = 1 << 13
    KELLER_K1 = 1 << 14
    KELLER_K2 = 1 << 15
    KELLER_K3 = 1 << 16
    KELLER_K4 = 1 << 17
    KELLER_K5 = 1 << 18
    KELLER_K6 = 1 << 28
    KELLER_K7 = 1 << 29

    TERRON_K0 = 1 << 19
    TERRON_K1 = 1 << 20
    TERRON_K2 = 1 << 21
    TERRON_K3 = 1 << 22
    TERRON_K4 = 1 << 23
    TERRON_K5 = 1 << 24
    TERRON_K6 = 1 << 30
    TERRON_K7 = 1 << 31

    TRANCLUCATOR = 1 << 25

_map_t = {t_.USE: "Use", t_.RANGER: "Ranger", t_.WARRIOR: "Warrior",
          t_.PIRATE: "Pirate", t_.TRANSPORT: "Transport", t_.LINER: "Liner",
          t_.DIPLOMAT: "Diplomat", t_.BLAZER_K0: "BlazerK0", t_.BLAZER_K1: "BlazerK1",
          t_.BLAZER_K2: "BlazerK2", t_.BLAZER_K3: "BlazerK3", t_.BLAZER_K4: "BlazerK4",
          t_.BLAZER_K5: "BlazerK5", t_.BLAZER_K6: "BlazerK6", t_.BLAZER_K7: "BlazerK7",
          t_.KELLER_K0: "KellerK0", t_.KELLER_K1: "KellerK1", t_.KELLER_K2: "KellerK2",
          t_.KELLER_K3: "KellerK3", t_.KELLER_K4: "KellerK4", t_.KELLER_K5: "KellerK5",
          t_.KELLER_K6: "KellerK6", t_.KELLER_K7: "KellerK7", t_.TERRON_K0: "TerronK0",
          t_.TERRON_K1: "TerronK1", t_.TERRON_K2: "TerronK2", t_.TERRON_K3: "TerronK3",
          t_.TERRON_K4: "TerronK4", t_.TERRON_K5: "TerronK5", t_.TERRON_K6: "TerronK6",
          t_.TERRON_K7: "TerronK7", t_.TRANCLUCATOR: "Tranclucator"}
_rmap_t = {v: k for k, v in _map_t.items()}

def _t_str(self):
    flags = [_map_t[f] for f in self.__class__ if f in self]
    return ','.join(flags)

def _t_from_str(cls, s):
    flags = s.strip().split(',')
    result = cls(0)
    for l, f in _rmap_t.items():
        if l in flags:
            result |= f
    return result

setattr(t_, "__str__", _t_str)
setattr(t_, "from_str", classmethod(_t_from_str))


# Economy bitwise
class e_(IntFlag):
    USE = 1

    AGRICULTURE = 2
    INDUSTRIAL = 4
    MIXED = 8

_map_e = {e_.USE: "Use", e_.AGRICULTURE: "Agriculture",
          e_.INDUSTRIAL: "Industrial", e_.MIXED: "Mixed"}
_rmap_e = {v: k for k, v in _map_e.items()}

def _e_str(self):
    flags = [_map_e[f] for f in self.__class__ if f in self]
    return ','.join(flags)

def _e_from_str(cls, s):
    flags = s.strip().split(',')
    result = cls(0)
    for l, f in _rmap_e.items():
        if l in flags:
            result |= f
    return result

setattr(e_, "__str__", _e_str)
setattr(e_, "from_str", classmethod(_e_from_str))


# Government bitwise
class g_(IntFlag):
    USE = 1

    ANARCHY = 2
    DICTATORSHIP = 4
    MONARCHY = 8
    REPUBLIC = 16
    DEMOCRACY = 32

_map_g = {g_.USE: "Use", g_.ANARCHY: "Anarchy",
          g_.DICTATORSHIP: "Dictatorship", g_.MONARCHY: "Monarchy",
          g_.REPUBLIC: "Republic", g_.DEMOCRACY: "Democracy"}
_rmap_g = {v: k for k, v in _map_g.items()}

def _g_str(self):
    flags = [_map_g[f] for f in self.__class__ if f in self]
    return ','.join(flags)

def _g_from_str(cls, s):
    flags = s.strip().split(',')
    result = cls(0)
    for l, f in _rmap_g.items():
        if l in flags:
            result |= f
    return result

setattr(g_, "__str__", _g_str)
setattr(g_, "from_str", classmethod(_g_from_str))


# Weapon
class w_(IntEnum):
    UNDEF = 0
    YES = 1
    NO = 2

_map_w = {w_.UNDEF: "NoMatter", w_.YES: "HasWeapon", w_.NO: "NoWeapon"}
_rmap_w = {v: k for k, v in _map_w.items()}

def _w_str(self):
    return _map_w[self]

def _w_from_str(s):
    return _rmap_w[s]

setattr(w_, "__str__", _w_str)
setattr(w_, "from_str", staticmethod(_w_from_str))


# Friendship
class f_(IntEnum):
    FREE = 0
    HELP = 1

_map_f = {f_.FREE: "Free", f_.HELP: "Help"}
_rmap_f = {v: k for k, v in _map_f.items()}

def _f_str(self):
    return _map_f[self]

def _f_from_str(s):
    return _rmap_f[s]

setattr(f_, "__str__", _f_str)
setattr(f_, "from_str", staticmethod(_f_from_str))


# Place type
class pt_(IntEnum):
    FREE = 0
    NEAR_PLANET = 1
    IN_PLANET = 2
    TO_STAR = 3
    NEAR_ITEM = 4
    FROM_SHIP = 5

_map_pt = {pt_.FREE: "Free", pt_.NEAR_PLANET: "NearPlanet",
           pt_.IN_PLANET: "InPlanet", pt_.TO_STAR: "ToStar",
           pt_.NEAR_ITEM: "NearItem", pt_.FROM_SHIP: "FromShip"}
_rmap_pt = {v: k for k, v in _map_pt.items()}

def _pt_str(self):
    return _map_pt[self]

def _pt_from_str(s):
    return _rmap_pt[s]

setattr(pt_, "__str__", _pt_str)
setattr(pt_, "from_str", staticmethod(_pt_from_str))


# Move type
class mt_(IntEnum):
    NONE = 0
    MOVE = 1
    FOLLOW = 2
    JUMP = 3
    LANDING = 4
    FREE = 5

_map_mt = {mt_.NONE: "None", mt_.MOVE: "Move", mt_.FOLLOW: "Follow",
           mt_.JUMP: "Jump", mt_.LANDING: "Landing", mt_.FREE: "Free"}
_rmap_mt = {v: k for k, v in _map_mt.items()}

def _mt_str(self):
    return _map_mt[self]

def _mt_from_str(s):
    return _rmap_mt[s]

setattr(mt_, "__str__", _mt_str)
setattr(mt_, "from_str", staticmethod(_mt_from_str))


# Operation type
class op_(IntEnum):
    NORMAL = 0
    INIT = 1
    GLOBAL = 2
    DIALOGBEGIN = 3


# Variable type
class var_(IntEnum):
    UNKNOWN = 0  #, "Unknown"
    INTEGER = 1  #, "Integer"
    DWORD = 2  #, "Dword"
    FLOAT = 3  #, "Float"
    STRING = 4  #, "String"

_map_var = {var_.UNKNOWN: "Unknown", var_.INTEGER: "Integer",
            var_.DWORD: "Dword", var_.FLOAT: "Float", var_.STRING: "String"}
_rmap_var = {v: k for k, v in _map_var.items()}

def _var_str(self):
    return _map_var[self]

def _var_from_str(s):
    return _rmap_var[s]

setattr(var_, "__str__", _var_str)
setattr(var_, "from_str", staticmethod(_var_from_str))


# Variable type in source
class svar_(IntEnum):
    UNKNOWN = 0
    INTEGER = 1
    DWORD = 2
    STRING = 3
    FLOAT = 4


# Ether type
class et_(IntEnum):
    GALAXY = 0
    ETHER = 1
    SHIP = 2
    QUEST = 3
    QUEST0K = 4
    QUESTCANCEL = 5


# Relation
class rel_(IntEnum):
    WAR = 0
    BAD = 1
    NORMAL = 2
    GOOD = 3
    BEST = 4
    NOCHANGE = 5

_map_rel = {rel_.WAR: "War", rel_.BAD: "Bad", rel_.NORMAL: "Normal",
            rel_.GOOD: "Good", rel_.BEST: "Best", rel_.NOCHANGE: "NoChange"}
_rmap_rel = {v: k for k, v in _map_rel.items()}

def _rel_str(self):
    return _map_rel[self]

def _rel_from_str(s):
    return _rmap_rel[s]

setattr(rel_, "__str__", _rel_str)
setattr(rel_, "from_str", staticmethod(_rel_from_str))


# Item class
class ic_(IntEnum):
    EQUIPMENT = 0  #, "Equipment"
    WEAPON = 1  #, "Weapon"
    GOODS = 2  #, "Goods"
    ARTIFACT = 3  #, "Artifact"
    USELESS = 4  #, "Useless"
    UNKNOWN = 5  #, "Unknown"

_map_ic = {ic_.EQUIPMENT: "Equipment", ic_.WEAPON: "Weapon", ic_.GOODS: "Goods",
           ic_.ARTIFACT: "Artifact", ic_.USELESS: "Useless", ic_.UNKNOWN: "Unknown"}
_rmap_ic = {v: k for k, v in _map_ic.items()}

def _ic_str(self):
    return _map_ic[self]

def _ic_from_str(s):
    return _rmap_ic[s]

setattr(ic_, "__str__", _ic_str)
setattr(ic_, "from_str", staticmethod(_ic_from_str))


# Item Equipment type
class Equipment(IntEnum):
    FUELTANK = 0  #, "FuelTank"
    ENGINE = 1  #, "Engine"
    RADAR = 2  #, "Radar"
    SCANNER = 3  #, "Scaner"
    REPAIRROBOT = 4  #, "RepairRobot"
    CARGOHOOK = 5  #, "CargoHook"
    DEFGENERATOR = 6  #, "DefGenerator"

_map_equip = {Equipment.FUELTANK: "FuelTank", Equipment.ENGINE: "Engine",
              Equipment.RADAR: "Radar", Equipment.SCANNER: "Scaner",
              Equipment.REPAIRROBOT: "RepairRobot",
              Equipment.CARGOHOOK: "CargoHook",
              Equipment.DEFGENERATOR: "DefGenerator"}
_rmap_equip = {v: k for k, v in _map_equip.items()}

def _equip_str(self):
    return _map_equip[self]

def _equip_from_str(s):
    return _rmap_equip[s]

setattr(Equipment, "__str__", _equip_str)
setattr(Equipment, "from_str", staticmethod(_equip_from_str))


class Weapon(IntEnum):
    pass  # 0..17


class Goods(IntEnum):
    pass  # 0..9


class Artifact(IntEnum):
    pass  # 0..30

