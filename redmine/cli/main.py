import json
from collections import OrderedDict

import click
from requests.exceptions import HTTPError

from redmine.cli.alias import AliasedGroup
from redmine.cli.config import Config, pass_config
from redmine.cli.helpers import get_description, get_note
from redmine.cli.options import OPTIONS
from redmine.issue import Issue, IssueStatus
from redmine.priority import Priority
from redmine.project import Project
from redmine.query import Query
from redmine.redmine import Redmine
from redmine.tracker import Tracker
from redmine.user import User
from redmine.version import Version

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.command(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option(
    OPTIONS["force"]["long"],
    help=OPTIONS["force"]["help"],
    show_default=True,
    default=False,
)
@click.option(OPTIONS["account"]["long"])
@click.pass_context
def cli(ctx, **kwargs):
    cfg = Config(kwargs.get("account"))
    redmine = Redmine(
        cfg.url, cfg.api_key, cfg.ssl_verify, invalidate_cache=kwargs.get("force")
    )
    ctx.obj = redmine


@cli.command()
@click.argument("issue_ids", nargs=-1)
@click.option(OPTIONS["assignee"]["long"], OPTIONS["assignee"]["short"], default=None)
@click.option(OPTIONS["status"]["long"], OPTIONS["status"]["short"], default=None)
@click.option(OPTIONS["tracker"]["long"], OPTIONS["tracker"]["short"], default=None)
@click.option(OPTIONS["project"]["long"], OPTIONS["project"]["short"], default=None)
@click.option(OPTIONS["priority"]["long"], OPTIONS["priority"]["short"], default=None)
@click.option(OPTIONS["version"]["long"], OPTIONS["version"]["short"], default=None)
@click.option(OPTIONS["query"]["long"], OPTIONS["query"]["short"], default=None)
@click.option(OPTIONS["start"]["long"], OPTIONS["start"]["short"], default=None)
@click.option(OPTIONS["due"]["long"], OPTIONS["due"]["short"], default=None)
@click.option(OPTIONS["done"]["long"], OPTIONS["done"]["short"], default=None)
@click.option(OPTIONS["parent"]["long"], OPTIONS["parent"]["short"], default=None)
@click.option(OPTIONS["limit"]["long"], OPTIONS["limit"]["short"], default=25)
@click.option(OPTIONS["sort"]["long"], OPTIONS["sort"]["short"], default="id:desc")
@click.option(OPTIONS["updated-on"]["long"], default=None)
@click.option(OPTIONS["updated-after"]["long"], default=None)
@click.option(OPTIONS["updated-before"]["long"], default=None)
@click.option(OPTIONS["created-on"]["long"], default=None)
@click.option(OPTIONS["created-after"]["long"], default=None)
@click.option(OPTIONS["created-before"]["long"], default=None)
@click.option(OPTIONS["json"]["long"], default=False, show_default=True)
@click.pass_obj
@click.pass_context
def issues(ctx, redmine, issue_ids, **kwargs):
    """ List issues """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    if issue_ids:
        kwargs.update({"issue_id": ",".join(issue_ids)})

    try:
        issues = redmine.get_issues(**kwargs)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    if kwargs.get("json"):
        return click.echo(json.dumps(issues))

    for issue in issues:
        click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issue_id")
@click.option(OPTIONS["journals"]["long"], OPTIONS["journals"]["short"], default=True)
@click.pass_obj
def show(redmine, issue_id, journals):
    """ Show issue details """

    try:
        issue = redmine.get_issue(issue_id, journals)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    issue = Issue(
        **issue,
        statuses=redmine.statuses,
        priorities=redmine.priorities,
        projects=redmine.projects,
        users=redmine.users,
    )

    click.echo_via_pager(str(issue))


@cli.command()
@click.option(OPTIONS["subject"]["long"], OPTIONS["subject"]["short"], prompt=True)
@click.option(
    OPTIONS["description"]["long"], OPTIONS["description"]["short"], default=None
)
@click.option(OPTIONS["edit"]["long"], OPTIONS["edit"]["short"], default=False)
@click.option(OPTIONS["project"]["long"], OPTIONS["project"]["short"], prompt=True)
@click.option(OPTIONS["status"]["long"], OPTIONS["status"]["short"], prompt=True)
@click.option(OPTIONS["tracker"]["long"], OPTIONS["tracker"]["short"], prompt=True)
@click.option(OPTIONS["priority"]["long"], OPTIONS["priority"]["short"], prompt=True)
@click.option(OPTIONS["assignee"]["long"], OPTIONS["assignee"]["short"], default=None)
@click.option(OPTIONS["start"]["long"], OPTIONS["start"]["short"], default=None)
@click.option(OPTIONS["due"]["long"], OPTIONS["due"]["short"], default=None)
@click.option(OPTIONS["done"]["long"], OPTIONS["done"]["short"], default=None)
@click.option(OPTIONS["parent"]["long"], OPTIONS["parent"]["short"], default=None)
@click.pass_obj
def create(redmine, *args, **kwargs):
    """ Create new issue """

    if kwargs.get("edit"):
        kwargs["description"] = get_description()

    try:
        issue = redmine.create_issue(**kwargs)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issue_id")
@click.option(OPTIONS["subject"]["long"], OPTIONS["subject"]["short"], default=None)
@click.option(OPTIONS["project"]["long"], OPTIONS["project"]["short"], default=None)
@click.option(OPTIONS["status"]["long"], OPTIONS["status"]["short"], default=None)
@click.option(OPTIONS["tracker"]["long"], OPTIONS["tracker"]["short"], default=None)
@click.option(OPTIONS["priority"]["long"], OPTIONS["priority"]["short"], default=None)
@click.option(
    OPTIONS["description"]["long"], OPTIONS["description"]["short"], default=None
)
@click.option(OPTIONS["note"]["long"], OPTIONS["note"]["short"], default=None)
@click.option(OPTIONS["edit"]["long"], OPTIONS["edit"]["short"], default=False)
@click.option(OPTIONS["assignee"]["long"], OPTIONS["assignee"]["short"], default=None)
@click.option(OPTIONS["start"]["long"], OPTIONS["start"]["short"], default=None)
@click.option(OPTIONS["due"]["long"], OPTIONS["due"]["short"], default=None)
@click.option(OPTIONS["done"]["long"], OPTIONS["done"]["short"], default=None)
@click.option(OPTIONS["parent"]["long"], OPTIONS["parent"]["short"], default=None)
@click.pass_obj
@click.pass_context
def update(ctx, redmine, issue_id, **kwargs):
    """ Update issue """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    if kwargs.get("edit"):
        kwargs["description"] = get_description()
        kwargs["note"] = get_note()

    try:
        updated = redmine.update_issue(issue_id, **kwargs)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

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

    try:
        projects = sorted(redmine.get("projects"), key=lambda x: x["name"])
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for project in projects:
        click.echo(Project(**project))


@list.command()
@click.pass_obj
def tracker(redmine):
    """ List trackers """

    try:
        trackers = sorted(redmine.get("trackers"), key=lambda x: x["id"])
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for tracker in trackers:
        click.echo(Tracker(**tracker))


@list.command()
@click.pass_obj
def status(redmine):
    """ List statuses """

    try:
        statuses = sorted(redmine.get("issue_statuses"), key=lambda x: x["id"])
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for status in statuses:
        click.echo(IssueStatus(**status))


@list.command()
@click.pass_obj
def query(redmine):
    """ List queries """

    try:
        queries = sorted(redmine.get("queries"), key=lambda x: x["id"])
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for query in queries:
        click.echo(Query(**query))


@list.command()
@click.pass_obj
def priority(redmine):
    """ List priorities """

    try:
        priorities = sorted(
            redmine.get("enumerations/issue_priorities"), key=lambda x: x["id"]
        )
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for priority in priorities:
        click.echo(Priority(**priority))


@list.command()
@click.pass_obj
def user(redmine):
    """ List users """

    try:
        users = OrderedDict(sorted(redmine.get_users().items(), key=lambda x: x[1]))
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for user_id, name in users.items():
        click.echo(User(user_id, name))


@list.command()
@pass_config
def alias(config):
    for alias, command in config.aliases.items():
        click.echo(f"{alias}={command}")


@cli.group()
@click.argument("project_id")
@click.pass_context
def project(context, project_id):
    """ Project commands """
    context.obj.project_id = project_id


@project.command()
@click.pass_context
def roadmap(context):
    """ List versions of a project """

    redmine = context.obj
    project_id = context.obj.project_id

    try:
        versions = sorted(
            redmine.get(f"projects/{project_id}/versions"), key=lambda x: x["id"]
        )
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for version in versions:
        click.echo(Version(**version))


@cli.command()
def version():
    """ Print version """

    import platform
    import pkg_resources

    system = platform.system()
    kernel = platform.release()
    python_version = platform.python_version()

    pkg_name = "redminecli"
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
