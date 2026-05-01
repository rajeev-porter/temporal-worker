import asyncio
import logging
import signal
import sys

from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

from config import settings
from workflows import KedaTestWorkflow
from activities import keda_test_activity

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Connecting to Temporal Cloud at %s", settings.temporal_endpoint)
    logger.info("Namespace: %s", settings.temporal_namespace)
    logger.info("Task Queue: %s", settings.task_queue)

    client = await Client.connect(
        settings.temporal_endpoint,
        namespace=settings.temporal_namespace,
        api_key=settings.temporal_api_key,
        tls=TLSConfig(),  # TLS required for Temporal Cloud API Key auth
    )

    logger.info("Connected successfully. Starting worker...")

    worker = Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[KedaTestWorkflow],
        activities=[keda_test_activity],
        max_concurrent_activities=1,   
        max_concurrent_workflow_tasks=1
    )

    # Graceful shutdown on SIGTERM / SIGINT
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def _handle_signal():
        logger.info("Shutdown signal received, stopping worker...")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_signal)

    async with worker:
        logger.info("Worker is running and polling task queue '%s'", settings.task_queue)
        await stop_event.wait()

    logger.info("Worker shut down cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Worker failed: %s", e)
        sys.exit(1)
