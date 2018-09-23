from requests.exceptions import HTTPError


class MockResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise HTTPError(response=self)
