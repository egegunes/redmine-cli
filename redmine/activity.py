class Activity:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")

    def __str__(self):
        return f"{self.id:<4} {self.name:<20}"
