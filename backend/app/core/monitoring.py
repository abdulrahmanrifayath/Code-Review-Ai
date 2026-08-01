import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# Simple Prometheus-formatted metrics text generator
class PrometheusMetrics:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_duration_seconds = 0.0

    def generate_metrics_text(self) -> str:
        avg_latency = (self.total_duration_seconds / self.request_count) if self.request_count > 0 else 0.0
        return (
            "# HELP http_requests_total Total number of HTTP requests processed\n"
            "# TYPE http_requests_total counter\n"
            f"http_requests_total {self.request_count}\n\n"
            "# HELP http_errors_total Total number of HTTP 5xx errors\n"
            "# TYPE http_errors_total counter\n"
            f"http_errors_total {self.error_count}\n\n"
            "# HELP http_request_duration_seconds_avg Average request latency in seconds\n"
            "# TYPE http_request_duration_seconds_avg gauge\n"
            f"http_request_duration_seconds_avg {avg_latency:.4f}\n"
        )


metrics_collector = PrometheusMetrics()


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            metrics_collector.request_count += 1
            metrics_collector.total_duration_seconds += duration
            if response.status_code >= 500:
                metrics_collector.error_count += 1
            return response
        except Exception:
            metrics_collector.request_count += 1
            metrics_collector.error_count += 1
            raise
