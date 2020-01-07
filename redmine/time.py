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
        time = f"{self.project['name']:<21.20} "
        time += f"{self.issue['id']:>6} "
        time += f"{self.user['name']:<21.20} "
        time += f"{self.activity['name']:<15.14} "
        time += f"{self.spent_on:<11} "
        time += f"{self.hours:>6} hours"

        return time
