from redmine.priority import Priority


def test_priority_str():
    priority = Priority(id=1, name="Normal")

    assert str(priority) == "1   Normal"
