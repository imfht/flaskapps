<h1 align="center" style="margin-top:0;">
  Bento
</h1>

<p align="center">
  <a href="https://pypi.org/project/bento-cli/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/bento-cli?style=flat-square&color=blue">
  </a>
  <a href="https://pypi.org/project/bento-cli/">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/bento-cli?style=flat-square&color=green">
  </a>
</p>

See our public [README.md](https://github.com/returntocorp/bento) for Bento details.

# Developing

## Setup

Install pre-commit hooks:

```
brew install pre-commit
pre-commit install -f
```

Install poetry:

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

Install bento dev dependencies:

```
poetry install
```

Setup git commit message template:

```
git config commit.template .gitmessage
```

## Testing

To run all tests:

`make test` or `poetry run pytest`

To run acceptance tests:

`make qa-test` or `poetry run pytest tests/acceptance/qa.py`

To regenerate acceptance test output to reflect current behavior of bento:

`make regenerate-tests` or `poetry run python tests/acceptance/qa.py`

To build and run bento:

```
make
poetry run bento check
```

See [bento-core usage](https://returntocorp.quip.com/3K3gAxDYZIy6/Using-the-bento-core-repo) for more developer workflow details.
