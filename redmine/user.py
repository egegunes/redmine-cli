class User:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

    def __str__(self):
        return f"{self.id:>3} {self.name}"
