import unittest
from unittest import mock

import requests

from helping_files import http_utils


def response(status):
    result = requests.Response()
    result.status_code = status
    return result


class FetchTests(unittest.TestCase):
    def fetch(self, side_effect, **kwargs):
        sleeps = []
        with mock.patch("requests.get", side_effect=side_effect) as get:
            try:
                result = http_utils.fetch("https://example.test", sleep=sleeps.append, **kwargs)
            except Exception as error:
                result = error
        return result, get.call_count, sleeps

    def test_retries_server_errors_then_succeeds(self):
        result, calls, sleeps = self.fetch([response(503), response(500), response(200)])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(calls, 3)
        self.assertEqual(sleeps, [5, 10])

    def test_retries_timeouts_and_connection_errors(self):
        result, calls, _ = self.fetch([requests.Timeout(), requests.ConnectionError(), response(200)])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(calls, 3)

    def test_raises_after_exhausting_retries(self):
        result, calls, _ = self.fetch([response(503)] * 4)
        self.assertIsInstance(result, requests.HTTPError)
        self.assertEqual(calls, 4)

    def test_raises_last_network_error(self):
        result, calls, _ = self.fetch([requests.Timeout()] * 4)
        self.assertIsInstance(result, requests.Timeout)
        self.assertEqual(calls, 4)

    def test_non_retryable_error_raises_immediately(self):
        result, calls, sleeps = self.fetch([response(403), response(200)])
        self.assertIsInstance(result, requests.HTTPError)
        self.assertEqual(calls, 1)
        self.assertEqual(sleeps, [])

    def test_not_found_raises_by_default(self):
        result, calls, _ = self.fetch([response(404)])
        self.assertIsInstance(result, requests.HTTPError)
        self.assertEqual(calls, 1)

    def test_not_found_returns_none_when_allowed(self):
        result, calls, _ = self.fetch([response(404)], allow_not_found=True)
        self.assertIsNone(result)
        self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
