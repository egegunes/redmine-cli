# Redmine CLI [![Build Status](https://travis-ci.com/egegunes/redmine-cli.svg?branch=master)](https://travis-ci.com/egegunes/redmine-cli) [![Coverage Status](https://coveralls.io/repos/github/egegunes/redmine-cli/badge.svg?branch=master)](https://coveralls.io/github/egegunes/redmine-cli?branch=master)

## Installation

```
$ pip3 install --user redminecli
```

## Configuration

The client looks for the config in three places: `~/.redmine.conf`,
`~/.redmine/redmine.conf` and `~/.config/redmine/redmine.conf`.

```
[redmine]
url=https://example.com
key=APIKEY
```

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
