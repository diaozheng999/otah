#!/usr/bin/env python
import barrel
import clean
import hermes
import argparse
import react_native

parser = argparse.ArgumentParser(
    description="More command-line tools for React Native projects.")

subparsers = parser.add_subparsers()

hermes.get_parser(subparsers)
clean.get_parser(subparsers)
barrel.get_parser(subparsers)
react_native.get_parser(subparsers)

args = parser.parse_args()

if args.command == "barrel":
    barrel.cli(args)
elif args.command == "bundle":
    react_native.cli(args)
elif args.command == "clean":
    clean.cli(args)
elif args.command == "hermes":
    hermes.cli(args)
else:
    exit("Unknown command")
