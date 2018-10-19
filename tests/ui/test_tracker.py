from redmine.tracker import Tracker


def test_tracker_str():
    tracker = Tracker(id=1, name="Bug")

    assert str(tracker) == "1   Bug"
