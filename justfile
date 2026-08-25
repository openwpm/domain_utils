uv := env('UV', 'uv')
# Overridden by the nix dev shell, where ruff comes from nixpkgs because the
# published wheel is a prebuilt binary that will not run on NixOS.
ruff := env('RUFF', uv + ' run --group lint ruff')

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

# check style
lint:
    {{ ruff }} check .
    {{ ruff }} format --check .

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

# build the html docs
docs:
    {{ uv }} run --group docs sphinx-build -W --keep-going -b html docs docs/_build/html

# build sdist and wheel
dist: clean
    {{ uv }} build
    @ls -l dist

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
