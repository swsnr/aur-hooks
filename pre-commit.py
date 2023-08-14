#!/usr/bin/python3
# Copyright 2023 Sebastian Wiesner <sebastian@swsnr.de>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


"""Pre-commit hook for AUR packages.

This hook helps with managing AUR packages.  It

- verifies source files, and
- generates and updates .SRCINFO.
"""


from subprocess import run
from pathlib import Path


def msg(msg: str) -> None:
    """Print a formatted message."""
    print(f"\x1b[01;32m*** {msg} ***\x1b[00m")  # noqa: T201


def get_added_or_changed_files() -> list[Path]:
    """Return a list of files added or changed."""
    git_diff = ["git", "diff", "-z", "--name-only", "--cached", "--diff-filter=AM"]
    return [Path(p) for p in
        run(git_diff, check=True, capture_output=True, text=True).stdout.split("\0")
        if p]


def main() -> None:
    """Run pre-commit hook."""
    for path in get_added_or_changed_files():
        if path == Path("PKGBUILD"):
            msg(f"Generating and adding .SRCINFO for {path}")
            run(["makepkg", "--verifysource", "-f"], check=True)
            with (Path.cwd() / ".SRCINFO").open("wb") as sink:
                run(["makepkg", "--printsrcinfo"], check=True, stdout=sink)
            run(["git", "add", ".SRCINFO"], check=True)


if __name__ == "__main__":
    main()
