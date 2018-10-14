import json
import os
from urllib.parse import urljoin

import click
import requests


class Redmine:
    def __init__(self, url, api_key, me):
        self.url = url
        self.auth_header = {"X-Redmine-API-Key": api_key}
        self.me = me

        self.cache_dir = os.path.join(os.getenv("HOME"), ".cache/redmine")
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.statuses = self.get("issue_statuses")
        self.priorities = self.get("enumerations/issue_priorities")
        self.projects = self.get("projects")
        self.users = self.get_users()

    def __repr__(self):
        return f"Redmine({self.url})"

    def __str__(self):
        return repr(self)

    def fetch(self, resource):
        resp = requests.get(
            urljoin(self.url, "{}.json".format(resource)),
            headers=self.auth_header
        )

        resp.raise_for_status()

        return resp.json()

    def get(self, resource):
        # Some resources (i.e issue_priorities) have paths that contain "/"
        rname = resource.split("/")[-1]
        cache_file = os.path.join(self.cache_dir, "{}.json".format(rname))
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                data = json.loads(cf.read())
        else:
            data = self.fetch(resource)
            if resource in data:
                with open(cache_file, "w+") as cf:
                    cf.write(json.dumps(data))

        return data[rname]

    def get_users(self):
        cache_file = os.path.join(self.cache_dir, "users.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                users = json.loads(cf.read())
        else:
            memberships = []

            click.echo("Caching users... This may take a while.", err=True)
            with click.progressbar(self.projects) as projects:
                for project in projects:
                    resource = "projects/{}/memberships".format(project["id"])
                    response = self.fetch(resource)
                    if "memberships" in response:
                        memberships.extend(response["memberships"])

            users = {}

            for m in memberships:
                try:
                    users[str(m["user"]["id"])] = m["user"]["name"]
                except KeyError:
                    users[str(m["group"]["id"])] = m["group"]["name"]

            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(users))

        return users

    def get_issues(self, **kwargs):
        updated_on = None
        if kwargs.get("updated_on"):
            updated_on = kwargs.get("updated_on")
        elif kwargs.get("updated_before"):
            updated_on = "<=" + kwargs.get("updated_before")
        elif kwargs.get("updated_after"):
            updated_on = ">=" + kwargs.get("updated_after")

        created_on = None
        if kwargs.get("created_on"):
            created_on = kwargs.get("created_on")
        elif kwargs.get("created_before"):
            created_on = "<=" + kwargs.get("created_before")
        elif kwargs.get("created_after"):
            created_on = ">=" + kwargs.get("created_after")

        query_params = {
            "assigned_to_id": kwargs.get("assignee"),
            "status_id": kwargs.get("status"),
            "tracker_id": kwargs.get("tracker"),
            "project_id": kwargs.get("project"),
            "priority_id": kwargs.get("priority"),
            "query_id": kwargs.get("query"),
            "parent_id": kwargs.get("parent"),
            "start_date": kwargs.get("start"),
            "due_date": kwargs.get("due"),
            "done_ratio": kwargs.get("done"),
            "updated_on": updated_on,
            "created_on": created_on,
            "limit": kwargs.get("limit"),
            "sort": kwargs.get("sort")
        }
        resp = requests.get(
            f"{self.url}/issues.json",
            params=query_params,
            headers=self.auth_header
        )

        return resp.json()["issues"]

    def get_issue(self, issue_id, journals):
        query_params = {}
        if journals:
            query_params["include"] = "journals"
        r = requests.get(
            f"{self.url}/issues/{issue_id}.json",
            params=query_params,
            headers=self.auth_header
        )

        issue = r.json()["issue"]

        return issue

    def update_issue(self, issue_id, **kwargs):
        fields = {
            "issue": {
                "subject": kwargs.get("subject"),
                "project_id": kwargs.get("project"),
                "tracker_id": kwargs.get("tracker"),
                "status_id": kwargs.get("status"),
                "description": kwargs.get("description"),
                "priority_id": kwargs.get("priority"),
                "assigned_to_id": kwargs.get("assignee"),
                "parent_issue_id": kwargs.get("parent_issue"),
                "start_date": kwargs.get("start"),
                "due_date": kwargs.get("due"),
                "done_ratio": kwargs.get("done"),
                "notes": kwargs.get("notes"),
            }
        }

        for field in list(fields["issue"].keys()):
            if not fields["issue"][field]:
                del fields["issue"][field]

        resp = requests.put(
            f"{self.url}/issues/{issue_id}.json",
            json=fields,
            headers=self.auth_header
        )

        resp.raise_for_status()

        return True

    def create_issue(self, **kwargs):
        fields = {
            "issue": {
                "subject": kwargs.get("subject"),
                "project_id": kwargs.get("project"),
                "tracker_id": kwargs.get("tracker"),
                "status_id": kwargs.get("status"),
                "description": kwargs.get("description"),
                "priority_id": kwargs.get("priority"),
                "assigned_to_id": kwargs.get("assignee"),
                "parent_issue_id": kwargs.get("parent_issue"),
                "start_date": kwargs.get("start"),
                "due_date": kwargs.get("due"),
                "done_ratio": kwargs.get("done"),
            }
        }
        resp = requests.post(
            f"{self.url}/issues.json",
            json=fields,
            headers=self.auth_header
        )

        resp.raise_for_status()

        return resp.json()["issue"]
