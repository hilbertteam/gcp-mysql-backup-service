# MySQL Backup Service

MySQL Backup Service is a Python program automating MySQL backups on Google Cloud Platform.


## Usage 

The application requires several configuration parameters to be set up before using:

### GCP related parameters
- **PROJECT_ID** which is an ID of the GCP project

### Database related parameters 
- **DATABASE_HOST** which is a FQDN or an IP address of the database server 
- **DATABASE_PORT** which is a open port of the database server
- **DATABASE_SCHEMA** which is a name of a schema (database name) which you want to backup
- **DATABASE_USER** which is a name of a user you want to use to create a backup
- **DATABASE_PASSWORD_SECRET_NAME** which is a name of a secret stored in Google Secret Manager and containing a user's password
- **DATABASE_CA_SECRET_NAME** which is a name of a secret stored in Google Secret Manager and containing a CA file (optional)
- **DATABASE_CLIENT_CERT_SECRET_NAME** which is a name of a secret stored in Google Secret Manager and containing a client SSL certificate (optional) 
- **DATABASE_CLIENT_KEY_SECRET_NAME** which is a name of secret stored in Google Secret Manager and containing client's private key (optional)

### Google Pub/Sub related parameters
- **SUBSCRIPTION_NAME** which is a name of a Google Pub/Sub subscription used for triggering the backup process 
- **SUBSCRIPTION_TIMEOUT_SECONDS** which contains maximum amount of time in seconds allowed to create a backup and acknowledge the Pub/Sub message

### Google Cloud Storage related parameters 
- **BUCKET_NAME** which is a name of Google Cloud Storage bucket used for storing backups


After you set up all the parameters described you need to set up GCP services:
1. Create a Cloud Pub/Sub topic and subscription
2. Create a Cloud Storage bucket
3. Add a database password to Cloud Secret Manager


After that grant all the required roles to the user which will be used for running **MySQL Backup Service**:
- Pub/Sub Subscriber
- Storage Object Creator (global or for the bucket)
- Secret Manager Viewer


To test **MySQL Backup Service** execute the following steps:
1. Install Google Cloud SDK using [the following instructions](https://cloud.google.com/sdk/install).
2. Authenticate using `gcloud`:
```bash
gcloud auth login
```
3. Set [Application Default Credentials](https://cloud.google.com/sdk/gcloud/reference/auth/application-default) which will be used by a local instance of MySQL Backup Service:
```bash
gcloud auth application-default login
```
4. Install Poetry:
```bash
pip install poetry
```
4. Install dependencies:
```bash
poetry install -v
```
5. Export all the environment variables described above:
```
export PROJECT_ID=<PROJECT_ID>
export DATABASE_HOST=<DATABASE_HOST>
export DATABASE_SCHEMA=<DATABASE_SCHEMA>
export DATABASE_USER=<DATABASE_USER>
export DATABASE_PASSWORD_SECRET_NAME=<DATABASE_PASSWORD_SECRET_NAME>
export SUBSCRIPTION_NAME=<SUBSCRIPTION_NAME>
export BUCKET_NAME=<BUCKET_NAME>
```
6. Run MySQL Backup Service:
```bash
python -m gcp_mysql_backup_service run --logging-config config/logging-config.yml
```
7. Open a new terminal window and send a message to the Cloud Pub/Sub topic:
```
gcloud pubsub topics publish mysql-backup-service --message=test
```
8. In the terminal running MySQL Backup Service you should see the following output: 
```
gcp_mysql_backup_service.backup - INFO - Start creating a employees.sql backup
gcp_mysql_backup_service.backup - INFO - Backup has been successfully saved to employees.sql
gcp_mysql_backup_service.storage - INFO - Started uploading employees.sql to d6c437d0-2fa0-43da-bb84-65fb3ccfa371-mysql-backup-service bucket
gcp_mysql_backup_service.storage - INFO - Started uploading employees.sql as employees_2020_06_01_03_00.sql blob to d6c437d0-2fa0-43da-bb84-65fb3ccfa371-mysql-backup-service bucket
gcp_mysql_backup_service.storage - INFO - File employees.sql has been successfully uploaded to d6c437d0-2fa0-43da-bb84-65fb3ccfa371-mysql-backup-service bucket as employees_2020_06_01_03_00.sql
```
9. After that check that the backup was actually stored in the Cloud Storage bucket:
```
gsutil ls gs://d6c437d0-2fa0-43da-bb84-65fb3ccfa371-mysql-backup-service/gs://d6c437d0-2fa0-43da-bb84-65fb3ccfa371-mysql-backup-service/employees_2020_06_01_03_00.sql
```