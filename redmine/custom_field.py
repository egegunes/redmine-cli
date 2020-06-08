class CustomField:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.is_required = kwargs.get("is_required")
        self.multiple = kwargs.get("multiple")
        self.default = kwargs.get("default_value")
        self.possible_values = [p.get("value") for p in kwargs.get("possible_values")]

    def __str__(self):
        row = f"{self.id:<4} {self.name:<20} required={self.is_required} multiple={self.multiple} default={self.default if self.default != '' else 'None'}\n"
        row += f"possible_values={','.join(self.possible_values)}\n"
        return row
