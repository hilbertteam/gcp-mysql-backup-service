import logging
import subprocess

from gcp_mysql_backup_service.env import EnvironmentManager
from gcp_mysql_backup_service.secrets import SecretManager


class BackupError(Exception):
    pass


class BackupEnvironmentManager(EnvironmentManager):
    @property
    def database_host(self) -> str:
        return self._get('DATABASE_HOST')

    @property
    def database_port(self) -> int:
        return int(self._get('DATABASE_PORT', 3306))

    @property
    def database_schema(self) -> str:
        return self._get('DATABASE_SCHEMA')

    @property
    def database_user(self) -> str:
        return self._get('DATABASE_USER')

    @property
    def database_password_secret_name(self) -> str:
        return self._get('DATABASE_PASSWORD_SECRET_NAME')

    @property
    def database_ca_secret_name(self) -> str:
        return self._get('DATABASE_CA_SECRET_NAME')

    @property
    def database_client_cert_secret_name(self) -> str:
        return self._get('DATABASE_CLIENT_CERT_SECRET_NAME')

    @property
    def database_client_key_secret_name(self) -> str:
        return self._get('DATABASE_CLIENT_KEY_SECRET_NAME')


class BackupManager:
    def __init__(self, environment_manager: BackupEnvironmentManager, secret_manager: SecretManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._environment_manager: BackupEnvironmentManager = environment_manager
        self._secret_manager: SecretManager = secret_manager

    def _save_secret_locally(self, secret_id: str, file_name: str) -> None:
        secret = self._secret_manager.read_secret(secret_id)

        with open(file_name, 'w') as file:
            file.write(secret)

    def create_backup(self, filename: str) -> None:
        self._logger.info(f'Start creating a {filename} backup')

        password = self._secret_manager.read_secret(self._environment_manager.database_password_secret_name)
        parameters = [
            'mysqldump',
            f'--host={self._environment_manager.database_host}',
            f'--port={str(self._environment_manager.database_port)}',
            f'--user={self._environment_manager.database_user}',
            f'--password={password}',
            '--single-transaction',
            '--skip-add-locks',
            self._environment_manager.database_schema,
        ]

        if self._environment_manager.database_ca_secret_name:
            ca_file_name = 'ca.pem'
            client_cert_file_name = 'client-cert.pem'
            client_key_file_name = 'client-key.pem'

            self._save_secret_locally(self._environment_manager.database_ca_secret_name, ca_file_name)
            self._save_secret_locally(self._environment_manager.database_client_cert_secret_name, client_cert_file_name)
            self._save_secret_locally(self._environment_manager.database_client_key_secret_name, client_key_file_name)

            parameters.extend([
                f'--ssl-ca={ca_file_name}',
                f'--ssl-cert={client_cert_file_name}',
                f'--ssl-key={client_key_file_name}',
            ])

        with open(filename, 'w') as file:
            completed_process = subprocess.run(parameters, stdout=file, stderr=None)

            if completed_process.returncode != 0:
                raise BackupError()

        self._logger.info(f'Backup has been successfully saved to {filename}')
