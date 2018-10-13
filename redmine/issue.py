from textwrap import wrap

from redmine.journal import Journal
from collections import defaultdict


class Issue:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.subject = kwargs.get("subject")
        self.tracker = kwargs.get("tracker")
        self.project = kwargs.get("project")
        self.status = kwargs.get("status")
        self.priority = kwargs.get("priority")
        self.author = kwargs.get("author")
        self.assigned_to = kwargs.get("assigned_to", defaultdict(str))
        self.done = kwargs.get("done")
        self.start_date = kwargs.get("start_date")
        self.due_date = kwargs.get("due_date")
        self.description = kwargs.get("description")
        self.journals = kwargs.get("journals")
        self.done_ratio = kwargs.get("done_ratio")
        self.statuses = kwargs.get("statuses")
        self.priorities = kwargs.get("priorities")
        self.users = kwargs.get("users")

    def __repr__(self):
        return f"Issue({self.id}, {self.subject})"

    def __str__(self):
        issue = self.get_header()

        if self.journals:
            issue += self.get_journals()

        return issue

    def get_header(self):
        header = f"Issue #{self.id} {self.subject}\n"
        header += f"Project: {self.project['name']}\n"
        header += f"Tracker: {self.tracker['name']}\n"
        header += f"Status: {self.status['name']}\n"
        header += f"Priority: {self.priority['name']}\n"
        header += f"Author: {self.author['name']}\n"
        header += f"Assigned to: {self.assigned_to['name']}\n"
        header += f"Start date: {self.start_date}\n"
        header += f"Due date: {self.due_date}\n"
        header += f"Done: {self.done}\n\n"

        description = wrap(self.description, width=79)
        for d in description:
            header += f"{d}\n"

        return header

    def get_journals(self):
        journals = ""
        for journal in self.journals:
            journals += str(
                Journal(**journal,
                        statuses=self.statuses,
                        priorities=self.priorities,
                        users=self.users)
            )

        return journals

    def as_row(self):
        return f"{self.id:>6} " \
               f"{self.project['name']:22.20} " \
               f"{self.priority['name']:<8} " \
               f"{self.status['name']:<16} " \
               f"{self.done_ratio:>2}% " \
               f"{self.subject:<30}"


class IssueStatus:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")

    def __str__(self):
        return f"{self.id:<3} {self.name}"
