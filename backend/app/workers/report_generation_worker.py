import logging
from typing import Any

from app.core.queue.schemas import QueueType
from app.services.reports.report_generator import ProfessionalReportGeneratorEngine
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.report_generation")


class ReportGenerationWorker(BaseWorker):
    """
    Background worker for asynchronous Report Generation.
    Generates Markdown, HTML, PDF, or JSON executive code review reports.
    """

    def __init__(self, worker_id: str | None = None, queue_mgr: Any | None = None):
        super().__init__(queue_type=QueueType.REPORT_GENERATION, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        repo_full_name = payload.get("repo_full_name", "repository")
        pr_number = payload.get("pr_number", 1)
        output_format = payload.get("format", "MARKDOWN").upper()

        logger.info(
            "Generating %s Report for PR #%s in '%s' (action: %s)",
            output_format, pr_number, repo_full_name, action
        )

        content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
            repo_full_name,
            pr_number,
            output_format,
        )

        return {
            "title": title,
            "format": output_format,
            "metadata": metadata,
            "content_snippet": content[:300] if isinstance(content, str) else "[Binary Data]",
            "content_length": len(content),
        }
