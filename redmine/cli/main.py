from collections import OrderedDict

import click

from redmine.cli.alias import AliasedGroup
from redmine.cli.config import pass_config
from redmine.cli.helpers import get_description, get_note
from redmine.cli.options import OPTIONS

from redmine.issue import Issue, IssueStatus
from redmine.priority import Priority
from redmine.project import Project
from redmine.query import Query
from redmine.redmine import Redmine
from redmine.tracker import Tracker
from redmine.user import User


CONTEXT_SETTINGS = {
    "help_option_names": ['-h', '--help']
}


@click.command(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option(
    OPTIONS["force"]["long"],
    help=OPTIONS["force"]["help"],
    show_default=True,
    default=False
)
@pass_config
@click.pass_context
def cli(ctx, cfg, **kwargs):
    redmine = Redmine(cfg.url,
                      cfg.api_key,
                      invalidate_cache=kwargs.get("force"))
    ctx.obj = redmine


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
@click.option(OPTIONS["updated-on"]["long"], default=None)
@click.option(OPTIONS["updated-after"]["long"], default=None)
@click.option(OPTIONS["updated-before"]["long"], default=None)
@click.option(OPTIONS["created-on"]["long"], default=None)
@click.option(OPTIONS["created-after"]["long"], default=None)
@click.option(OPTIONS["created-before"]["long"], default=None)
@click.pass_obj
@click.pass_context
def issues(ctx, redmine, **kwargs):
    """ List issues """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    issues = redmine.get_issues(**kwargs)

    show_project = True
    show_assignee = True

    if kwargs.get("project"):
        show_project = False

    if kwargs.get("assignee"):
        show_assignee = False

    for issue in issues:
        click.echo(Issue(**issue).as_row(show_assignee=show_assignee,
                                         show_project=show_project))


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
@click.pass_context
def update(ctx, redmine, issue_id, **kwargs):
    """ Update issue """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    if kwargs.get("edit"):
        kwargs["description"] = get_description()
        kwargs["note"] = get_note()

    updated = redmine.update_issue(issue_id, **kwargs)

    if updated:
        msg = f"Issue {issue_id} updated."
        click.echo(click.style(msg, fg="green"), err=True)


@cli.group()
def list():
    """ List various resources """
    pass


@list.command()
@click.pass_obj
def projects(redmine):
    """ List projects """

    projects = sorted(redmine.get("projects"), key=lambda x: x['name'])

    for project in projects:
        click.echo(Project(**project))


@list.command()
@click.pass_obj
def trackers(redmine):
    """ List trackers """

    trackers = sorted(redmine.get("trackers"), key=lambda x: x['id'])

    for tracker in trackers:
        click.echo(Tracker(**tracker))


@list.command()
@click.pass_obj
def statuses(redmine):
    """ List statuses """

    statuses = sorted(redmine.get("issue_statuses"), key=lambda x: x['id'])

    for status in statuses:
        click.echo(IssueStatus(**status))


@list.command()
@click.pass_obj
def queries(redmine):
    """ List queries """

    queries = sorted(redmine.get("queries"), key=lambda x: x['id'])

    for query in queries:
        click.echo(Query(**query))


@list.command()
@click.pass_obj
def priorities(redmine):
    """ List priorities """

    priorities = sorted(
        redmine.get("enumerations/issue_priorities"),
        key=lambda x: x['id']
    )

    for priority in priorities:
        click.echo(Priority(**priority))


@list.command()
@click.pass_obj
def users(redmine):
    """ List users """

    users = OrderedDict(
        sorted(redmine.get_users().items(), key=lambda x: x[1])
    )

    for user_id, name in users.items():
        click.echo(User(user_id, name))


@cli.command()
def version():
    """ Print version """

    import platform
    import pkg_resources

    system = platform.system()
    kernel = platform.release()
    python_version = platform.python_version()

    pkg_name = "redmine-cli"
    version = pkg_resources.require(pkg_name)[0].version

    msg = f"{pkg_name} {version} Python {python_version} {system} {kernel}"

    click.echo(msg)


@cli.command()
@click.argument("issue_id")
@click.pass_obj
def open(redmine, issue_id):
    """ Open issue in browser """

    from urllib.parse import urljoin

    url = urljoin(redmine.url, "/issues/{}".format(issue_id))
    click.launch(url)
