# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Name a release, and check that a tag matches the one that was named.

Reach for this through ``just bump`` and ``just check-version`` rather than
running it directly.

``__version__`` in ``domain_utils/__init__.py`` is the single source of truth
for the version; the packaging metadata reads it, and the release workflow
refuses to publish a tag that disagrees with it. The changelog is part of the
published description, so a section that is still ``Unreleased`` would ship to
PyPI as the first thing on the page.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Defined once, so the two operations cannot drift apart.
VERSION_LINE = re.compile(r"^__version__ = '(?P<version>[^']*)'$", re.MULTILINE)
UNRELEASED_HEADING = re.compile(r'^Unreleased\n-+$', re.MULTILINE)
RELEASE_NUMBER = re.compile(r'^\d+\.\d+\.\d+$')


class ReleaseError(Exception):
    """Something the caller has to fix before the release can proceed."""


def _dated_heading(version: str) -> re.Pattern[str]:
    escaped = re.escape(version)
    return re.compile(rf'^{escaped} \(\d{{4}}-\d{{2}}-\d{{2}}\)$', re.MULTILINE)


def _substitute_once(pattern: re.Pattern[str], replacement: str, text: str, *, what: str) -> str:
    """Apply ``pattern`` exactly once, or raise.

    The point of this wrapper is that a rewrite which matches nothing is an
    error rather than a silent no-op, which is the failure mode the shell
    version had.
    """
    # A callable replacement sidesteps backreference expansion, so a version
    # or heading containing a backslash cannot be reinterpreted.
    new_text, count = pattern.subn(lambda _: replacement, text, count=1)
    if count != 1:
        raise ReleaseError(f'could not rewrite {what}; expected 1 match, found {count}')
    return new_text


def read_version(init: Path) -> str:
    match = VERSION_LINE.search(init.read_text())
    if match is None:
        raise ReleaseError(f'no __version__ assignment found in {init}')
    return match.group('version')


def bump(version: str, *, init: Path, changelog: Path, today: date) -> str:
    """Set ``__version__`` and name the ``Unreleased`` changelog section."""
    if not RELEASE_NUMBER.match(version):
        raise ReleaseError(f'expected a version like 0.8.0, got {version!r}')

    changelog_text = changelog.read_text()
    if UNRELEASED_HEADING.search(changelog_text) is None:
        raise ReleaseError(
            f'{changelog.name} has no "Unreleased" section to name.\n'
            'hint: notes for unreleased changes go under an "Unreleased" heading;\n'
            '      the version number is chosen here, at release time'
        )

    heading = f'{version} ({today.isoformat()})'
    # The underline has to grow with the title: an underline shorter than its
    # title is a sphinx warning, and the docs build runs with -W.
    changelog.write_text(
        _substitute_once(
            UNRELEASED_HEADING,
            f'{heading}\n{"-" * len(heading)}',
            changelog_text,
            what='the "Unreleased" heading',
        )
    )
    init.write_text(
        _substitute_once(
            VERSION_LINE,
            f"__version__ = '{version}'",
            init.read_text(),
            what='__version__',
        )
    )

    # Verify what was written rather than trusting that it was.
    check(version, init=init, changelog=changelog)
    return heading


def check(tag: str, *, init: Path, changelog: Path) -> str:
    """Check the tag matches ``__version__`` and a dated changelog section."""
    version = tag.removeprefix('v')
    packaged = read_version(init)
    if version != packaged:
        raise ReleaseError(f'tag {tag} does not match __version__ {packaged!r}')
    if _dated_heading(version).search(changelog.read_text()) is None:
        raise ReleaseError(
            f'{changelog.name} needs a dated section for {version}, '
            f'e.g. "{version} ({date.today().isoformat()})"'
        )
    return version


def main(argv: list[str]) -> int:
    root = REPO_ROOT
    if len(argv) >= 2 and argv[0] == '--root':
        root = Path(argv[1])
        argv = argv[2:]
    init = root / 'domain_utils' / '__init__.py'
    changelog = root / 'HISTORY.rst'

    try:
        match argv:
            case ['bump', version]:
                heading = bump(version, init=init, changelog=changelog, today=date.today())
                print(f'__version__ = {version}, changelog section is now {heading}')
            case ['check', tag]:
                print(f'Releasing {check(tag, init=init, changelog=changelog)}')
            case _:
                print(f'usage: {Path(__file__).name} [--root DIR] (bump VERSION | check TAG)')
                return 2
    except ReleaseError as error:
        # ::error:: makes it an annotation on the workflow run.
        print(f'::error::{error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
