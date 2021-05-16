__version__ = "0.1.0"

import logging
import subprocess

from google.cloud import storage
from google.cloud.storage.bucket import Bucket
from google.api_core.exceptions import Conflict

logger = logging.getLogger(__name__)

class Buckets:

    def __init__(self, 
        client : storage.Client,
        region : str
        ):

        self.client = client
        self.region = region


    def create_bucket(self, 
        bucket_name : str, 
        storage_class : str = 'STANDARD'
        ) -> Bucket:
        """Creates a bucket """

        try:
            bucket = self.client.bucket(bucket_name)
            bucket.storage_class = storage_class

            new_bucket = self.client.create_bucket(bucket, location=self.region)
        
            logger.info(f"Created bucket {new_bucket.name} in {new_bucket.location} \
                with storage class {new_bucket.storage_class}")
            
            return new_bucket

        except Conflict: # HTTP 409
            logger.info(f"Bucket {bucket_name} exists already")
            return bucket

        except Exception: 
            logger.exception("")

        return None

    def list_buckets(self):
        """Lists all buckets."""

        try:
            buckets = self.client.list_buckets()

            for bucket in buckets:
                self.log_bucket_info(bucket)

        except Exception: 
            logger.exception("")
    
    def list_bucket(self, bucket_name : str):
        """Lists a bucket """

        try:
            bucket = self.client.get_bucket(bucket_name)

            self.log_bucket_info(bucket)
        
        except Exception: 
            logger.exception("")

    def delete_bucket(self, bucket_name : str):
        """Deletes a bucket. The bucket must be empty."""

        try:
            bucket = self.client.get_bucket(bucket_name)
            bucket.delete()

            logger.info("Bucket {} deleted".format(bucket.name))

        except Exception: 
            logger.exception("")
    
    def size_bucket(self, bucket_name : str):

        try:
            subprocess.run(
                f"gsutil du -s  gs://{bucket_name}", shell=True)

        except Exception: 
            logger.exception("")

    def log_bucket_info(self, bucket : storage.bucket):
        logger.info("ID: {}".format(bucket.id))
        logger.info("Name: {}".format(bucket.name))
        logger.info("Storage Class: {}".format(bucket.storage_class))
        logger.info("Location: {}".format(bucket.location))
        logger.info("Location Type: {}".format(bucket.location_type))
        logger.info("Cors: {}".format(bucket.cors))
        logger.info(
            "Default Event Based Hold: {}".format(bucket.default_event_based_hold)
        )
        logger.info("Default KMS Key Name: {}".format(bucket.default_kms_key_name))
        logger.info("Metageneration: {}".format(bucket.metageneration))
        logger.info(
            "Retention Effective Time: {}".format(
                bucket.retention_policy_effective_time
            )
        )
        logger.info("Retention Period: {}".format(bucket.retention_period))
        logger.info("Retention Policy Locked: {}".format(bucket.retention_policy_locked))
        logger.info("Requester Pays: {}".format(bucket.requester_pays))
        logger.info("Self Link: {}".format(bucket.self_link))
        logger.info("Time Created: {}".format(bucket.time_created))
        logger.info("Versioning Enabled: {}".format(bucket.versioning_enabled))
        logger.info("Labels:")
        logger.info(f'{bucket.labels}\n')    
   

    
