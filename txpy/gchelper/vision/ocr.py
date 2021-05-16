import logging
import os

from google.cloud import vision, storage

from ..storage.blobs import Blobs
from ..storage.buckets import Buckets

logger = logging.getLogger(__name__)

class OCR:

    def __init__(self, 
        service_acct : str,
        project_id : str,
        region : str = 'us-central1'
        ):

        logger.info(f"Create OCR client for project {project_id} in region {region}")
        
        self.project_id = project_id
        self.region = region
        
        self.vision_client = vision.ImageAnnotatorClient.from_service_account_file(service_acct)
        
        self.storage_client = storage.Client.from_service_account_json(service_acct)
        self.bucketsHelper = Buckets(self.storage_client, region=region)
        self.blobsHelper = Blobs(self.storage_client)


    def run_ocr(self,
        source_bucket : str, 
        source_prefix : str,
        temp_directory : str = './tmp'
        ):

        logger.info(f"source:{source_bucket}/{source_prefix} temp:{temp_directory}")
        
        # get source blobs (png files)
        blobs = self.blobsHelper.list_blobs(source_bucket, prefix=source_prefix)
        #blobs = self.storage_client.list_blobs(source_bucket, prefix=source_prefix)

        image = vision.Image()
        for blob in blobs:
            if blob.name.endswith(".png"):

                logger.info(f"Processing OCR for {blob.name}.")

                image.source.image_uri = f"gs://{source_bucket}/{blob.name}"
                response = self.vision_client.text_detection(image=image)

                if (response and response.text_annotations):
                    #save text description in temp file
                    text = response.text_annotations[0].description
                    temp_txt = os.path.join(
                        temp_directory, os.path.basename(blob.name).replace(".png", ".txt"))

                    with open(temp_txt, "w") as f:
                        f.write(text)
                        f.close()
        
                else:
                    logger.warn(f'OCR faild for {blob.name}')
        