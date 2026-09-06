"""Tests for scripts/release.py, the version and changelog handling."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'release.py'

CHANGELOG = """=======
History
=======

Unreleased
----------

* Something that landed after 0.8.0.


0.8.0 (2026-09-05)
------------------

* The previous release.
"""


def _repo(tmp_path: Path, changelog: str = CHANGELOG, version: str = '0.8.0') -> Path:
    (tmp_path / 'domain_utils').mkdir(parents=True)
    (tmp_path / 'domain_utils' / '__init__.py').write_text(f"__version__ = '{version}'\n")
    (tmp_path / 'HISTORY.rst').write_text(changelog)
    return tmp_path


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), '--root', str(root), *args],
        capture_output=True,
        text=True,
    )


def test_bump_names_the_unreleased_section(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = _run(root, 'bump', '0.9.0')
    assert result.returncode == 0, result.stderr
    changelog = (root / 'HISTORY.rst').read_text()
    assert 'Unreleased' not in changelog
    assert (root / 'domain_utils' / '__init__.py').read_text() == "__version__ = '0.9.0'\n"


def test_bump_grows_the_heading_underline(tmp_path: Path) -> None:
    # An underline shorter than its title is a sphinx warning, and the docs
    # build runs with -W.
    root = _repo(tmp_path)
    assert _run(root, 'bump', '0.9.0').returncode == 0
    lines = (root / 'HISTORY.rst').read_text().splitlines()
    heading = next(i for i, line in enumerate(lines) if line.startswith('0.9.0 ('))
    assert len(lines[heading + 1]) == len(lines[heading])


def test_the_same_heading_can_become_a_patch_or_a_minor(tmp_path: Path) -> None:
    for version in ('0.8.1', '0.9.0', '1.0.0'):
        root = _repo(tmp_path / version)
        assert _run(root, 'bump', version).returncode == 0
        assert f'{version} (' in (root / 'HISTORY.rst').read_text()


def test_bump_refuses_without_an_unreleased_section(tmp_path: Path) -> None:
    root = _repo(tmp_path, changelog='=======\nHistory\n=======\n\n0.8.0 (2026-09-05)\n---\n')
    result = _run(root, 'bump', '0.9.0')
    assert result.returncode == 1
    assert 'no "Unreleased" section' in result.stderr
    # and nothing was written
    assert (root / 'domain_utils' / '__init__.py').read_text() == "__version__ = '0.8.0'\n"


def test_bump_refuses_a_version_that_is_not_a_release_number(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    result = _run(root, 'bump', '0.9')
    assert result.returncode == 1
    assert 'expected a version like' in result.stderr


def test_check_accepts_a_matching_tag(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    assert _run(root, 'bump', '0.9.0').returncode == 0
    for tag in ('v0.9.0', '0.9.0'):
        result = _run(root, 'check', tag)
        assert result.returncode == 0, result.stderr
        assert 'Releasing 0.9.0' in result.stdout


def test_check_rejects_a_tag_that_disagrees_with_the_version(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    assert _run(root, 'bump', '0.9.0').returncode == 0
    result = _run(root, 'check', 'v0.9.1')
    assert result.returncode == 1
    assert 'does not match __version__' in result.stderr


def test_check_rejects_an_undated_section(tmp_path: Path) -> None:
    # The changelog ships as the PyPI description, so an unnamed section would
    # be the first thing on the page.
    root = _repo(tmp_path, version='0.9.0')
    result = _run(root, 'check', 'v0.9.0')
    assert result.returncode == 1
    assert 'needs a dated section' in result.stderr
