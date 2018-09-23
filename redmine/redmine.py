import json
import os
from urllib.parse import urljoin

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
        filename = resource.split("/")[-1]
        cache_file = os.path.join(self.cache_dir, "{}.json".format(filename))
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                data = json.loads(cf.read())
        else:
            data = self.fetch(resource)
            if resource in data:
                data = data[resource]

                with open(cache_file, "w+") as cf:
                    cf.write(json.dumps(data))

        return data

    def get_users(self):
        cache_file = os.path.join(self.cache_dir, "users.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                users = json.loads(cf.read())
        else:
            memberships = []

            print("Caching users... This may take a while.")
            for project in self.projects:
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
        query_params = {
            "assigned_to_id": kwargs.get("assignee"),
            "status_id": kwargs.get("status"),
            "tracker_id": kwargs.get("tracker"),
            "project_id": kwargs.get("project"),
            "query_id": kwargs.get("query"),
            "limit": kwargs.get("limit"),
            "sort": kwargs.get("sort")
        }
        r = requests.get(
            f"{self.url}/issues.json",
            params=query_params,
            headers=self.auth_header
        )
        issues = r.json()["issues"]

        return issues

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

    def update_issue(self, issue_id):
        print("update command not implemented yet")

    def create_issue(self):
        print("create command not implemented yet")
