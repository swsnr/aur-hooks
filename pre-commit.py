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


import sys
from json import loads
from subprocess import run, CalledProcessError
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


WRAPPER="""\
# shellcheck shell=bash enable=all

# Declare input variables to PKGBUILD
export srcdir=''
export pkgdir=''

# Include makepkg to set all build variables such as CFLAGS
source /etc/makepkg.conf

{PKGBUILD}

# Mark all sorts of PKGBUILD variables as exported to prevent shellcheck from
# marking them as unused
export pkgname pkgbase epoch pkgver pkgrel pkgdesc url license arch \
    source \
    depends optdepends makedepends conflicts provides \
    md5sums sha256sums sha512sums b2sums
"""


def shellcheck_pkgbuild(pkgbuild: Path) -> None:
    """Run shellcheck on `file`."""
    shellcheck = ["shellcheck", "-x", "--format=json1", "--severity=style", "-"]
    result = run(shellcheck, text=True, capture_output=True,
        input=WRAPPER.format(PKGBUILD=pkgbuild.read_text()))
    comments = loads(result.stdout)["comments"]
    offset = WRAPPER.splitlines().index("{PKGBUILD}")
    for comment in comments:
        line = int(comment["line"] - offset)
        column = comment["column"]
        level = comment["level"]
        code = "SC" + str(comment["code"])
        code_url = f"https://github.com/koalaman/shellcheck/wiki/{code}"
        message = comment["message"]
        color = {
            "style": "\x1b[32m",
            "warning": "\x1b[33m",
            "error": "\x1b[01;31m",
        }.get(level, "")
        print(  # noqa: T201
            f"{color}{pkgbuild}:{line}:{column}: {level}: "
            f"\x1b]8;;{code_url}\x1b\\{code}\x1b]8;;\x1b\\: {message}\x1b[00m")
    result.check_returncode()


def main() -> None:
    """Run pre-commit hook."""
    try:
        for path in get_added_or_changed_files():
            if path == Path("PKGBUILD"):
                msg(f"Running shellcheck on {path}")
                shellcheck_pkgbuild(path)
                msg(f"Running namcap on {path}")
                run(["namcap", path], check=True)
                msg(f"Generating and adding .SRCINFO for {path}")
                run(["makepkg", "--verifysource", "-f"], check=True)
                with (Path.cwd() / ".SRCINFO").open("wb") as sink:
                    run(["makepkg", "--printsrcinfo"], check=True, stdout=sink)
                run(["git", "add", ".SRCINFO"], check=True)
    except CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
