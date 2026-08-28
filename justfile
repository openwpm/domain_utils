uv := env('UV', 'uv')
# Overridable so a ruff already on PATH can be used instead.
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

# run the test suite
test *args:
    {{ uv }} run --group test pytest {{ args }}

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
