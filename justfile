# Overridden by the nix dev shell, where these come from nixpkgs because their
# published wheels are prebuilt binaries that will not run on NixOS.
uv := env('UV', 'uv')
ruff := env('RUFF', uv + ' run --group lint ruff')
pyright := env('PYRIGHT', uv + ' run --group typecheck pyright')

# The interpreters the test matrix runs against, oldest first.
pythons := '3.11 3.12 3.13 3.14'

# show this help
default:
    @just --list

# remove build, test and coverage artifacts
clean:
    rm -rf build/ dist/ .eggs/ htmlcov/ .coverage .pytest_cache .ruff_cache docs/_build
    find . -name '*.egg-info' -exec rm -rf {} +
    find . -name '__pycache__' -exec rm -rf {} +
    find . -name '*.py[co]' -delete

# create the dev environment
install-dev:
    {{ uv }} sync --all-groups

# install the pre-commit hooks
hooks:
    pre-commit install

# check style
lint:
    {{ ruff }} check .
    {{ ruff }} format --check .

# check types (pyright, strict)
# Depends on the environment: pyright resolves imports through .venv, so on
# a fresh checkout it would otherwise report every third-party import as
# unknown.
typecheck: install-dev
    {{ pyright }}

# autoformat
format:
    {{ ruff }} check --fix .
    {{ ruff }} format .

# run the test suite, or a subset: `just test tests/test_get_port.py`
test *args:
    {{ uv }} run --group test pytest {{ args }}

# run the whole suite under the coverage gate, as CI does
# (the gate itself is configured in pyproject.toml, under [tool.coverage])
coverage:
    {{ uv }} run --group test pytest --cov

# run the test suite against one interpreter
test-python version *args:
    {{ uv }} run --python {{ version }} --group test pytest {{ args }}

# run the test suite against every supported interpreter
test-all:
    #!/usr/bin/env bash
    set -uo pipefail
    failed=()
    for version in {{ pythons }}; do
        # Fold each interpreter into its own section when running on Actions.
        if [ -n "${GITHUB_ACTIONS:-}" ]; then
            echo "::group::pytest on python $version"
        else
            echo "=== pytest on python $version"
        fi
        {{ uv }} run --python "$version" --group test pytest --cov || failed+=("$version")
        [ -n "${GITHUB_ACTIONS:-}" ] && echo "::endgroup::"
    done
    if [ ${#failed[@]} -gt 0 ]; then
        echo "failed on: ${failed[*]}" >&2
        exit 1
    fi

# build the html docs
docs:
    {{ uv }} run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html

# build sdist and wheel
dist: clean
    {{ uv }} build
    {{ uv }} tool run twine check --strict dist/*
    @ls -l dist

# everything CI runs, in the order it runs it
ci: lint typecheck test-all dist docs

# check the tag and build the distributions for it
release-build tag: (check-version tag) dist

# install the built wheel and run the tests against it, not against the source tree
test-wheel version dist_dir='dist':
    #!/usr/bin/env bash
    set -euo pipefail
    # Run from outside the checkout so the tests import the installed wheel
    # rather than the source tree sitting next to them.
    workdir="$(mktemp -d)"
    trap 'rm -rf "$workdir"' EXIT
    {{ uv }} venv --python {{ version }} "$workdir/.venv"
    {{ uv }} pip install --python "$workdir/.venv/bin/python" {{ dist_dir }}/*.whl pytest
    cp -r tests "$workdir/tests"
    cd "$workdir"
    ./.venv/bin/python -m pytest tests -p no:cacheprovider

# set the version and date the changelog, e.g. `just bump 0.8.0`
bump version:
    #!/usr/bin/env bash
    set -euo pipefail
    version="{{ trim_start_match(version, 'v') }}"
    if ! echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        echo "error: expected a version like 0.8.0, got '$version'" >&2
        exit 1
    fi
    if ! grep -qE "^${version} \(unreleased\)$" HISTORY.rst; then
        echo "error: HISTORY.rst has no '${version} (unreleased)' section to date" >&2
        grep -nE '^[0-9]+\.[0-9]+\.[0-9]+ \(' HISTORY.rst | head -3 >&2
        exit 1
    fi
    today="$(date +%F)"
    sed -i -E "s/^__version__ = '.*'$/__version__ = '${version}'/" domain_utils/__init__.py
    sed -i -E "s/^${version} \(unreleased\)$/${version} (${today})/" HISTORY.rst
    echo "__version__ = ${version}, changelog dated ${today}"
    # Leaves committing and tagging to you; this only verifies what it wrote.
    just check-version "v${version}"

# check the tag matches the packaged version and the dated changelog section
check-version tag:
    #!/usr/bin/env bash
    set -euo pipefail
    tag="{{ trim_start_match(tag, 'v') }}"
    version="$(sed -n "s/^__version__ = ['\"]\(.*\)['\"]$/\1/p" domain_utils/__init__.py)"
    if [ "$tag" != "$version" ]; then
        echo "::error::tag {{ tag }} does not match __version__ '$version'"
        exit 1
    fi
    # The changelog is part of the published description, so an undated
    # "(unreleased)" heading would ship to PyPI as the first thing on the page.
    if ! grep -qE "^${tag} \([0-9]{4}-[0-9]{2}-[0-9]{2}\)$" HISTORY.rst; then
        echo "::error::HISTORY.rst needs a dated section for ${tag}, e.g. '${tag} ($(date +%F))'"
        grep -n "^${tag} " HISTORY.rst >&2 || echo "  (no section for ${tag} at all)" >&2
        exit 1
    fi
    echo "Releasing $version"

# how to publish
release:
    @echo "Releases are published by GitHub Actions on a v* tag."
    @echo "See docs/release.rst."
