import os
from typing import Any


class EnvironmentManager:
    def _get(self, key: str, default: Any = '') -> str:
        return os.environ.get(key, default)

    @property
    def project_id(self) -> str:
        return self._get('PROJECT_ID')
