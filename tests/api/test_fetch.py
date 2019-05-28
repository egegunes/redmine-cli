from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError

from redmine.redmine import Redmine

from .response import MockResponse

redmine = Redmine(
    "http://example.com", "API_KEY", invalidate_cache=False, cache_initial=False
)


@patch("redmine.redmine.requests.get")
def test_fetch(mock_get):
    expected = {
        "projects": [
            {
                "id": 1,
                "name": "Test project",
                "identifier": "test",
                "description": "Description",
                "status": 1,
                "created_on": "2018-07-09T13:52:12Z",
                "updated_on": "2018-07-09T13:52:12Z",
            },
            {
                "id": 2,
                "name": "Test project 2",
                "identifier": "test-2",
                "description": "Description",
                "status": 1,
                "created_on": "2018-07-09T13:52:12Z",
                "updated_on": "2018-07-09T13:52:12Z",
            },
        ],
        "total_count": 2,
        "offset": 0,
        "limit": 25,
    }
    mock_get.return_value = MockResponse(200, expected)

    response = redmine.fetch("projects")

    assert response == expected


@patch("redmine.redmine.requests.get")
def test_fetch_with_empty_response(mock_get):
    expected = {}
    mock_get.return_value = MockResponse(200, expected)

    response = redmine.fetch("projects")

    assert response == expected


@patch("redmine.redmine.requests.get")
def test_fetch_with_server_error(mock_get):
    mock_get.return_value = MockResponse(500, {})

    with pytest.raises(HTTPError):
        redmine.fetch("projects")


@patch("redmine.redmine.requests.get")
def test_fetch_with_bad_request(mock_get):
    mock_get.return_value = MockResponse(400, {})

    with pytest.raises(HTTPError):
        redmine.fetch("projects")


@patch("redmine.redmine.requests.get")
def test_fetch_with_not_found(mock_get):
    mock_get.return_value = MockResponse(404, {})

    with pytest.raises(HTTPError):
        redmine.fetch("projects")
