#!/usr/bin/env python3

import argparse
import os.path
import os

from rscript.file.scr import CompiledScript


def main():
    parser = argparse.ArgumentParser(
        description="Make dump of given script"
    )
    parser.add_argument(metavar="FILE", dest="infile",
                        help="Path to compiled script")
    parser.add_argument("-o", "--output", default="", dest="outfile",
                        help="Path to output file", nargs="?")
    args = parser.parse_args()

    basepath = ''
    filename = os.path.split(args.infile)[1]
    scriptname = os.path.splitext(filename)[0]
    outfile = scriptname + "_d.txt"

    if args.outfile != '':
        basepath, filename = os.path.split(args.outfile)
        outfile = args.outfile

    script = CompiledScript()
    script.basepath = basepath
    with open(args.infile, 'rb') as f:
        script.load(f)

    if basepath != '' and not os.path.exists(basepath):
        os.mkdir(basepath)
    if script.basepath != '' and not os.path.exists(script.basepath):
        os.mkdir(script.basepath)

    with open(outfile, 'wt', encoding='cp1251',  newline='') as f:
        script.dump(f)


if __name__ == '__main__':
    main()
