import configparser
import os

import click

from redmine.issue import Issue, IssueStatus
from redmine.priority import Priority
from redmine.project import Project
from redmine.query import Query
from redmine.redmine import Redmine
from redmine.tracker import Tracker
from redmine.user import User


from collections import OrderedDict

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


@click.command(cls=AliasedGroup)
@pass_config
@click.pass_context
def cli(ctx, cfg, **kwargs):
    redmine = Redmine(cfg.url, cfg.api_key, cfg.me)
    ctx.obj = redmine


@cli.command()
@click.option("--status", default=None)
@click.option("--tracker", default=None)
@click.option("--project", default=None)
@click.option("--limit", default=25)
@click.option("--sort", default="id:desc")
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
@click.option("--assignee", default=None)
@click.option("--status", default=None)
@click.option("--tracker", default=None)
@click.option("--project", default=None)
@click.option("--query", default=None)
@click.option("--limit", default=25)
@click.option("--sort", default="id:desc")
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
@click.option("--journals/--no-journals", default=True)
@click.pass_obj
def show(redmine, issue_id, journals):
    """ Show issue details """

    issue = redmine.get_issue(issue_id, journals)

    issue = Issue(**issue,
                  statuses=redmine.statuses,
                  priorities=redmine.priorities,
                  users=redmine.users)

    click.echo_via_pager(str(issue))


@cli.command()
@click.option("--subject", prompt=True)
@click.option("--project", prompt=True)
@click.option("--status", prompt=True)
@click.option("--tracker", prompt=True)
@click.option("--priority", prompt=True)
@click.option("--description/--no-description", default=True)
@click.option("--assignee", default=None)
@click.option("--start", default=None)
@click.option("--due", default=None)
@click.option("--done", default=None)
@click.option("--parent", default=None)
@click.pass_obj
def create(redmine, *args, **kwargs):
    """ Create new issue """

    if kwargs.get("description"):
        kwargs["description"] = click.edit()

    issue = redmine.create_issue(**kwargs)

    click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issue_id")
@click.option("--note/--no-note", default=False)
@click.option("--subject", default=None)
@click.option("--project", default=None)
@click.option("--status", default=None)
@click.option("--tracker", default=None)
@click.option("--priority", default=None)
@click.option("--description/--no-description", default=False)
@click.option("--assignee", default=None)
@click.option("--parent", default=None)
@click.option("--start", default=None)
@click.option("--due", default=None)
@click.option("--done", default=None)
@click.pass_obj
def update(redmine, issue_id, **kwargs):
    """ Update issue """

    if kwargs.get("note"):
        kwargs["notes"] = click.edit()

    if kwargs.get("description"):
        kwargs["description"] = click.edit()

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

    priorities = sorted(redmine.get("enumerations/issue_priorities"), key=lambda x: x['id'])

    for priority in priorities:
        click.echo(Priority(**priority))


@cli.command()
@click.pass_obj
def users(redmine):
    """ List users """

    users = OrderedDict(sorted(redmine.get_users().items(), key=lambda x: x[1]))

    for user_id, name in users.items():
        click.echo(User(user_id, name))
