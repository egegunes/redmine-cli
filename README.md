# Redmine CLI [![Build Status](https://travis-ci.com/egegunes/redmine-cli.svg?branch=master)](https://travis-ci.com/egegunes/redmine-cli) [![Coverage Status](https://coveralls.io/repos/github/egegunes/redmine-cli/badge.svg?branch=master)](https://coveralls.io/github/egegunes/redmine-cli?branch=master)

## Installation

```
$ pip3 install --user redminecli
```

## Configuration

The client looks for the config in three places: `~/.redmine.conf`,
`~/.redmine/redmine.conf` and `~/.config/redmine/redmine.conf`.

```
[accounts]
default=account1

[account1]
url=https://account1.example.com
key=KEY

[account2]
url=https://account2.example.com
key=KEY
ssl_verify=False

[aliases]
...

```

### Aliases

You can define aliases for ~issue filtering~ all commands:

```
[aliases]
wip = issues --status 2
blocked = issues --status 7
in_progress = update --status 2
```

## Usage

```
Usage: redmine [OPTIONS] COMMAND [ARGS]...

Options:
  --force / --no-force  Invalidate cache  [default: False]
  --account TEXT        Account name to use
  -h, --help            Show this message and exit.

Commands:
  create   Create new issue
  issues   List issues
  list     List various resources
  open     Open issue in browser
  project  Project commands
  show     Show issue details
  update   Update issue
  version  Print version

```

### Create a new issue

```
$ redmine create \
    --status 1 \
    --tracker 1 \
    --project 88 \
    --priority 3 \
    --subject "Fix json output" \
    --description "json output doesn't work for specific issue numbers"
```

For more options see `redmine create --help`.

### Update an issue

```
$ redmine update 107873 --assignee 112
```

For more options see `redmine update --help`.

### Filter issues

```
$ redmine issues --assignee 112 --project 88
```

For more options see `redmine issues --help`.

### See specific issues row by row

```
$ redmine issues 107873 109789
```

### JSON Output

```
$ redmine issues --assignee 112 --json
$ redmine issues 107873 109789 --json
```

### Show issue details

```
$ redmine show 107873
```

This will open issue details in `less`.

### See project roadmap

```
$ redmine project 88 roadmap
```

### List users

```
$ redmine list user
```

### Multi account

```
# This will use the default account in the redmine.conf
$ redmine issues --assignee 112

# This will use account2
$ redmine --account account2 issues --assignee 2194
```

## Contributing

Currently, project's roadmap is dictated by my needs at work. If you need a
feature or encountered a bug please open an issue. If you're OK to invest time
in this project all PR's are welcome.
