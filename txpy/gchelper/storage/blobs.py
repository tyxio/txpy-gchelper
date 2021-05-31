__version__ = "0.1.0"

import logging
import subprocess
import io
import re

from typing import List

from google.cloud import storage
from google.cloud.storage.blob import Blob

logger = logging.getLogger(__name__)

class Blobs:

    def __init__(self, 
        client : storage.Client,
        no_logging : bool = False
        ):

        self.client = client
        self.no_logging = no_logging

    
    def list_blobs(self,
        bucket_name : str,
        prefix : str = '',
        delimiter : str =None  
        ) -> List[Blob]:  

        '''
        https://googleapis.dev/python/storage/latest/client.html?highlight=list_blobs#google.cloud.storage.client.Client.list_blobs
        
        '''

        blobs = list()
        try:
            blobs = list(self.client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter))

            if self.no_logging == False:
                logger.info("Blobs:")   
                for blob in blobs:
                    logger.info(blob.name)

                if delimiter:
                    logger.info("Prefixes:")
                    for prefix in blobs.prefixes:
                        logger.info(prefix)
        
        except Exception: 
            logger.exception("")

        return blobs

    #region Download

    def download_files(self,
        bucket_name : str,
        prefix : str = '/',
        destination_folder : str = '.',           
        extension_filter : str = "*"      
        ):

        try:            
            subprocess.run(
                f"gsutil -m cp gs://{bucket_name}/{prefix}*.{extension_filter} {destination_folder}",
                shell=True)

        except Exception: 
            logger.exception("")

    def download_as_bytes(self,
        bucket_name : str,
        blob_name : str
        ) -> bytes:

        byte_stream = None
        try:            
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.get_blob(blob_name)
            byte_stream = blob.download_as_bytes()

        except Exception: 
            logger.exception("")

        return byte_stream
    
    def download_as_file(self,
        bucket_name : str,
        blob_name : str
        ) -> io.BytesIO:

        byte_stream = io.BytesIO()
        try:            
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.get_blob(blob_name)
            blob.download_to_file(byte_stream)
            byte_stream.seek(0)

        except Exception: 
            logger.exception("")

        return byte_stream

    #endregion 

    #region Upload

    def upload_file(self, 
            bucket_name : str, 
            source_file_name : str, 
            prefix : str = '/'):
       
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(prefix)

            blob.upload_from_filename(source_file_name)

            logger.info(f"File {source_file_name} uploaded to {prefix}.")
        
        except Exception: 
            logger.exception("")

    def upload_file_as_bytes(self, 
            bucket_name : str,
            prefix : str,
            data : bytes, 
            content_type : str = '',            
            ):
        
        '''
        content_type: application/pdf, image/jpeg, application/octet-stream
        ''' 
        try:
            bucket = self.client.bucket(bucket_name)            
            blob = bucket.blob(prefix)

            if content_type:
                blob.upload_from_string(data, content_type=content_type)
            else:
               blob.upload_from_string(data)

            logger.info(f"File uploaded to {prefix}")
        
        except Exception: 
            logger.exception("")

    def upload_files(self,
        bucket_name : str,
        prefix : str = '',
        source_folder : str = '.',
        extension_filter : str = "*",            
        ):

        try:           
            subprocess.run(
                f"gsutil -m cp {source_folder}/*.{extension_filter} gs://{bucket_name}/{prefix}",
                shell=True)

        except Exception: 
            logger.exception("")

    
    def save_jsonl_content(self,
        json_content : str,
        full_gcs_path : str
        ):
        """Saves jsonl content to specified GCS location.

        Args:
            jsonl: jsonl file
            full_gcs_path: GCS location to upload the jsonl file
        """
        try: 
            match = re.match(r"gs://([^/]+)/(.*)", full_gcs_path)
            bucket_name = match.group(1)
            blob_name = match.group(2)

            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)

            blob.upload_from_string(json_content)

        except Exception: 
            logger.exception("")
            
    #endregion

