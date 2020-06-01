from typing import Optional

from google.cloud import secretmanager

from gcp_mysql_backup_service.env import EnvironmentManager


class SecretManager:
    def __init__(self, environment_manager: EnvironmentManager) -> None:
        self._environment_manager: EnvironmentManager = environment_manager
        self._client: Optional[secretmanager.SecretManagerServiceClient] = None

    def _get_client(self) -> secretmanager.SecretManagerServiceClient:
        if self._client is None:
            self._client = secretmanager.SecretManagerServiceClient()

        return self._client

    def read_secret(self, secret_id: str, version_id: str = '1') -> str:
        name = self._get_client().secret_version_path(self._environment_manager.project_id, secret_id, version_id)
        response = self._get_client().access_secret_version(name)
        payload = response.payload.data.decode('UTF-8')

        return payload
