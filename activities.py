import logging

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def keda_test_activity(message: str) -> str:
    """
    Minimal activity for KEDA autoscaling validation.
    Logs the message and returns a simple response.
    """
    logger.info("Activity received message: %s", message)
    return f"processed: {message}"
