import argparse
import os
import re
import subprocess

import dulwich.porcelain
from dulwich.errors import NotGitRepository

from urllib.parse import urlparse
from posixpath import basename

WORKFLOW_DATABASE = {}
PLUGIN_DATABASE = {}
PACKAGE_DATABASE = {}

SETUP_SETS = ["common", "sparc", "msk"]
LIST_TYPES = ["plugin", "package", "workflow"]


def _parse_arguments():
    parser = argparse.ArgumentParser(prog="SetupMAPClient")
    parser.add_argument("-d", "--destination", help="Directory location to setup MAP Client.", default=os.curdir)
    parser.add_argument("-s", "--size", action='store_true', help="Allow pre-release versions")
    parser.add_argument("set", help=f"The set to setup MAP Client with, one of: {SETUP_SETS}")

    return parser.parse_args()


def _read_set_file(base_path, set_name, set_type):
    listing = []
    set_filename = os.path.join(base_path, f"{set_name}.{set_type}_list")
    if os.path.isfile(set_filename):
        with open(set_filename) as f:
            content = f.readlines()

        for line in content:
            line = line.rstrip()
            line = re.sub("#.*$", "", line)
            or_list_types = "|".join(LIST_TYPES)
            or_setup_sets_types = "|".join(SETUP_SETS)
            match = re.match(f"^@include ({or_setup_sets_types})\\.({or_list_types})_list$", line)
            if match:
                listing.extend(_read_set_file(base_path, match.group(1), match.group(2)))
            else:
                if line:
                    listing.append({"set": set_name, "uri": line})

    return listing


def _clone_repo(uri, target):
    cloned = False
    try:
        dulwich.porcelain.clone(uri, target=target)
        cloned = True
    except FileExistsError:
        print(f"Repository already exists: {target}")
    except NotGitRepository:
        print(f"Not a git repo: {uri}")

    return cloned


def main():
    args = _parse_arguments()

    setup_set = args.set if args.set in SETUP_SETS else "common"

    here = os.path.abspath(os.path.dirname(__file__))
    mapclient_target = os.path.join(args.destination, "mapclient")
    if _clone_repo("https://github.com/MusculoskeletalAtlasProject/mapclient/", mapclient_target):
        subprocess.call(["pip", "install", "-e", os.path.join(mapclient_target, "src")])

    for list_type in LIST_TYPES:
        resources = _read_set_file(os.path.join(here, "set_files"), setup_set, list_type)
        for resource in resources:
            parsed_uri = urlparse(resource["uri"])
            if parsed_uri.scheme == "https":
                name = basename(parsed_uri.path)
                name = name.replace(".git", "")
                destination_dir = os.path.join(args.destination, f"{list_type}s", resource["set"])
                if not os.path.isdir(destination_dir):
                    os.makedirs(destination_dir)
                repo_path = os.path.join(destination_dir, name)
                if _clone_repo(resource["uri"], repo_path) and list_type == "package":
                    subprocess.call(["pip", "install", "-e", repo_path])


if __name__ == "__main__":
    main()
