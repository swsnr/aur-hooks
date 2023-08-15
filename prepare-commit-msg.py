#!/usr/bin/python3
# Copyright 2023 Sebastian Wiesner <sebastian@swsnr.de>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


"""Prepare commit message for AUR packages."""


import sys
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
from typing import Optional


@dataclass
class Pkginfo:
    """Information about a package extracted from a PKGBUILD."""

    pkgbase: str
    pkgname: str
    epoch: Optional[str]
    pkgver: str
    pkgrel: str
    pkgver_type: str


def git_diff(diff_filter: str) -> list[Path]:
    """Return a list of files added or changed."""
    git_diff = ["git", "diff", "-z", "--name-only", "--cached",
        f"--diff-filter={diff_filter}"]
    return [Path(p) for p in
        run(git_diff, check=True, capture_output=True, text=True).stdout.split("\0")
        if p]


def get_pkginfo() -> Pkginfo:
    """Extract package information."""
    script = r"""\
source PKGBUILD
printf '%s\x00%s\x00%s\x00%s\x00%s\x00%s' \
    "$pkgbase" "$pkgname" "$epoch" "$pkgver" "$pkgrel" "$(type -t pkgver)"
    """
    output = run(["bash", "-c", script],
        capture_output=True, check=True, text=True).stdout
    pkgbase, pkgname, epoch, pkgver, pkgrel, pkgver_type = output.split("\x00")
    return Pkginfo(
        pkgbase=pkgbase or pkgname,
        pkgname=pkgname,
        epoch=epoch or None,
        pkgver=pkgver,
        pkgrel=pkgrel,
        pkgver_type=pkgver_type,
    )


def main() -> None:
    """Prepare and print a commit message."""
    msg_file = Path(sys.argv[1])
    old_msg = msg_file.read_text()

    msg_lines = []

    for file in git_diff("A"):
        if file == Path("PKGBUILD"):
            info = get_pkginfo()
            epoch = f"{info.epoch}:" if info.epoch else ""
            msg_lines.append(
                f"Initial upload: {info.pkgbase} {epoch}{info.pkgver}-{info.pkgrel}")
            break

    for file in git_diff("M"):
        if file == Path("PKGBUILD"):
            info = get_pkginfo()
            epoch = f"{info.epoch}:" if info.epoch else ""
            msg_lines.append(
                f"upgpkg: {info.pkgbase} {epoch}{info.pkgver}-{info.pkgrel}")
            # iF pkgrel is 1 and there's no pkgver function (which would
            # indicate a VCS package) assume that this is a new upstream
            # release.
            if info.pkgrel == "1" and info.pkgver_type != "function":
                msg_lines.append("")
                msg_lines.append("Upstream release")
            break

    msg_lines.append(old_msg)
    msg_file.write_text("\n".join(msg_lines))


if __name__ == "__main__":
    main()
