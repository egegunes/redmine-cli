from collections import defaultdict
from datetime import datetime
from textwrap import wrap

from redmine.journal import Journal


class Search:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")

    def as_row(self, show_assignee=True, show_project=True):
        row = f"{self.id:>6} "
        row += f"{self.type:21.20} "

        return row


class IssueStatus:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")

    def __str__(self):
        return f"{self.id:<3} {self.name}"
