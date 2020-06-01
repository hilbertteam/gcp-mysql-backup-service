import logging
from typing import Optional, Callable, Any

from google.cloud import pubsub_v1

from gcp_mysql_backup_service.env import EnvironmentManager


class SubscriptionEnvironmentManager(EnvironmentManager):
    @property
    def subscription_name(self) -> str:
        return self._get('SUBSCRIPTION_NAME')

    @property
    def timeout(self) -> int:
        return int(self._get('SUBSCRIPTION_TIMEOUT_SECONDS', 600))


class SubscriptionManager:
    def __init__(self, environment_manager: SubscriptionEnvironmentManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._environment_manager: SubscriptionEnvironmentManager = environment_manager
        self._client: Optional[pubsub_v1.SubscriberClient] = None
        self._subscriptions = []

    def _get_client(self) -> pubsub_v1.SubscriberClient:
        if self._client is None:
            self._client = pubsub_v1.SubscriberClient()

        return self._client

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        subscription_path = self._get_client().subscription_path(
            self._environment_manager.project_id,
            self._environment_manager.subscription_name
        )
        subscription = self._get_client().subscribe(
            subscription_path,
            callback=callback
        )

        self._subscriptions.append(subscription)

    def run(self) -> None:
        with self._get_client():
            for subscription in self._subscriptions:
                try:
                    subscription.result(timeout=self._environment_manager.timeout)
                except:
                    subscription.cancel()
