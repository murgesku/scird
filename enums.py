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


# Race bitwise
class r_(IntFlag):
    USE = 1

    MALOC = 2
    PELENG = 4
    PEOPLE = 8
    FEI = 16
    GAAL = 32


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


# Economy bitwise
class e_(IntFlag):
    USE = 1

    AGRICULTURAL = 2
    INDUSTRIAL = 4
    MIXED = 8


# Government bitwise
class g_(IntFlag):
    USE = 1

    ANARCHY = 2
    DICTATORSHIP = 4
    MONARCHY = 8
    REPUBLIC = 16
    DEMOCRACY = 32


# Weapon
class w_(IntEnum):
    UNDEF = 0
    YES = 1
    NO = 2


# Friendship
class f_(IntEnum):
    FREE = 0
    HELP = 1


# Place type
class pt_(IntEnum):
    FREE = 0
    NEAR_PLANET = 1
    IN_PLANET = 2
    TO_STAR = 3
    NEAR_ITEM = 4
    FROM_SHIP = 5


# Move type
class mt_(IntEnum):
    NONE = 0
    MOVE = 1
    FOLLOW = 2
    JUMP = 3
    LANDING = 4
    FREE = 5


# Operation type
class op_(IntEnum):
    NORMAL = 0
    INIT = 1
    GLOBAL = 2
    DIALOGBEGIN = 3


# Variable type
class var_(IntEnum):
    UNKNOWN = 0
    INTEGER = 1
    DWORD = 2
    FLOAT = 3
    STRING = 4


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


# Item class
class ic_(IntEnum):
    EQUIPMENT = 0
    WEAPON = 1
    GOODS = 2
    ARTEFACT = 3
    USELESS = 4
    UNKNOWN = 5


# Item Equipment type
class Equipment(IntEnum):
    FUELTANK = 0
    ENGINE = 1
    RADAR = 2
    SCANNER = 3
    REPAIRROBOT = 4
    CARGOHOOK = 5
    DEFGENERATOR = 6


class Weapon(IntEnum):
    pass  # 0..17


class Goods(IntEnum):
    pass  # 0..9


class Artefact(IntEnum):
    pass  # 0..30
