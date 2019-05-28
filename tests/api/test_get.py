import os
from unittest.mock import MagicMock, patch

from redmine.redmine import Redmine

redmine = Redmine(
    "http://example.com", "API_KEY", invalidate_cache=False, cache_initial=False
)


def test_get_projects_calls_fetch_when_no_cache():
    resource = "projects"

    with patch.object(Redmine, "fetch") as mock_fetch:
        import os

        os.path.exists = MagicMock(return_value=False)
        redmine.get(resource)

    mock_fetch.assert_called_once_with(resource)


def test_get_projects_calls_set_cache_when_no_cache():
    resource = "projects"
    data = {"projects": [{"id": 1, "name": "Project"}]}

    with patch.object(Redmine, "fetch", return_value=data):
        with patch.object(Redmine, "set_cache") as mock_cache:
            os.path.exists = MagicMock(return_value=False)
            redmine.get(resource)

    cache_file = os.path.join(redmine.cache_dir, "{}.json".format(resource))

    mock_cache.assert_called_once_with(cache_file, data)


def test_get_trackers_calls_fetch_when_no_cache():
    resource = "trackers"

    with patch.object(Redmine, "fetch") as mock_fetch:
        import os

        os.path.exists = MagicMock(return_value=False)
        redmine.get(resource)

    mock_fetch.assert_called_once_with(resource)


def test_get_trackers_calls_set_cache_when_no_cache():
    resource = "trackers"
    data = {"trackers": [{"id": 1, "name": "Tracker"}]}

    with patch.object(Redmine, "fetch", return_value=data):
        with patch.object(Redmine, "set_cache") as mock_cache:
            os.path.exists = MagicMock(return_value=False)
            redmine.get(resource)

    cache_file = os.path.join(redmine.cache_dir, "{}.json".format(resource))

    mock_cache.assert_called_once_with(cache_file, data)


def test_get_statuses_calls_fetch_when_no_cache():
    resource = "statuses"

    with patch.object(Redmine, "fetch") as mock_fetch:
        import os

        os.path.exists = MagicMock(return_value=False)
        redmine.get(resource)

    mock_fetch.assert_called_once_with(resource)


def test_get_statuses_calls_set_cache_when_no_cache():
    resource = "statuses"
    data = {"statuses": [{"id": 1, "name": "Status"}]}

    with patch.object(Redmine, "fetch", return_value=data):
        with patch.object(Redmine, "set_cache") as mock_cache:
            os.path.exists = MagicMock(return_value=False)
            redmine.get(resource)

    cache_file = os.path.join(redmine.cache_dir, "{}.json".format(resource))

    mock_cache.assert_called_once_with(cache_file, data)


def test_get_priorities_calls_fetch_when_no_cache():
    resource = "enumerations/priorities"

    with patch.object(Redmine, "fetch") as mock_fetch:
        import os

        os.path.exists = MagicMock(return_value=False)
        redmine.get(resource)

    mock_fetch.assert_called_once_with(resource)


def test_get_priorities_calls_set_cache_when_no_cache():
    resource = "priorities"
    data = {"priorities": [{"id": 1, "name": "Priority"}]}

    with patch.object(Redmine, "fetch", return_value=data):
        with patch.object(Redmine, "set_cache") as mock_cache:
            os.path.exists = MagicMock(return_value=False)
            redmine.get(resource)

    cache_file = os.path.join(redmine.cache_dir, "{}.json".format(resource))

    mock_cache.assert_called_once_with(cache_file, data)


def test_get_queries_calls_fetch_when_no_cache():
    resource = "queries"

    with patch.object(Redmine, "fetch") as mock_fetch:
        import os

        os.path.exists = MagicMock(return_value=False)
        redmine.get(resource)

    mock_fetch.assert_called_once_with(resource)


def test_get_queries_calls_set_cache_when_no_cache():
    resource = "queries"
    data = {"queries": [{"id": 1, "name": "Query"}]}

    with patch.object(Redmine, "fetch", return_value=data):
        with patch.object(Redmine, "set_cache") as mock_cache:
            os.path.exists = MagicMock(return_value=False)
            redmine.get(resource)

    cache_file = os.path.join(redmine.cache_dir, "{}.json".format(resource))

    mock_cache.assert_called_once_with(cache_file, data)
