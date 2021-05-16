import logging

from google.cloud import automl
from google.cloud.automl import Dataset

logger = logging.getLogger(__name__)

class Datasets:

    def __init__(self, 
        client : automl.AutoMlClient,
        project_id : str,
        region : str
        ):

        self.client = client
        self.project_id = project_id
        self.region = region
 
    def create_dataset(self,
        dataset : Dataset
        ) -> Dataset:

        created_dataset = None
        try:
            # A resource that represents Google Cloud Platform location.
            project_location = f"projects/{self.project_id}/locations/{self.region}"
            
            # Create a dataset with the dataset metadata in the region.
            response = self.client.create_dataset(parent=project_location, dataset=dataset)

            created_dataset = response.result()

            # Display the dataset information
            logger.info(f"Dataset name: {created_dataset.name}")
            logger.info(f'Dataset id: {created_dataset.name.split("/")[-1]}')
        
        except Exception: 
            logger.exception("")
        
        return created_dataset

    def import_data(self,
        input_paths : str,
        dataset_name : str = '',
        dataset_id : str = ''
        ):

        try:
            if len(dataset_name) != 0:
                dataset_full_id = dataset_name
            else:
                # Get the full path of the dataset.
                dataset_full_id = self.client.dataset_path(
                    project=self.project_id,
                    location=self.region,
                    dataset=dataset_id)
            
            # Get the multiple Google Cloud Storage URIs
            input_uris = input_paths.split(",")
            gcs_source = automl.GcsSource(input_uris=input_uris)
            input_config = automl.InputConfig(gcs_source=gcs_source)
            
            # Import data from the input URI
            response = self.client.import_data(name=dataset_full_id, input_config=input_config)

            logger.info("Processing import...")
            logger.info(f"Data imported. {response.result()}")
        
        except Exception: 
            logger.exception("")  

    def list_datasets(self):

        try:
            project_location = f"projects/{self.project_id}/locations/{self.region}"

            # List all the datasets available in the region.
            request = automl.ListDatasetsRequest(parent=project_location, filter="")
            response = self.client.list_datasets(request=request)

            logger.info("List of datasets:\n")
            for dataset in response:
                logger.info(f'Dataset name: {dataset.name}')
                logger.info(f'Dataset id: {dataset.name.split("/")[-1]}')
                logger.info(f'Dataset display name: {dataset.display_name}')
                logger.info(f'Dataset create time: {dataset.create_time}')
                logger.info(f'Image classification dataset metadata: {dataset.image_classification_dataset_metadata} \n')

        except Exception: 
            logger.exception("")

    def get_dataset(self, id : str) -> Dataset:

        dataset = None
        try:
            full_id = self.client.dataset_path(self.project_id, self.region, id)
            dataset = self.client.get_dataset(name=full_id)

            logger.info(f'Dataset name: {dataset.name}')
            logger.info(f'Dataset id: {dataset.name.split("/")[-1]}')
            logger.info(f'Dataset display name: {dataset.display_name}')
            logger.info(f'Dataset create time: {dataset.create_time}')
            logger.info(f'Image classification dataset metadata: {dataset.image_classification_dataset_metadata} \n')

        except Exception: 
            logger.exception("")
        
        return dataset

    def delete_dataset(self, id : str):

        try:
            full_id = self.client.dataset_path(self.project_id, self.region, id)

            response = self.client.delete_dataset(name=full_id)

            logger.info(f"Dataset deleted. {response.result()}") 

        except Exception: 
            logger.exception("")