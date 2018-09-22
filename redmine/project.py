class Project:
    def __init__(self, *args, **kwargs):
        self.id = kwargs.get("id")
        self.identifier = kwargs.get("identifier")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")

    def __str__(self):
        return f"{self.id:<3} {self.name}"
