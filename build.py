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
                        help="Path to dump file")
    parser.add_argument("-o", "--output", default="", dest="outfile",
                        help="Path to output file", nargs="?")
    args = parser.parse_args()

    basepath, filename = os.path.split(args.infile)
    dumpname = os.path.splitext(filename)[0]
    outfile = dumpname + ".scr"

    if args.outfile != '':
        outfile = args.outfile

    script = CompiledScript()
    script.basepath = basepath
    with open(args.infile, 'rt', encoding='cp1251', newline='') as f:
        script.restore(f)

    with open(outfile, 'wb') as f:
        script.save(f)


if __name__ == '__main__':
    main()
