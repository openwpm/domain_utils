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

# set the version and name the changelog section, e.g. `just bump 0.8.0`
bump version:
    {{ uv }} run --script scripts/release.py bump {{ version }}

# check the tag matches the packaged version and the dated changelog section
check-version tag:
    {{ uv }} run --script scripts/release.py check {{ tag }}

# how to publish
release:
    @echo "Releases are published by GitHub Actions on a v* tag."
    @echo "See docs/release.rst."
