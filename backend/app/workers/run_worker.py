import argparse
import asyncio
import logging
import signal
import sys

from app.core.logging import setup_logging
from app.workers.ai_analysis_worker import AIAnalysisWorker
from app.workers.notifications_worker import NotificationsWorker
from app.workers.report_generation_worker import ReportGenerationWorker
from app.workers.retry_scheduler import RetrySchedulerWorker
from app.workers.static_analysis_worker import StaticAnalysisWorker
from app.workers.webhook_worker import WebhookWorker

logger = logging.getLogger("reviewai.worker_runner")


async def main():
    parser = argparse.ArgumentParser(description="ReviewAI Async Redis Background Workers CLI")
    parser.add_argument(
        "--queue",
        type=str,
        default="all",
        help="Queue worker to run: 'webhook_processing', 'ai_analysis', 'static_analysis', 'report_generation', 'notifications', 'retry_scheduler', or 'all'",
    )
    args = parser.parse_args()

    setup_logging()
    logger.info("Starting ReviewAI Worker Runner for target queue: '%s'", args.queue)

    workers = []

    if args.queue in ("webhook_processing", "all"):
        workers.append(WebhookWorker())

    if args.queue in ("ai_analysis", "all"):
        workers.append(AIAnalysisWorker())

    if args.queue in ("static_analysis", "all"):
        workers.append(StaticAnalysisWorker())

    if args.queue in ("report_generation", "all"):
        workers.append(ReportGenerationWorker())

    if args.queue in ("notifications", "all"):
        workers.append(NotificationsWorker())

    if args.queue in ("retry_scheduler", "all"):
        workers.append(RetrySchedulerWorker())

    if not workers:
        logger.error("No valid worker specified for target queue '%s'", args.queue)
        sys.exit(1)

    # Setup signal handler for graceful shutdown
    loop = asyncio.get_running_loop()

    def shutdown():
        logger.info("Shutdown signal received. Stopping workers...")
        for w in workers:
            w.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown)
        except NotImplementedError:
            # Signal handling on Windows selector loop fallback
            pass

    # Gather tasks
    tasks = [asyncio.create_task(w.start()) for w in workers]
    logger.info("Successfully launched %d background worker task(s). Running...", len(tasks))

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Worker tasks cancelled.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Exiting worker process.")
