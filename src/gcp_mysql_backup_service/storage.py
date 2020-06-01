import datetime
import logging
import os
from typing import Optional

from google.cloud import storage

from gcp_mysql_backup_service.env import EnvironmentManager


class StorageEnvironmentManager(EnvironmentManager):
    def bucket_name(self) -> str:
        return self._get('BUCKET_NAME')


class StorageManager:
    def __init__(self, environment_manager: StorageEnvironmentManager) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._environment_manager: StorageEnvironmentManager = environment_manager
        self._client: Optional[storage.Client] = None

    def _get_client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()

        return self._client

    def upload_file(self, filename: str) -> None:
        bucket_name = self._environment_manager.bucket_name()

        self._logger.info(f'Started uploading {filename} to {bucket_name} bucket')

        filename_parts = os.path.splitext(filename)
        filename_without_extension = filename_parts[0]
        extension = filename_parts[1]
        date_string = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        destination_blob_name = f'{filename_without_extension}_{date_string}{extension}'

        bucket = self._get_client().bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        self._logger.info(f'Started uploading {filename} as {destination_blob_name} blob to {bucket_name} bucket')

        blob.upload_from_filename(filename)

        self._logger.info(
            f'File {filename} has been successfully uploaded to {bucket_name} bucket as {destination_blob_name}')
