import json
import os
from urllib.parse import urljoin

import click
import requests


class Redmine:
    def __init__(
        self,
        url,
        api_key,
        ssl_verify=True,
        invalidate_cache=False,
        cache_initial=True,
        verbose=False,
    ):
        self.url = url
        self.auth_header = {"X-Redmine-API-Key": api_key}
        self.ssl_verify = ssl_verify
        self.verbose = verbose

        self.cache_dir = os.path.join(os.getenv("HOME"), ".cache/redmine")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        if invalidate_cache:
            for f in os.listdir(self.cache_dir):
                f_path = os.path.join(self.cache_dir, f)
                if os.path.isfile(f_path):
                    os.unlink(f_path)

        if cache_initial:
            self.statuses = self.get("issue_statuses")
            self.priorities = self.get("enumerations/issue_priorities")
            self.projects = self.get("projects")
            self.users = self.get_users()

    def __repr__(self):
        return f"Redmine({self.url})"

    def __str__(self):
        return repr(self)

    def fetch(self, resource, **kwargs):
        resp = requests.get(
            urljoin(self.url, "{}.json".format(resource)),
            params={"limit": 100, **kwargs},
            headers=self.auth_header,
            verify=self.ssl_verify,
        )

        resp.raise_for_status()

        return resp.json()

    def set_cache(self, cache_file, data):
        with open(cache_file, "w+") as cf:
            cf.write(json.dumps(data))

    def get(self, resource, cache=True, **kwargs):
        # Some resources (i.e issue_priorities) have paths that contain "/"
        rname = resource.split("/")[-1]
        cache_file = os.path.join(self.cache_dir, "{}.json".format(rname))
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                data = json.loads(cf.read())
        else:
            data = self.fetch(resource, **kwargs)
            if resource in data and cache:
                self.set_cache(cache_file, data)

        return data[rname]

    def get_users(self):
        cache_file = os.path.join(self.cache_dir, "users.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                users = json.loads(cf.read())
        else:
            memberships = []

            with click.progressbar(self.projects, label="Caching users") as projects:
                for project in projects:
                    resource = "projects/{}/memberships".format(project["id"])
                    response = self.fetch(resource)
                    if "memberships" in response:
                        memberships.extend(response["memberships"])

            users = {}
            membership_types = ["user", "group", "group_anonymous"]

            for m in memberships:
                for t in membership_types:
                    try:
                        users[str(m[t]["id"])] = m[t]["name"]
                    except KeyError:
                        continue
                    else:
                        break

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
            "fixed_version_id": kwargs.get("version"),
            "query_id": kwargs.get("query"),
            "parent_id": kwargs.get("parent"),
            "start_date": kwargs.get("start"),
            "due_date": kwargs.get("due"),
            "done_ratio": kwargs.get("done"),
            "updated_on": updated_on,
            "created_on": created_on,
            "limit": kwargs.get("limit"),
            "sort": kwargs.get("sort"),
        }

        if kwargs.get("issue_id"):
            query_params = {"issue_id": kwargs.get("issue_id")}

        resp = requests.get(
            f"{self.url}/issues.json",
            params=query_params,
            headers=self.auth_header,
            verify=self.ssl_verify,
        )

        resp.raise_for_status()

        return resp.json()["issues"]

    def search(self, **kwargs):
        query_params = {
            "q": kwargs.get("query"),
            "titles_only": kwargs.get("titles_only"),
        }

        resp = requests.get(
            f"{self.url}/search.json",
            params=query_params,
            headers=self.auth_header,
            verify=self.ssl_verify,
        )

        resp.raise_for_status()
        return resp.json()["results"]

    def get_issue(self, issue_id, journals):
        query_params = {}
        if journals:
            query_params["include"] = "journals"
        resp = requests.get(
            f"{self.url}/issues/{issue_id}.json",
            params=query_params,
            headers=self.auth_header,
            verify=self.ssl_verify,
        )

        resp.raise_for_status()

        return resp.json()["issue"]

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
                "notes": kwargs.get("note"),
            }
        }

        for field in list(fields["issue"].keys()):
            if fields["issue"][field] == None:
                del fields["issue"][field]

        resp = requests.put(
            f"{self.url}/issues/{issue_id}.json",
            json=fields,
            headers=self.auth_header,
            verify=self.ssl_verify,
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
                "parent_issue_id": kwargs.get("parent"),
                "start_date": kwargs.get("start"),
                "due_date": kwargs.get("due"),
                "done_ratio": kwargs.get("done"),
                "custom_fields": [{"id": cf[0], "value": cf[1]} for cf in kwargs.get("cf")]
            }
        }
        resp = requests.post(
            f"{self.url}/issues.json",
            json=fields,
            headers=self.auth_header,
            verify=self.ssl_verify,
        )
        if self.verbose:
            print(f"{resp.request.method} {resp.request.path_url}")
            for key, value in resp.request.headers.items():
                print(f"{key}: {value}")
            print(f"{resp.request.body}")

        resp.raise_for_status()

        return resp.json()["issue"]

    def create_time_entry(self, issue_id, hours, **kwargs):
        fields = {
            "time_entry": {
                "issue_id": issue_id,
                "hours": hours,
                "comments": kwargs.get("comment"),
            }
        }

        if kwargs.get("activity"):
            fields["time_entry"].update({"activity_id": kwargs.get("activity")})

        if kwargs.get("on"):
            fields["time_entry"].update({"spent_on": kwargs.get("on")})

        resp = requests.post(
            f"{self.url}/time_entries.json",
            json=fields,
            headers=self.auth_header,
            verify=self.ssl_verify,
        )

        resp.raise_for_status()

        return resp.json()
