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
            print("Serving projects from cache...")
            with open(cache_file, "r") as cf:
                projects = json.loads(cf.read())
        else:
            print("Fetching projects...")
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
            print("Serving trackers from cache...")
            with open(cache_file, "r") as cf:
                trackers = json.loads(cf.read())
        else:
            print("Fetching trackers...")
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
            print("Serving statuses from cache...")
            with open(cache_file, "r") as cf:
                statuses = json.loads(cf.read())
        else:
            print("Fetching statuses...")
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
            print("Serving queries from cache...")
            with open(cache_file, "r") as cf:
                queries = json.loads(cf.read())
        else:
            print("Fetching queries...")
            queries = self.fetch_queries()
            with open(cache_file, "w+") as cf:
                cf.write(json.dumps(queries))

        return queries

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
