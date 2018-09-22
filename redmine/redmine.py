import requests


class Redmine:
    def __init__(self, url, api_key, me):
        self.url = url
        self.auth_header = {"X-Redmine-API-Key": api_key}
        self.me = me

    def __repr__(self):
        return f"Redmine({self.url})"

    def __str__(self):
        return repr(self)

    def get_projects(self):
        r = requests.get(
            f"{self.url}/projects.json",
            headers=self.auth_header
        )

        return r.json()["projects"]

    def get_trackers(self):
        r = requests.get(
            f"{self.url}/trackers.json",
            headers=self.auth_header
        )

        return r.json()["trackers"]

    def get_issues(self, **kwargs):
        query_params = {
            "assigned_to_id": kwargs.get("assignee"),
            "status_id": kwargs.get("status"),
            "tracker_id": kwargs.get("tracker"),
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
