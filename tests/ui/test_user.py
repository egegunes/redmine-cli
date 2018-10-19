from redmine.user import User


def test_user_str():
    user = User(1, "Ege Gunes")

    assert str(user) == "  1 Ege Gunes"
