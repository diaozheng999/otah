#!/usr/bin/env python

"""
    clean.py
    - author: Diao Zheng

    Cleans the existing build directory.
"""

import shutil
import os
import argparse
from barrel import clean, SOURCE_ROOT

def get_parser(parent=None):
    """ Returns an argparse parser or attaches a subparser to parent. """

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
    """ The script that actually runs """

    if os.path.exists(args.dir):
        print("Removing %s..."%args.dir)
        shutil.rmtree(args.dir)
    else:
        print("%s does not exist."%args.dir)
    if not args.no_barrel:
        clean(args.barrel)
    else:
        print("Not cleaning barrelled files.")

def cli_root():
    """ The default CLI interface if this script is invoked by itself """

    parser = get_parser()
    args = parser.parse_args()
    cli(args)

if __name__ == "__main__":
    cli_root()
