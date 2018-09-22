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

    click.echo(
        Issue(**issue,
              statuses=redmine.statuses,
              priorities=redmine.priorities,
              users=redmine.users)
    )


@cli.command()
@click.pass_obj
def create(redmine):
    """ Create new issue """

    redmine.create_issue()


@cli.command()
@click.argument("issue_id")
@click.pass_obj
def update(redmine, issue_id):
    """ Update issue """

    redmine.update_issue(issue_id)


@cli.command()
@click.pass_obj
def projects(redmine):
    """ List projects """

    projects = redmine.get_projects()

    for project in projects:
        click.echo(Project(**project))


@cli.command()
@click.pass_obj
def trackers(redmine):
    """ List trackers """

    trackers = redmine.get_trackers()

    for tracker in trackers:
        click.echo(Tracker(**tracker))


@cli.command()
@click.pass_obj
def statuses(redmine):
    """ List statuses """

    statuses = redmine.get_statuses()

    for status in statuses:
        click.echo(IssueStatus(**status))


@cli.command()
@click.pass_obj
def queries(redmine):
    """ List queries """

    queries = redmine.get_queries()

    for query in queries:
        click.echo(Query(**query))


@cli.command()
@click.pass_obj
def priorities(redmine):
    """ List priorities """

    priorities = redmine.get_priorities()

    for priority in priorities:
        click.echo(Priority(**priority))


@cli.command()
@click.pass_obj
def users(redmine):
    """ List users """

    users = redmine.get_users()

    for user_id, name in users.items():
        click.echo(User(user_id, name))
