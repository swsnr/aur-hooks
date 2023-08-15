# AUR hooks

My personal git hooks for AUR packages, inspired by [aurpublish].

[aurpublish]: https://github.com/eli-schwartz/aurpublish

## Installation

```console
$ git clone https://github.com/swsnr/aur-hooks.git
$ cd aur-hooks
$./install.py /path/to/AUR/repo`
```

## Features

- Prepare commit message according to version update.
- Run namcap on `PKGBUILD`.
- Run shellcheck on `PKGBUILD`.
- Verify source files before a commit.
- Automatically update `.SRCINFO` before a commit.

## License

This Source Code Form is subject to the terms of the Mozilla Public License, v.
2.0. If a copy of the MPL was not distributed with this file, You can obtain one
at <https://mozilla.org/MPL/2.0/>.
