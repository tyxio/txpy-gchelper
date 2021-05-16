import logging


from google.cloud import automl
from google.cloud.automl import Dataset, Model, ClassificationType
from google.api_core.operation import Operation

from .datasets import Datasets
from .models import Models

logger = logging.getLogger(__name__)

class Trainer:

    def __init__(self, 
        automl_client : automl.AutoMlClient,
        project_id : str,
        region : str
        ):

        self.automl_client = automl_client
        self.project_id = project_id
        self.region = region   

        self.datasetHelper = Datasets(automl_client, project_id=project_id, region=region)
        self.modelHelper = Models(
            automl_client=automl_client, prediction_client=None,
            project_id=project_id, region=region)

    #region Vision
    def train_image_classification_model(self,
        display_name : (str, 'the display name for the dataset and model'),
        input_paths : (str, 'the paths to csv files describing the input data for a new dataset') = '',
        dataset_id : (str, 'the id of an existing dataset to reuse') = '',
        classification_type : (automl.ClassificationType, 'MULTICLASS or MULTILABEL') = automl.ClassificationType.MULTICLASS,
        train_budget_milli_node_hours : int = 24000
        ) -> Operation:

        dataset = None
        if len(dataset_id) == 0:
            # Specify the classification type
            # Types:
            # MultiLabel: Multiple labels are allowed for one example.
            # MultiClass: At most one label is allowed per example.
            # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#classificationtype
            metadata = automl.ImageClassificationDatasetMetadata(
                classification_type=classification_type
            )
            dataset = automl.Dataset(
                display_name=display_name,
                image_classification_dataset_metadata=metadata,
            )

        # Leave model unset to use the default base model provided by Google
        # train_budget_milli_node_hours: The actual train_cost will be equal or
        # less than this value.
        # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#imageclassificationmodelmetadata
        metadata = automl.ImageClassificationModelMetadata(
            train_budget_milli_node_hours=train_budget_milli_node_hours
        )
        model = automl.Model(
            display_name=display_name,
            dataset_id=dataset_id,
            image_classification_model_metadata=metadata,
        )

        long_running_operation = self.train_automl_model(
            model=model,
            dataset=dataset,
            dataset_id=dataset_id,
            input_paths=input_paths
        )

        return long_running_operation

    def train_object_detection_model(self,
        display_name : (str, 'the display name for the dataset and model'),
        input_paths : (str, 'the paths to csv files describing the input data for a new dataset') = '',
        dataset_id : (str, 'the id of an existing dataset to reuse') = '',
        train_budget_milli_node_hours : int = 24000
        ) -> Operation:

        dataset = None
        if len(dataset_id) == 0:
            # Specify the classification type
            # Types:
            # MultiLabel: Multiple labels are allowed for one example.
            # MultiClass: At most one label is allowed per example.
            # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#classificationtype
            metadata = automl.ImageObjectDetectionDatasetMetadata()
            dataset = automl.Dataset(
                display_name=display_name,
                image_object_detection_dataset_metadata=metadata,
            )

        # Leave model unset to use the default base model provided by Google
        # train_budget_milli_node_hours: The actual train_cost will be equal or
        # less than this value.
        # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#imageclassificationmodelmetadata
        metadata = automl.ImageObjectDetectionModelMetadata(
            train_budget_milli_node_hours=train_budget_milli_node_hours
        )
        model = automl.Model(
            display_name=display_name,
            dataset_id=dataset_id, 
            image_object_detection_model_metadata=metadata
        )

        long_running_operation = self.train_automl_model(
            model=model,
            dataset=dataset,
            dataset_id=dataset_id,
            input_paths=input_paths
        )

        return long_running_operation

    #endregion

    #region NLP

    def train_text_classification_model(self,
        display_name : (str, 'the display name for the dataset and model'),
        input_paths : (str, 'the paths to csv files describing the input data for a new dataset') = '',
        dataset_id : (str, 'the id of an existing dataset to reuse') = '',
        classification_type : (automl.ClassificationType, 'MULTICLASS or MULTILABEL') = automl.ClassificationType.MULTICLASS
        ) -> Operation:

        dataset = None
        if len(dataset_id) == 0:
            # Specify the classification type
            # Types:
            # MultiLabel: Multiple labels are allowed for one example.
            # MultiClass: At most one label is allowed per example.
            # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#classificationtype
            metadata = automl.TextClassificationDatasetMetadata(
                classification_type=classification_type
            )
            dataset = automl.Dataset(
                display_name=display_name,
                text_classification_dataset_metadata=metadata,
            )

        model = automl.Model(
            display_name=display_name,
            dataset_id=dataset_id,
            text_classification_model_metadata={}
        )

        long_running_operation = self.train_automl_model(
            model=model,
            dataset=dataset,
            dataset_id=dataset_id,
            input_paths=input_paths
        )

        return long_running_operation

    def train_text_extraction_model(self,
        display_name : (str, 'the display name for the dataset and model'),
        input_paths : (str, 'the paths to csv files describing the input data for a new dataset') = '',
        dataset_id : (str, 'the id of an existing dataset to reuse') = '',
        train_budget_milli_node_hours : int = 24000
        ) -> Operation:

        dataset = None
        if len(dataset_id) == 0:
            dataset = automl.Dataset(
                display_name=display_name,
                text_extraction_dataset_metadata={},
            )

        metadata = automl.TextExtractionModelMetadata()

        model = automl.Model(
            display_name=display_name,
            dataset_id=dataset_id,
            text_extraction_model_metadata=metadata
        )

        long_running_operation = self.train_automl_model(
            model=model,
            dataset=dataset,
            dataset_id=dataset_id,
            input_paths=input_paths
        )

        return long_running_operation


    #enregion

    def train_automl_model(self,
        model  : (Model, 'the model to create.'),
        dataset : (Dataset, 'the dataset to create.') = None,
        input_paths : (str, 'the paths to csv files describing the input data for a new dataset') = '',
        dataset_id : (str, 'the id of an existing dataset to reuse') = '',
        ) -> Operation:

        """
        Create and train an AutoML model.       
          
        """

        if dataset:
            # Create a dataset with the dataset metadata in the region.
            logger.info(f"Creating dataset {dataset.display_name} ...")
            dataset = self.datasetHelper.create_dataset(dataset=dataset)
            if (dataset == None):
                logger.error(f'Could not create the dataset {dataset.display_name}!')
                return
            
            # Import data from the input URI.
            logger.info("Importing Data. This may take a few minutes.")
            self.datasetHelper.import_data(
                dataset_name=dataset.name, 
                input_paths=input_paths)
        
        else:
            # get existing dataset
            logger.info(f"Retrieve  dataset {dataset_id}...")
            dataset = self.datasetHelper.get_dataset(id=dataset_id) 
            if (dataset == None):
                logger.error(f'Could not retrieve the dataset {dataset_id}!')
                return        

        # train the model
        logger.info("Training model...")
        model.dataset_id = dataset.name.split("/")[-1]
        long_running_operation = self.modelHelper.create_model(model=model)   

        return long_running_operation


