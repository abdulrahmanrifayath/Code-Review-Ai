import logging
from typing import Any, Dict, Optional

from app.core.database import AsyncSessionLocal
from app.core.queue.schemas import QueueType
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.static_analysis")


class StaticAnalysisWorker(BaseWorker):
    """
    Background worker for asynchronous Static Code Analysis.
    Runs security scanning, code quality calculation, AST parsing,
    and performance vulnerability detection.
    """

    def __init__(self, worker_id: Optional[str] = None, queue_mgr: Optional[Any] = None):
        super().__init__(queue_type=QueueType.STATIC_ANALYSIS, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        repo_full_name = payload.get("repo_full_name")
        pr_number = payload.get("pr_number")
        code_files = payload.get("files", [])

        logger.info("Executing Static Analysis for PR #%s on '%s' (action: %s)", pr_number, repo_full_name, action)

        async with AsyncSessionLocal() as db:
            from app.services.analysis_service import AnalysisService
            service = AnalysisService(db)

            result = await service.run_static_analysis(
                user=payload.get("user"),
                repository_id=payload.get("repository_id"),
                pr_number=pr_number,
            )
            await db.commit()

        return result
