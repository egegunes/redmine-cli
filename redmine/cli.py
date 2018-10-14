import configparser
import os
from collections import OrderedDict

import click

from redmine.issue import Issue, IssueStatus
from redmine.priority import Priority
from redmine.project import Project
from redmine.query import Query
from redmine.redmine import Redmine
from redmine.tracker import Tracker
from redmine.user import User


class Config:
    def __init__(self, *args, **kwargs):
        HOME = os.getenv("HOME")
        self.paths = [
            os.path.join(HOME, ".redmine.conf"),
            os.path.join(HOME, ".redmine/redmine.conf"),
            os.path.join(HOME, ".config/redmine/redmine.conf")
        ]
        self.url = None
        self.api_key = None
        self.me = None
        self.aliases = {}
        self.read()

    def read(self):
        config = configparser.ConfigParser()

        for path in self.paths:
            if os.path.isfile(path):
                config.read(path)
                break

        self.url = config["redmine"]["url"]
        self.api_key = config["redmine"]["key"]

        if "me" in config["redmine"]:
            self.me = config["redmine"]["me"]

        try:
            self.aliases.update(config.items("aliases"))
        except configparser.NoSectionError:
            pass

        return config


pass_config = click.make_pass_decorator(Config, ensure=True)


class AliasedGroup(click.Group):
    def group_params(self, params):
        grouped_params = []

        for i in range(0, len(params), 2):
            grouped_params.append((params[i].lstrip("-"), params[i + 1]))

        return grouped_params

    def get_command(self, ctx, cmd_name):
        # Return builtin commands as normal
        ctx.alias = False
        c = click.Group.get_command(self, ctx, cmd_name)
        if c is not None:
            return c

        cfg = ctx.ensure_object(Config)

        if cmd_name in cfg.aliases:
            actual_cmd = cfg.aliases[cmd_name].split()
            params = self.group_params(actual_cmd[1:])
            for param in params:
                ctx.alias = True
                ctx.params[param[0]] = param[1]
            return click.Group.get_command(self, ctx, actual_cmd[0])


def get_description():
    MARKER = "# Write your description above"
    message = click.edit('\n\n' + MARKER)
    if message is not None:
        return message.split(MARKER, 1)[0].rstrip('\n')


def get_note():
    MARKER = "# Write your note above"
    message = click.edit('\n\n' + MARKER)
    if message is not None:
        return message.split(MARKER, 1)[0].rstrip('\n')


OPTIONS = {
    "project": {
        "long": "--project",
        "short": "-P",
    },
    "status": {
        "long": "--status",
        "short": "-s"
    },
    "tracker": {
        "long": "--tracker",
        "short": "-t"
    },
    "priority": {
        "long": "--priority",
        "short": "-p"
    },
    "assignee": {
        "long": "--assignee",
        "short": "-a"
    },
    "query": {
        "long": "--query",
        "short": "-q"
    },
    "subject": {
        "long": "--subject",
        "short": "-S"
    },
    "description": {
        "long": "--description",
        "short": "-D"
    },
    "note": {
        "long": "--note",
        "short": "-n"
    },
    "start": {
        "long": "--start",
        "short": "-b"
    },
    "due": {
        "long": "--due",
        "short": "-d"
    },
    "done": {
        "long": "--done",
        "short": "-f"
    },
    "parent": {
        "long": "--parent",
        "short": "-m"
    },
    "limit": {
        "long": "--limit",
        "short": "-l"
    },
    "sort": {
        "long": "--sort",
        "short": "-x"
    },
    "journals": {
        "long": "--journals/--no-journals",
        "short": "-j/-J"
    },
    "edit": {
        "long": "--edit/--no-edit",
        "short": "-e/-E"
    }
}


CONTEXT_SETTINGS = {
    "help_option_names": ['-h', '--help']
}


@click.command(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@pass_config
@click.pass_context
def cli(ctx, cfg, **kwargs):
    redmine = Redmine(cfg.url, cfg.api_key, cfg.me)
    ctx.obj = redmine


@cli.command()
@click.option(
    OPTIONS["status"]["long"],
    OPTIONS["status"]["short"],
    default=None
)
@click.option(
    OPTIONS["tracker"]["long"],
    OPTIONS["tracker"]["short"],
    default=None
)
@click.option(
    OPTIONS["project"]["long"],
    OPTIONS["project"]["short"],
    default=None
)
@click.option(
    OPTIONS["priority"]["long"],
    OPTIONS["priority"]["short"],
    default=None
)
@click.option(
    OPTIONS["start"]["long"],
    OPTIONS["start"]["short"],
    default=None
)
@click.option(
    OPTIONS["due"]["long"],
    OPTIONS["due"]["short"],
    default=None
)
@click.option(
    OPTIONS["done"]["long"],
    OPTIONS["done"]["short"],
    default=None
)
@click.option(
    OPTIONS["parent"]["long"],
    OPTIONS["parent"]["short"],
    default=None
)
@click.option(
    OPTIONS["limit"]["long"],
    OPTIONS["limit"]["short"],
    default=25
)
@click.option(
    OPTIONS["sort"]["long"],
    OPTIONS["sort"]["short"],
    default="id:desc"
)
@click.pass_obj
@click.pass_context
def me(ctx, redmine, **kwargs):
    """ List issues assigned to requester """

    if not redmine.me:
        msg = "redmine: Please add your user id to use `me` command"
        return click.echo(click.style(msg, fg="red"), err=True)

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    issues = redmine.get_issues(assignee=redmine.me, **kwargs)

    for issue in issues:
        click.echo(Issue(**issue).as_row())


@cli.command()
@click.option(
    OPTIONS["assignee"]["long"],
    OPTIONS["assignee"]["short"],
    default=None
)
@click.option(
    OPTIONS["status"]["long"],
    OPTIONS["status"]["short"],
    default=None
)
@click.option(
    OPTIONS["tracker"]["long"],
    OPTIONS["tracker"]["short"],
    default=None
)
@click.option(
    OPTIONS["project"]["long"],
    OPTIONS["project"]["short"],
    default=None
)
@click.option(
    OPTIONS["priority"]["long"],
    OPTIONS["priority"]["short"],
    default=None
)
@click.option(
    OPTIONS["query"]["long"],
    OPTIONS["query"]["short"],
    default=None
)
@click.option(
    OPTIONS["start"]["long"],
    OPTIONS["start"]["short"],
    default=None
)
@click.option(
    OPTIONS["due"]["long"],
    OPTIONS["due"]["short"],
    default=None
)
@click.option(
    OPTIONS["done"]["long"],
    OPTIONS["done"]["short"],
    default=None
)
@click.option(
    OPTIONS["parent"]["long"],
    OPTIONS["parent"]["short"],
    default=None
)
@click.option(
    OPTIONS["limit"]["long"],
    OPTIONS["limit"]["short"],
    default=25
)
@click.option(
    OPTIONS["sort"]["long"],
    OPTIONS["sort"]["short"],
    default="id:desc"
)
@click.pass_obj
@click.pass_context
def issues(ctx, redmine, **kwargs):
    """ List issues """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    issues = redmine.get_issues(**kwargs)

    for issue in issues:
        click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issue_id")
@click.option(
    OPTIONS["journals"]["long"],
    OPTIONS["journals"]["short"],
    default=True
)
@click.pass_obj
def show(redmine, issue_id, journals):
    """ Show issue details """

    issue = redmine.get_issue(issue_id, journals)

    issue = Issue(**issue,
                  statuses=redmine.statuses,
                  priorities=redmine.priorities,
                  projects=redmine.projects,
                  users=redmine.users)

    click.echo_via_pager(str(issue))


@cli.command()
@click.option(
    OPTIONS["subject"]["long"],
    OPTIONS["subject"]["short"],
    prompt=True
)
@click.option(
    OPTIONS["description"]["long"],
    OPTIONS["description"]["short"],
    default=None
)
@click.option(
    OPTIONS["edit"]["long"],
    OPTIONS["edit"]["short"],
    default=False
)
@click.option(
    OPTIONS["project"]["long"],
    OPTIONS["project"]["short"],
    prompt=True
)
@click.option(
    OPTIONS["status"]["long"],
    OPTIONS["status"]["short"],
    prompt=True
)
@click.option(
    OPTIONS["tracker"]["long"],
    OPTIONS["tracker"]["short"],
    prompt=True
)
@click.option(
    OPTIONS["priority"]["long"],
    OPTIONS["priority"]["short"],
    prompt=True
)
@click.option(
    OPTIONS["assignee"]["long"],
    OPTIONS["assignee"]["short"],
    default=None
)
@click.option(
    OPTIONS["start"]["long"],
    OPTIONS["start"]["short"],
    default=None
)
@click.option(
    OPTIONS["due"]["long"],
    OPTIONS["due"]["short"],
    default=None
)
@click.option(
    OPTIONS["done"]["long"],
    OPTIONS["done"]["short"],
    default=None
)
@click.option(
    OPTIONS["parent"]["long"],
    OPTIONS["parent"]["short"],
    default=None
)
@click.pass_obj
def create(redmine, *args, **kwargs):
    """ Create new issue """

    if kwargs.get("edit"):
        kwargs["description"] = get_description()

    issue = redmine.create_issue(**kwargs)

    click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issue_id")
@click.option(
    OPTIONS["subject"]["long"],
    OPTIONS["subject"]["short"],
    default=None
)
@click.option(
    OPTIONS["project"]["long"],
    OPTIONS["project"]["short"],
    default=None
)
@click.option(
    OPTIONS["status"]["long"],
    OPTIONS["status"]["short"],
    default=None
)
@click.option(
    OPTIONS["tracker"]["long"],
    OPTIONS["tracker"]["short"],
    default=None
)
@click.option(
    OPTIONS["priority"]["long"],
    OPTIONS["priority"]["short"],
    default=None
)
@click.option(
    OPTIONS["description"]["long"],
    OPTIONS["description"]["short"],
    default=None
)
@click.option(
    OPTIONS["note"]["long"],
    OPTIONS["note"]["short"],
    default=None
)
@click.option(
    OPTIONS["edit"]["long"],
    OPTIONS["edit"]["short"],
    default=False
)
@click.option(
    OPTIONS["assignee"]["long"],
    OPTIONS["assignee"]["short"],
    default=None
)
@click.option(
    OPTIONS["start"]["long"],
    OPTIONS["start"]["short"],
    default=None
)
@click.option(
    OPTIONS["due"]["long"],
    OPTIONS["due"]["short"],
    default=None
)
@click.option(
    OPTIONS["done"]["long"],
    OPTIONS["done"]["short"],
    default=None
)
@click.option(
    OPTIONS["parent"]["long"],
    OPTIONS["parent"]["short"],
    default=None
)
@click.pass_obj
def update(redmine, issue_id, **kwargs):
    """ Update issue """

    if kwargs.get("edit"):
        kwargs["description"] = get_description()
        kwargs["notes"] = get_note()

    updated = redmine.update_issue(issue_id, **kwargs)

    if updated:
        msg = f"Issue {issue_id} updated."
        click.echo(click.style(msg, fg="green"))


@cli.command()
@click.pass_obj
def projects(redmine):
    """ List projects """

    projects = sorted(redmine.get("projects"), key=lambda x: x['name'])

    for project in projects:
        click.echo(Project(**project))


@cli.command()
@click.pass_obj
def trackers(redmine):
    """ List trackers """

    trackers = sorted(redmine.get("trackers"), key=lambda x: x['id'])

    for tracker in trackers:
        click.echo(Tracker(**tracker))


@cli.command()
@click.pass_obj
def statuses(redmine):
    """ List statuses """

    statuses = sorted(redmine.get("issue_statuses"), key=lambda x: x['id'])

    for status in statuses:
        click.echo(IssueStatus(**status))


@cli.command()
@click.pass_obj
def queries(redmine):
    """ List queries """

    queries = sorted(redmine.get("queries"), key=lambda x: x['id'])

    for query in queries:
        click.echo(Query(**query))


@cli.command()
@click.pass_obj
def priorities(redmine):
    """ List priorities """

    priorities = sorted(
        redmine.get("enumerations/issue_priorities"),
        key=lambda x: x['id']
    )

    for priority in priorities:
        click.echo(Priority(**priority))


@cli.command()
@click.pass_obj
def users(redmine):
    """ List users """

    users = OrderedDict(
        sorted(redmine.get_users().items(), key=lambda x: x[1])
    )

    for user_id, name in users.items():
        click.echo(User(user_id, name))
