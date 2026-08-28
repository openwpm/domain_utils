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

# how to publish
release:
    @echo "Releases are published by GitHub Actions on a v* tag."
    @echo "See docs/release.rst."
