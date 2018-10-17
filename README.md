# Redmine CLI [![Build Status](https://travis-ci.com/egegunes/redmine-cli.svg?branch=master)](https://travis-ci.com/egegunes/redmine-cli)

## Installation

```
python3 -m venv venv
source venv/bin/activate
make install
```

The client looks for the config in three places: `~/.redmine.conf`,
`~/.redmine/redmine.conf` and `~/.config/redmine/redmine.conf`.

Put your Redmine instance's url and api key under `[redmine]` section.

## Usage

```
Usage: redmine [OPTIONS] COMMAND [ARGS]...

Options:
  --force / --no-force  Invalidate cache  [default: False]
  -h, --help            Show this message and exit.

Commands:
  create   Create new issue
  issues   List issues
  list     List various resources
  open     Open issue in browser
  show     Show issue details
  update   Update issue
  version  Print version

```

## Aliases

You can define aliases for ~issue filtering~ all commands:

```
[aliases]
wip = issues --status 2
blocked = issues --status 7
in_progress = update --status 2
```
