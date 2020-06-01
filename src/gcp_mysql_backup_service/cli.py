import logging
import sys
from functools import partial
from typing import Type

import click
from types import TracebackType

from google.cloud.pubsub_v1.subscriber.message import Message

from gcp_mysql_backup_service.backup import BackupEnvironmentManager, BackupManager
from gcp_mysql_backup_service.config import LoggingConfig
from gcp_mysql_backup_service.env import EnvironmentManager
from gcp_mysql_backup_service.secrets import SecretManager
from gcp_mysql_backup_service.storage import StorageManager, StorageEnvironmentManager
from gcp_mysql_backup_service.subscription import SubscriptionManager, SubscriptionEnvironmentManager


def excepthook(
        exception_type: Type[BaseException],
        exception_instance: BaseException,
        exception_traceback: TracebackType) -> None:
    """
    Function called for uncaught exceptions
    :param exception_type: Type of an exception
    :param exception_instance: Exception instance
    :param exception_traceback: Exception traceback
    """

    logging.fatal(
        f'Exception hook has been fired: {exception_instance}',
        exc_info=(exception_type, exception_instance, exception_traceback))


sys.excepthook = excepthook


def callback(
        environment_manager: BackupEnvironmentManager,
        backup_manager: BackupManager,
        storage_manager: StorageManager,
        message: Message) -> None:
    schema_name = environment_manager.database_schema
    backup_filename = f'{schema_name}.sql'
    backup_manager.create_backup(backup_filename)

    storage_manager.upload_file(backup_filename)
    message.ack()


@click.group()
@click.pass_context
def cli(*args, **kwargs) -> None:  # type: ignore
    """
    gcp-mysql-backup-service is a Python program automating MySQL backups on Google Cloud Platform (GCP)
    """

    pass


@cli.command()
@click.option('--logging-config', '-l', help='Path to the logging configuration file', type=str, default='config/logging-config.yml')
def run(logging_config: str) -> None:
    """
    Runs a MySQL backup service
    """

    logging_config = LoggingConfig.load(logging_config)
    logging_config.apply()
    logger = logging.getLogger()

    logger.info('Started running MySQL backup service')

    secret_manager = SecretManager(EnvironmentManager())
    backup_manager = BackupManager(BackupEnvironmentManager(), secret_manager)
    storage_manager = StorageManager(StorageEnvironmentManager())
    subscription_callback = partial(callback, BackupEnvironmentManager(), backup_manager, storage_manager)

    subscription_manager = SubscriptionManager(SubscriptionEnvironmentManager())
    subscription_manager.subscribe(subscription_callback)
    subscription_manager.run()

    logger.info('Finished running MySQL backup service')
