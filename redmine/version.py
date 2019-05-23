class Version:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.status = kwargs.get("status")
        self.name = kwargs.get("name")
        self.due_date = kwargs.get("due_date")

    def __str__(self):
        return f"{self.id:<4} {self.status:<7} {self.name:<20} {self.due_date}"
