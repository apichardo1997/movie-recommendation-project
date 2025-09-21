

## Setup
All code is specific for MacOS. For other OSs such as linux, please adjust accordingly.

### Poetry environment

The following requires having [poetry](https://python-poetry.org/docs/) installed.

Install python 3.12:
```
brew update
brew install pyenv
pyenv install 3.12
```

Now you can install the poetry environment for this project as follows:
```
poetry install
```

### Pre-commit hooks

Install the pre-commit hooks with:
```
poetry run pre-commit install
```
Now the [ruff](https://github.com/astral-sh/ruff) linter and formatter will run automatically before each commit.
