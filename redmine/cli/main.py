import datetime
import json
import sys
from collections import OrderedDict

import click
from requests.exceptions import HTTPError

from redmine.activity import Activity
from redmine.custom_field import CustomField
from redmine.cli.alias import AliasedGroup
from redmine.cli.config import Config, pass_config
from redmine.cli.helpers import get_description, get_note
from redmine.cli.options import OPTIONS
from redmine.issue import Issue, IssueStatus
from redmine.priority import Priority
from redmine.project import Project
from redmine.query import Query
from redmine.redmine import Redmine
from redmine.time import Time
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
@click.option(OPTIONS["account"]["long"], help=OPTIONS["account"]["help"])
@click.option(OPTIONS["verbose"]["long"], help=OPTIONS["verbose"]["help"])
@click.pass_context
def cli(ctx, **kwargs):
    try:
        cfg = Config(kwargs.get("account"))
    except FileNotFoundError as e:
        click.echo(click.style(f"Fatal: {e}", fg="red"))
        sys.exit(1)

    redmine = Redmine(
        cfg.url,
        cfg.api_key,
        cfg.ssl_verify,
        invalidate_cache=kwargs.get("force"),
        verbose=kwargs.get("verbose"),
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
@click.option(OPTIONS["subject"]["long"], OPTIONS["subject"]["short"], default=None)
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
@click.option(OPTIONS["pager"]["long"], default=True)
@click.pass_obj
def show(redmine, issue_id, journals, pager):
    """ Show issue details """

    try:
        issue = redmine.get_issue(issue_id, journals)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    try:
        issue = Issue(
            **issue,
            statuses=redmine.statuses,
            priorities=redmine.priorities,
            projects=redmine.projects,
            users=redmine.users,
        )
        if pager:
            click.echo_via_pager(str(issue))
        else:
            click.echo(str(issue))
    except KeyError:
        return click.echo(
            click.style(f"Cache is obsolete. Run with --force.", fg="red")
        )


@cli.command()
@click.option(
    OPTIONS["subject"]["long"], OPTIONS["subject"]["short"], default=None, required=True
)
@click.option(
    OPTIONS["description"]["long"], OPTIONS["description"]["short"], default=None
)
@click.option(OPTIONS["edit"]["long"], OPTIONS["edit"]["short"], default=False)
@click.option(
    OPTIONS["project"]["long"], OPTIONS["project"]["short"], default=None, required=True
)
@click.option(
    OPTIONS["status"]["long"], OPTIONS["status"]["short"], default=None, required=True
)
@click.option(
    OPTIONS["tracker"]["long"], OPTIONS["tracker"]["short"], default=None, required=True
)
@click.option(
    OPTIONS["priority"]["long"],
    OPTIONS["priority"]["short"],
    default=None,
    required=True,
)
@click.option(OPTIONS["assignee"]["long"], OPTIONS["assignee"]["short"], default=None)
@click.option(OPTIONS["start"]["long"], OPTIONS["start"]["short"], default=None)
@click.option(OPTIONS["due"]["long"], OPTIONS["due"]["short"], default=None)
@click.option(OPTIONS["done"]["long"], OPTIONS["done"]["short"], default=None)
@click.option(OPTIONS["parent"]["long"], OPTIONS["parent"]["short"], default=None)
@click.option(OPTIONS["custom_field"]["long"], default=None, multiple=True, type=(str, str))
@click.pass_obj
@click.pass_context
def create(ctx, redmine, *args, **kwargs):
    """ Create new issue """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    if kwargs.get("edit"):
        kwargs["description"] = get_description()

    if kwargs.get("start") in ["now", "today"]:
        kwargs["start"] = datetime.date.today().isoformat()

    if kwargs.get("due") in ["now", "today"]:
        kwargs["due"] = datetime.date.today().isoformat()

    if kwargs.get("cf") is None:
        kwargs["cf"] = []

    try:
        issue = redmine.create_issue(**kwargs)
    except HTTPError as e:
        click.echo(click.style(f"Fatal: {e}", fg="red"))
        content = json.loads(e.response.content)
        if "errors" in content:
            for i, error in enumerate(content["errors"]):
                click.echo(click.style(f"ERROR {i}: {error}", fg="red"))
        sys.exit(1)

    click.echo(Issue(**issue).as_row())


@cli.command()
@click.argument("issues", nargs=-1)
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
def update(ctx, redmine, issues, **kwargs):
    """ Update issue """

    if ctx.parent.alias:
        kwargs.update(ctx.parent.params)

    if kwargs.get("edit"):
        kwargs["note"] = get_note()

    if kwargs.get("start") in ["now", "today"]:
        kwargs["start"] = datetime.date.today().isoformat()

    if kwargs.get("due") in ["now", "today"]:
        kwargs["due"] = datetime.date.today().isoformat()

    try:
        for issue_id in issues:
            updated = redmine.update_issue(issue_id, **kwargs)

            if updated:
                msg = f"Issue {issue_id} updated."
                click.echo(click.style(msg, fg="green"), err=True)
    except HTTPError as e:
        click.echo(click.style(f"Fatal: {e}", fg="red"))
        content = json.loads(e.response.content)
        if "errors" in content:
            for i, error in enumerate(content["errors"]):
                click.echo(click.style(f"ERROR {i}: {error}", fg="red"))
        sys.exit(1)


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
def activity(redmine):
    """ List time tracking activities """

    try:
        activities = sorted(
            redmine.get("enumerations/time_entry_activities"), key=lambda x: x["id"]
        )
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for activity in activities:
        click.echo(Activity(**activity))


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
@click.pass_obj
def custom_fields(redmine):
    try:
        custom_fields = redmine.get("custom_fields")
    except HTTPError as e:
        click.echo(click.style(f"Fatal: {e}", fg="red"))
        sys.exit(1)

    for field in custom_fields:
        click.echo(CustomField(**field))


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


@cli.command()
@click.option(OPTIONS["user"]["long"], OPTIONS["user"]["short"], default=None)
@click.option(OPTIONS["project"]["long"], OPTIONS["project"]["short"], default=None)
@click.option(OPTIONS["from"]["long"], default=None)
@click.option(OPTIONS["to"]["long"], default=None)
@click.option(OPTIONS["on"]["long"], default=None)
@click.pass_obj
def times(redmine, **kwargs):
    """ List spent times """

    on = kwargs.get("on")
    if on is not None:
        kwargs.update({"from": on, "to": on})

    try:
        entries = redmine.get(
            "time_entries",
            cache=False,
            **{
                "user_id": kwargs.get("user"),
                "project_id": kwargs.get("project"),
                "from": kwargs.get("from"),
                "to": kwargs.get("to"),
            },
        )
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    for entry in entries:
        click.echo(Time(**entry))


@cli.command()
@click.argument("issue_id")
@click.argument("hours")
@click.option(OPTIONS["on"]["long"], default=None)
@click.option(OPTIONS["activity"]["long"], OPTIONS["activity"]["short"], default=None)
@click.option(OPTIONS["comment"]["long"], OPTIONS["comment"]["short"], default=None)
@click.pass_obj
def spent(redmine, issue_id, hours, **kwargs):
    """ Create new time entry """

    try:
        redmine.create_time_entry(issue_id, hours, **kwargs)
    except HTTPError as e:
        return click.echo(click.style(f"Fatal: {e}", fg="red"))

    click.echo(click.style("Time logged", fg="green"), err=True)
