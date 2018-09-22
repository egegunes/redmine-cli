import json
import os

import requests


class Redmine:
    def __init__(self, url, api_key, me):
        self.url = url
        self.auth_header = {"X-Redmine-API-Key": api_key}
        self.me = me

        self.cache_dir = os.path.join(os.getenv("HOME"), ".cache/redmine")
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.statuses = self.get_statuses()
        self.priorities = self.get_priorities()
        self.projects = self.get_projects()
        self.users = self.get_users()

    def __repr__(self):
        return f"Redmine({self.url})"

    def __str__(self):
        return repr(self)

    def fetch_projects(self):
        r = requests.get(
            f"{self.url}/projects.json",
            headers=self.auth_header
        )

        return r.json()["projects"]

    def get_projects(self):
        cache_file = os.path.join(self.cache_dir, "project.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                projects = json.loads(cf.read())
        else:
            projects = self.fetch_projects()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(projects))

        return projects

    def fetch_trackers(self):
        r = requests.get(
            f"{self.url}/trackers.json",
            headers=self.auth_header
        )

        return r.json()["trackers"]

    def get_trackers(self):
        cache_file = os.path.join(self.cache_dir, "tracker.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                trackers = json.loads(cf.read())
        else:
            trackers = self.fetch_trackers()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(trackers))

        return trackers

    def fetch_statuses(self):
        r = requests.get(
            f"{self.url}/issue_statuses.json",
            headers=self.auth_header
        )

        return r.json()["issue_statuses"]

    def get_statuses(self):
        cache_file = os.path.join(self.cache_dir, "status.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                statuses = json.loads(cf.read())
        else:
            statuses = self.fetch_statuses()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(statuses))

        return statuses

    def fetch_queries(self):
        r = requests.get(
            f"{self.url}/queries.json",
            headers=self.auth_header
        )

        return r.json()["queries"]

    def get_queries(self):
        cache_file = os.path.join(self.cache_dir, "query.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                queries = json.loads(cf.read())
        else:
            queries = self.fetch_queries()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(queries))

        return queries

    def fetch_priorities(self):
        r = requests.get(
            f"{self.url}/enumerations/issue_priorities.json",
            headers=self.auth_header
        )

        return r.json()["issue_priorities"]

    def get_priorities(self):
        cache_file = os.path.join(self.cache_dir, "priority.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                priorities = json.loads(cf.read())
        else:
            priorities = self.fetch_priorities()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(priorities))

        return priorities

    def fetch_users(self, project_id):
        r = requests.get(
            f"{self.url}/projects/{project_id}/memberships.json",
            headers=self.auth_header
        )

        return r.json()["memberships"]

    def get_users(self):
        cache_file = os.path.join(self.cache_dir, "users.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as cf:
                users = json.loads(cf.read())
        else:
            memberships = []

            print("Caching users... This may take a while.")
            for project in self.projects:
                memberships.extend(self.fetch_users(project["id"]))

            users = {}

            for m in memberships:
                try:
                    users[m["user"]["id"]] = m["user"]["name"]
                except KeyError:
                    users[m["group"]["id"]] = m["group"]["name"]

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
