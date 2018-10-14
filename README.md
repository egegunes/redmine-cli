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
  create      Create new issue
  issues      List issues
  me          List issues assigned to requester
  open        Open issue in browser
  priorities  List priorities
  projects    List projects
  queries     List queries
  show        Show issue details
  statuses    List statuses
  trackers    List trackers
  update      Update issue
  users       List users
  version     Print version

```

## Aliases

You can define aliases for issue filtering commands. For example:

```
[aliases]
wip = issues --query 44
blocked = me --status 7
```
