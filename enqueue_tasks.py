"""
enqueue_tasks.py — run this locally to push tasks into the queue
and trigger KEDA autoscaling.

Usage:
    TEMPORAL_ENDPOINT=... TEMPORAL_NAMESPACE=... TEMPORAL_API_KEY=... \
    python enqueue_tasks.py --count 10
"""

import asyncio
import argparse
import logging
import uuid

from temporalio.client import Client, TLSConfig

from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def enqueue(count: int):
    logger.info(
        "Connecting to %s (namespace: %s)", settings.temporal_endpoint, settings.temporal_namespace
    )

    client = await Client.connect(
        settings.temporal_endpoint,
        namespace=settings.temporal_namespace,
        api_key=settings.temporal_api_key,
        tls=TLSConfig(),
    )

    logger.info("Enqueueing %d workflow(s) on task queue '%s'...", count, settings.task_queue)

    for i in range(count):
        workflow_id = f"keda-test-{uuid.uuid4()}"
        handle = await client.start_workflow(
            "KedaTestWorkflow",
            "hello from enqueue_tasks",
            id=workflow_id,
            task_queue=settings.task_queue,
        )
        logger.info("[%d/%d] Started workflow id=%s", i + 1, count, handle.id)

    logger.info("Done. %d workflow(s) enqueued.", count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enqueue test Temporal workflows")
    parser.add_argument(
        "--count", type=int, default=10, help="Number of workflows to enqueue (default: 10)"
    )
    args = parser.parse_args()
    asyncio.run(enqueue(args.count))
