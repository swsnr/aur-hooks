#!/usr/bin/python3
# Copyright 2023 Sebastian Wiesner <sebastian@swsnr.de>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


"""Install script for AUR hooks."""


from pathlib import Path
from argparse import ArgumentParser


DIRECTORY = Path(__file__).absolute().parent


HOOKS = [
    "pre-commit",
    "prepare-commit-msg",
]


def main() -> None:
    """Install hooks."""
    parser = ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("directory", type=Path, nargs="?")
    args = parser.parse_args()
    directory = args.directory or Path.cwd()
    if directory.samefile(DIRECTORY):
        parser.error("Cannot install in this directory")
        return

    for hook in HOOKS:
        hookdir = directory / ".git" / "hooks"
        srcfile = (DIRECTORY / hook).with_suffix(".py")
        destfile = hookdir / hook
        print(f"Linking {srcfile} to {destfile}")  # noqa: T201
        if args.force:
            destfile.unlink(missing_ok=True)
        destfile.symlink_to(srcfile)


if __name__ == "__main__":
    main()
