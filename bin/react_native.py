#!/usr/bin/env python

import barrel
import os
import subprocess
import hermes
import sys
import time
import argparse

ANDROID_DISTRIBUTION_MODES = ["google", "huawei"]
IOS_DISTRIBUTION_MODES = ["apple"]

def generate_entry_file(file_name, environ, distribution_mode):
    with open(file_name, "w") as f:
        f.write(("""
        
global.__OTAH_DISTRIBUTION_MODE__ = "%s";
global.__OTAH_ENV__ = "%s";
require("./index.js");

        """%(distribution_mode.upper(), environ.upper())).strip())

def predict_platform(mode):
    if mode in IOS_DISTRIBUTION_MODES:
        return "ios"
    elif mode in ANDROID_DISTRIBUTION_MODES:
        return "android"
    else:
        exit("!! At least platform or distribution mode must be defined.")

def validate_distribution_mode(platform, mode):
    if platform == "android":
        if mode and mode not in ANDROID_DISTRIBUTION_MODES:
            exit("!! Platform `android` is not compatible with distribution mode `%s`"%(mode, ))
        return (platform, mode or "google")
    elif platform == "ios":
        if mode and mode not in IOS_DISTRIBUTION_MODES:
            exit("!! Platform `ios` is not compatible with distribution mode `%s`"%(mode, ))
        else:
            return (platform, mode or "apple")
    else:
        return (predict_platform(mode), mode)

def get_bundle_path(
    platform, distribution_mode, env,
    path, xcproj, ignore_distribution_mode
):
    if platform == "ios":
        if path:
            return "%s/%s"%(path, xcproj)
        return "ios"
    elif ignore_distribution_mode:
        return "%s/app/src/%s/assets"%(path if path else "android", env)
    else:
        return "%s/app/src/%s/%s/assets"%(
            path if path else "android",
            distribution_mode,
            env
        )

def get_assets_dest(platform, path, xcproj):
    if platform == "ios":
        if path:
            return "%s/%s"%(path, xcproj)
        return "ios"
    elif path:
        return "%s/app/src/main/res"%(path)
    return "android/app/src/main/res"

def create_dir(dirname, directory):
    if os.path.exists(directory):
        print("%s directory '%s' exists."%(dirname, directory, ))
    else:
        print("Creating %s directory: '%s'"%(dirname, directory, ))
        os.makedirs(directory)

def bundle(
    platform, distribution_mode, env, dev, bundle_path, bundle_name,
    bundle_extension, assets_dest, entry_file, do_hermes, hermes_flags,
    clean_build, do_barrel, leave_entry_file, ci_mode, package_lock_sha,
    package_lock_stored_sha, info_only
):
    bundle_output = "%s/%s%s"%(bundle_path, bundle_name, bundle_extension)

    print("===================================================================")
    print("                My M1 React Native Bundle environment")
    print("===================================================================")
    print("               Platform | %s"%platform)
    print("      Distribution Mode | %s"%distribution_mode)
    print("            Environment | %s"%env)
    print("               Dev Mode | %r"%dev)
    print("          Bundle Output | %s"%bundle_output)
    print("     Assets Destination | %s"%assets_dest)
    print("             Entry File | %s"%entry_file)
    print("         Compile Hermes | %r"%do_hermes)
    print("   Hermes Compiler Args | %r"%hermes_flags)
    print("            Clean Build | %r"%clean_build)
    print("                 Barrel | %r"%do_barrel)
    print("       Leave Entry File | %r"%leave_entry_file)
    print("                CI Mode | %r"%ci_mode)
    print(" package-lock.json Hash | %r"%package_lock_sha)
    print("            Stored Hash | %r"%package_lock_stored_sha)
    print("===================================================================")

    if info_only:
        return

    print("")
    print("Generating entry file......")
    print("")
    generate_entry_file(entry_file, env, distribution_mode)

    if do_barrel:
        print("")
        print("Barrelling......")
        print("")
        if clean_build:
            barrel.clean(barrel.SOURCE_ROOT)
        barrel.barrel(barrel.SOURCE_ROOT)

    print("")
    print("Creating output directory......")
    print("")
    create_dir("bundle output", bundle_path)
    create_dir("assets", assets_dest)

    print("")
    print("Bundle React Native......")
    print("")

    react_native_command = "npx react-native bundle"
    react_native_command += " --entry-file %s"%(entry_file,)
    react_native_command += " --bundle-output %s"%(bundle_output,)
    react_native_command += " --dev %s"%("true" if dev else "false",)
    react_native_command += " --platform %s"%(platform,)
    react_native_command += " --assets-dest %s"%(assets_dest,)

    if clean_build:
        react_native_command += " --reset-cache"

    print(react_native_command)
    r = subprocess.call(react_native_command, shell=True)
    if r:
        exit("React Native failed.")

    if do_hermes:
        print("")
        print("Compiling with Hermes......")
        print("")
        hermes.compile(
            bundle_path,
            bundle_name,
            bundle_extension,
            hermes_flags,
            not dev)

    if not leave_entry_file:
        print("")
        print("Cleanup entry files......")
        print("")
        r = subprocess.call("rm -rf __m1bundle.*", shell=True)
        if r:
            exit("Cannot cleanup entry file.")

    if ci_mode:
        print("")
        print("Writing new hash to node_modules......")
        print("")
        with open("node_modules/PACKAGE_HASH", "w") as f:
            f.write(package_lock_sha)


def get_parser(parent=None):
    description = "Nasi Lemak React Native Bundler"

    if parent:
        parser = parent.add_parser("bundle", description=description)
    else:
        parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument(
        '-p',
        '--platform',
        help="Which platform to bundle to",
        choices=("android", "ios")
    )

    parser.add_argument(
        '-m',
        '--distribution-mode',
        help="Which distribution mode (i.e. App Store) to. " +
             " 'apple' - Apple App Store (--platform ios only), " +
             " 'google' - Google Play Store (--platform android only), " +
             " 'huawei' - Huawei AppGallery (--platform android only)",
        choices=("apple", "google", "huawei")
    )

    parser.add_argument(
        '--env',
        help="Which environment to bundle to",
        default="staging"
    )


    parser.add_argument(
        '--path',
        help="Path to build to"
    )

    parser.add_argument(
        '-d',
        "--dev",
        help="Whether to enable React Native dev mode",
        action='store_true'
    )

    parser.add_argument(
        '--hermes',
        help="Compile Hermes bundle",
        action='store_true'
    )

    parser.add_argument(
        '--hermes-flags',
        help="Additional flags/options to be passed to hermes",
        default=""
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
        '--clean-build',
        help="Set this to true to re-barrel and reset React Native transform cache.",
        action='store_true'
    )

    parser.add_argument(
        '--leave-entry-file',
        help="Set this to not clean up the last used entry file(s).",
        action='store_true'
    )

    parser.add_argument(
        '--barrel',
        '-b',
        help="Performs barrel action before continuing",
        action='store_true'
    )

    parser.add_argument(
        '--display-info-only',
        help="Only displays build information, but doesn't build.",
        action='store_true'
    )

    parser.add_argument(
        '--xcproj',
        help="Name of the project folder in Xcode to build to.",
        default="mym1usagetracker"
    )

    parser.add_argument(
        '--ignore-distribution-mode-flavor',
        help="Do not create a flavor folder for distribution mode on Android.",
        action="store_true"
    )

    parser.add_argument(
        '--rn-only',
        help="Overrides default values to default CRNA project.",
        action="store_true"
    )

    parser.set_defaults(command="bundle")
    return parser

def cli(args):
    (platform, distribution_mode) = validate_distribution_mode(
        args.platform,
        args.distribution_mode
    )

    if (args.rn_only and platform == 'android'):
        args.ignore_distribution_mode_flavor = True
        args.bundle_name = "index.android"
        args.bundle_extension = ".bundle"

    bundle_path = get_bundle_path(
        platform, distribution_mode, args.env, args.path,
        args.xcproj, args.ignore_distribution_mode_flavor)

    assets_dest = get_assets_dest(platform, args.path, args.xcproj)

    entry_file = "__m1bundle.%d.js"%(time.time())

    in_ci = True if "GITLAB_CI" in os.environ else False

    if in_ci:
        in_ci = True if os.environ["GITLAB_CI"] else False

    clean_build = args.clean_build
    package_hash = None
    package_lock_stored_sha = None

    if in_ci:
        import hashlib

        hasher = hashlib.sha256()

        with open("package-lock.json", "r") as f:
            for line in f:
                hasher.update(line)

        package_hash = hasher.hexdigest()

        if os.path.exists("node_modules/PACKAGE_HASH"):
            with open("node_modules/PACKAGE_HASH", "r") as f:
                package_lock_stored_sha = f.read()
        
        if package_lock_stored_sha != package_hash:
            clean_build = True

    bundle(
        platform, distribution_mode, args.env, args.dev, bundle_path, 
        args.bundle_name, args.bundle_extension, assets_dest, entry_file,
        args.hermes,
        args.hermes_flags, clean_build, args.barrel,
        args.leave_entry_file,
        True if "GITLAB_CI" in os.environ else False,
        package_hash,
        package_lock_stored_sha,
        args.display_info_only
    )

if __name__ == "__main__":
    parser = get_parser()
    cli(parser.parse_args())
