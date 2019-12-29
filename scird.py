#!/usr/bin/env python3

import argparse
import os.path

from scr import CompiledScript
from svr import *
from lexer import Lexer
from analyzer import Analyzer
from linker import Linker
from enums import *
from utils import *

__version__ = "0.9.0"


def decompile(script, lang=None):
    """
    @type script: CompiledScript
    @type lang: BlockPar
    """
    # vars_zone = Rect(0, 1000, 400, 300)
    # code_zone = Rect(300, 1000, 200, 200)
    # main_zone = Rect(0, 0, 600, 1000)
    # star_zone = Rect(0, 600, 400, 1000)

    source = SourceScript()
    Linker.init(source, lang)

    localvars = {var.name: var for var in script.localvars}

    dialog_answers = []
    for c in script.dialog_answers:
        e = source.add(DialogAnswer)
        e.text = c.command
        e.msg = c.answer
        dialog_answers.append(e)

    dialog_msgs = []
    for c in script.dialog_msgs:
        e = source.add(DialogMsg)
        e.text = c.command
        dialog_msgs.append(e)

    for c in script.dialogs:
        e = source.add(Dialog)
        e.text = c.name
        tokens = Analyzer(Lexer(c.code).tokenize()).analyze()
        Linker(tokens, e, dialog_msgs).build()
        del localvars[c.name]

    for da, e in zip(script.dialog_answers, dialog_answers):
        code = da.answer + da.code
        tokens = Analyzer(Lexer(code).tokenize()).analyze()
        Linker(tokens, e, dialog_msgs).build()

    for dm, e in zip(script.dialog_msgs, dialog_msgs):
        tokens = Analyzer(Lexer(dm.code).tokenize()).analyze()
        Linker(tokens, e, dialog_answers).build()

    stars = []
    planets = {}
    for i, c in enumerate(script.stars):
        e = source.add(Star)
        e.text = c.name
        e.constellation = c.constellation + 1
        e.priority = i
        e.is_subspace = c.is_subspace
        e.no_kling = c.no_kling
        e.no_come_kling = c.no_come_kling
        del localvars[c.name]
        stars.append(e)

    for star, s in zip(script.stars, stars):
        for c in star.starlinks:
            d = stars[c.end_star]
            e = source.link(s, d)  # start - destination
            e.dist = c.distance
            e.relation = c.relation
            e.deviation = c.deviation
            e.is_hole = c.is_hole

        for c in star.planets:
            e = source.add(Planet)
            e.text = c.name
            e.race = c.race
            e.owner = c.owner
            e.economy = c.economy
            e.government = c.government
            e.range = c.range
            e.dialog = c.dialog
            source.link(e, s)
            planets[c.name] = e
            del localvars[c.name]

        for c in star.ships:
            e = source.add(Ship)
            e.count = c.count
            e.owner = c.owner
            e.type = c.type
            e.is_player = c.is_player
            e.speed = c.speed
            e.weapon = c.weapon
            e.cargohook = c.cargohook
            e.emptyspace = c.emptyspace
            e.rating = c.rating
            e.status = c.status
            e.score = c.score
            e.strength = c.strength
            e.ruins = c.ruins
            source.link(e, s)

    starnames = {star.text: star for star in stars}
    places = {}
    for c in script.places:
        e = source.add(Place)
        e.text = c.name
        e.type = c.type
        if c.type is not pt_.FREE:
            e.obj = c.object
        if c.type in (pt_.FREE, pt_.TO_STAR, pt_.FROM_SHIP):
            e.angle = c.angle
            e.dist = c.distance
        if c.type is not pt_.IN_PLANET:
            e.radius = c.radius
        source.link(e, starnames[c.star])
        places[c.name] = e
        del localvars[c.name]

    states = []
    for c in script.states:
        e = source.add(State)
        e.text = c.name
        e.type = c.type
        if c.type not in (mt_.NONE, mt_.FREE):
            e.obj = c.object
        for a in c.attack:
            e.attack_groups.append(a)
        e.item = c.take_item
        e.take_all = c.take_all
        e.out_msg = c.out_msg
        e.in_msg = c.in_msg
        states.append(e)

    # for state, s in zip(script.states, states):
    #     if state.code:
    #         Linker(state.code, s, states).build()

    groups = []
    for c in script.groups:
        e = source.add(Group)
        e.text = c.name
        e.owner = c.owner
        e.type = c.type
        e.count = c.count
        e.speed = c.speed
        e.weapon = c.weapon
        e.cargohook = c.cargohook
        e.emptyspace = c.emptyspace
        e.friendship = c.friendship
        e.add_player = c.add_player
        e.rating = c.rating
        e.score = c.score
        e.status = c.status
        e.search_dist = c.search_distance
        e.dialog = c.dialog
        e.strength = c.strength
        e.ruins = c.ruins
        planet = planets[c.planet]
        source.link(e, planet)
        state = states[c.state]
        source.link(e, state)
        groups.append(e)
        del localvars[c.name]

    for c in script.grouplinks:
        begin = groups[c.begin]
        end = groups[c.end]
        e = source.link(begin, end)
        e.relations = c.relations
        e.war_weight = c.war_weight

    groupnames = {group.text: group for group in groups}
    for c in script.items:
        e = source.add(Item)
        e.text = c.name
        e.kind = c.kind
        e.type = c.type
        e.size = c.size
        e.level = c.level
        e.radius = c.radius
        e.owner = c.owner
        e.useless = c.useless
        if c.place:
            obj = None
            if c.place in places:
                obj = places[c.place]
            elif c.place in planets:
                obj = planets[c.place]
            elif c.place in groups:
                obj = groupnames[c.place]
            if obj is not None:
                source.link(e, obj)
        del localvars[c.name]

    for c in script.globalvars:
        e = source.add(ExprVar)
        e.text = c.name
        e.type = svar_[c.type.name]
        if c.type is not var_.UNKNOWN:
            e.init_value = str(c.value)
        e.is_global = True

    for c in localvars.values():
        e = source.add(ExprVar)
        e.text = c.name
        e.type = svar_[c.type.name]
        if c.type is not var_.UNKNOWN:
            e.init_value = str(c.value)
        e.is_global = False

    # Linker(script.globalcode, None, None, type=op_.GLOBAL).build()
    # Linker(script.globalcode, None, None, type=op_.INIT).build()
    # Linker(script.globalcode, None, None, type=op_.NORMAL).build()
    # Linker(script.globalcode, None, None, type=op_.DIALOGBEGIN).build()

    return source


def main():
    parser = argparse.ArgumentParser(
        description="Scird - SRHD Script (v6) Decompiler."
    )
    parser.add_argument("-o", "--output", nargs="?", default=None,
                        help="Path to output file")
    parser.add_argument("-t", "--dump", action="store_true",
                        help="Make dump of given script")
    parser.add_argument("-l", "--lang", nargs="?", default=None,
                        help="Path to specified Lang file (txt or dat)")
    parser.add_argument("--not-substitute", action="store_true",
                        help="Disable text substitution, Lang is ignored")
    parser.add_argument("filename", metavar="FILE",
                        help="Path to script file")
    args = parser.parse_args(['Mod_EvoTrank.scr'])

    filename = os.path.split(args.filename)[1]
    scriptname = os.path.splitext(filename)[0]

    script = CompiledScript()
    with open(args.filename, 'rb') as f:
        script.load(f)

    if args.dump:
        print("Writing dump...")
        if args.output:
            with open(args.output, 'wt') as f:
                script.dump(f)
            print(args.output + " was created.")
        else:
            with open(scriptname + "_d.txt", 'wt') as f:
                script.dump(f)
            print(scriptname + "_d.txt was created.")
        return

    source = decompile(script, args.lang)
    print("Writing svr...")
    if args.output:
        with open(args.output, 'wb') as f:
            source.save(f)
        print(args.output + " was created.")
    else:
        with open(scriptname + "_d.svr", 'wb') as f:
            source.save(f)
        print(scriptname + "_d.svr was created.")
    return


if __name__ == "__main__":
    main()
