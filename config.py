import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    temporal_endpoint: str
    temporal_namespace: str
    temporal_api_key: str
    task_queue: str


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set or empty."
        )
    return value


settings = Settings(
    temporal_endpoint=_require("TEMPORAL_ENDPOINT"),
    temporal_namespace=_require("TEMPORAL_NAMESPACE"),
    temporal_api_key=_require("TEMPORAL_API_KEY"),
    task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "keda-test-queue"),
)
