import os
import configparser

import click

from redmine.redmine import Redmine
from redmine.issue import Issue, IssueRow
from redmine.project import Project
from redmine.tracker import Tracker


def read_config():
    HOME = os.getenv("HOME")
    CONFIG_PATHS = [
        os.path.join(HOME, ".redmine.conf"),
        os.path.join(HOME, ".redmine/redmine.conf"),
        os.path.join(HOME, ".config/redmine/redmine.conf")
    ]

    config = configparser.ConfigParser()

    for path in CONFIG_PATHS:
        if os.path.isfile(path):
            config.read(path)
            break

    return config


@click.group()
@click.pass_context
def cli(ctx):
    config = read_config()
    redmine = Redmine(
        config["redmine"]["url"],
        config["redmine"]["key"],
        config["redmine"]["me"]
    )
    ctx.obj = redmine


@cli.command()
@click.option("--status", default=None)
@click.option("--tracker", default=None)
@click.option("--limit", default=25)
@click.option("--sort", default="id:desc")
@click.pass_obj
def me(redmine, **kwargs):
    """ List issues assigned to requester """

    issues = redmine.get_issues(assignee=redmine.me, **kwargs)

    for issue in issues:
        click.echo(IssueRow(**issue))


@cli.command()
@click.option("--assignee", default=None)
@click.option("--status", default=None)
@click.option("--tracker", default=None)
@click.option("--limit", default=25)
@click.option("--sort", default="id:desc")
@click.pass_obj
def issues(redmine, **kwargs):
    """ List issues """

    issues = redmine.get_issues(**kwargs)

    for issue in issues:
        click.echo(IssueRow(**issue))


@cli.command()
@click.argument("issue_id")
@click.option("--journals/--no-journals", default=True)
@click.pass_obj
def show(redmine, issue_id, journals):
    """ Show issue details """

    issue = redmine.get_issue(issue_id, journals)

    click.echo(Issue(**issue))


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
