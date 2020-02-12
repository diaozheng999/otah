#!/usr/bin/env python

import sys
import os
import subprocess
import argparse

DEV_FLAGS = "-Og"
PROD_FLAGS = "-O"

def compile(bundle_path, bundle_name, bundle_extension, flags, production):

    platform_bin = "linux64-bin"

    if sys.platform == "darwin":
        platform_bin = "osx-bin"
    elif sys.platform == "win32":
        platform_bin = "win64-bin"
        bundle_path = bundle_path.replace("/", "\\")

    flags = flags + " -emit-binary"

    if production:
        flags += " " + PROD_FLAGS
    else:
        flags += " " + DEV_FLAGS

    flags = flags.strip()

    filename = os.path.join(bundle_path, "%s%s"%(
        bundle_name,
        bundle_extension
    ))

    command = "./node_modules/hermes-engine/%s/hermes %s -out %s.hbc %s"%(
        platform_bin,
        flags,
        filename,
        filename
    )

    print("Executing command: %s"%command)
    subprocess.call(command, shell=True)

def get_parser(parent=None):

    description = "Hermes compiler that compiles react native bundles into hermes binary."

    if parent:
        parser = parent.add_parser("hermes", description=description)
    else:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'bundle_path', 
        metavar='BUNDLE_PATH',
        help='Path to bundle used for compilation'
    )
    parser.add_argument(
        '--production', 
        help='Executes Hermes compiler in Production mode which uses Expensive optimizations', 
        action='store_true'
    )
    parser.add_argument(
        '--bundle-name',
        help='Defaults to \'main\'',
        default='main'
    )
    parser.add_argument(
        '--bundle-extension',
        help='Defaults to \'.jsbundle\'',
        default='.jsbundle'
    )
    parser.add_argument(
        '--flags',
        help='Additional flags/options to be passed to hermes',
        default=''
    )
    parser.set_defaults(command="hermes")
    return parser

def cli(args):
    print(args)

    compile(
        args.bundle_path,
        args.bundle_name,
        args.bundle_extension,
        args.flags,
        args.production
    )

if __name__ == "__main__":
    parser = get_parser()
    cli(parser.parse_args())
