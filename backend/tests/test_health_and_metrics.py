import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.monitoring import PrometheusMetrics


class TestHealthAndMetrics(unittest.TestCase):
    def test_prometheus_metrics_generation(self):
        metrics = PrometheusMetrics()
        metrics.request_count = 10
        metrics.error_count = 1
        metrics.total_duration_seconds = 2.5

        output = metrics.generate_metrics_text()
        self.assertIn("http_requests_total 10", output)
        self.assertIn("http_errors_total 1", output)
        self.assertIn("http_request_duration_seconds_avg 0.2500", output)


if __name__ == "__main__":
    unittest.main()
