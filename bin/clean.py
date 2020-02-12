#!/usr/bin/env python

import shutil
import os
import argparse
from barrel import clean, SOURCE_ROOT


def get_parser(parent=None):
    description = "Platform-independent clean script for packages."
    
    if parent:
        parser = parent.add_parser("clean", description=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-b',
        '--barrel',
        help="The directory that the barrel's remove script is called on.",
        default=SOURCE_ROOT
    )

    parser.add_argument(
        '--no-barrel',
        help="Explicitly prevents barrel's clean script from running.",
        action='store_true'
    )

    parser.add_argument(
        '-d',
        '--dir',
        help="The directory to remove.",
        default="dist"
    )

    parser.set_defaults(command="clean")
    return parser

def cli(args):
    if os.path.exists(args.dir):
        print("Removing %s..."%args.dir)
        shutil.rmtree(args.dir)
    else:
        print("%s does not exist."%args.dir)
    if not args.no_barrel:
        clean(args.barrel)
    else:
        print("Not cleaning barrelled files.")

if __name__ == "__main__":
    parser = get_parser()
    cli(parser.parse_args())
