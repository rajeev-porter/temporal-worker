import logging
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import keda_test_activity

logger = logging.getLogger(__name__)


@workflow.defn
class KedaTestWorkflow:
    """
    Minimal workflow used to validate KEDA autoscaling with Temporal Cloud.
    Runs a single activity and completes — no real business logic.
    """

    @workflow.run
    async def run(self, message: str = "hello") -> str:
        logger.info("Workflow started with message: %s", message)

        result = await workflow.execute_activity(
            keda_test_activity,
            message,
            start_to_close_timeout=timedelta(seconds=300),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        logger.info("Workflow completed with result: %s", result)
        return result
