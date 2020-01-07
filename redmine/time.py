class Time:
    def __init__(self, *args, **kwargs):
        self.project = kwargs.get("project")
        self.issue = kwargs.get("issue")
        self.user = kwargs.get("user")
        self.hours = kwargs.get("hours")
        self.activity = kwargs.get("activity")
        self.comments = kwargs.get("comments")
        self.spent_on = kwargs.get("spent_on")

    def __str__(self):
        return f"{self.project['name']:<21.20} {self.issue['id']:>6} {self.user['name']:<21.20} {self.activity['name']:<15.14} {self.spent_on:<11} {self.hours:>6} hours"
