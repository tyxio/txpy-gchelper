import logging
import io as io

from typing import List

from google.cloud import automl
from google.cloud.automl import Model
from google.api_core.operation import Operation


logger = logging.getLogger(__name__)

class Models:

    def __init__(self, 
        automl_client : automl.AutoMlClient,
        prediction_client : automl.PredictionServiceClient,
        project_id : str,
        region : str
        ):

        self.automl_client = automl_client
        self.prediction_client = prediction_client
        self.project_id = project_id
        self.region = region
 
    def create_model(self,
        model : (Model, 'The model to create')
        ) -> Operation:

        response = None
        try:
            # A resource that represents Google Cloud Platform location.
            project_location = f"projects/{self.project_id}/locations/{self.region}"
            
            # Create a model with the model metadata in the region.
            response = self.automl_client.create_model(parent=project_location, model=model)

            logger.info(f"Training operation name:{response.operation.name}")
            logger.info("Training started...")

        except Exception: 
            logger.exception("")

        return response

    def list_models(self):

        try:
            project_location = f"projects/{self.project_id}/locations/{self.region}"

            # List all the datasets available in the region.
            request = automl.ListModelsRequest(parent=project_location, filter="")
            response = self.automl_client.list_models(request=request)

            logger.info("List of models:\n")
            for model  in response:
                if model.deployment_state == automl.Model.DeploymentState.DEPLOYED:
                    deployment_state = "deployed"
                else:
                    deployment_state = "undeployed"

                logger.info(f'Model name: {model.name}')
                logger.info(f'Model id: {model.name.split("/")[-1]}')
                logger.info(f'Model display name: {model.display_name}')
                logger.info(f'Model create time: {model.create_time}')
                logger.info(f'Model deployment state: {deployment_state} \n')
        
        except Exception: 
            logger.exception("")

    def get_model(self, 
        id : str
        ):

        try:
            full_id = self.automl_client.model_path(self.project_id, self.region, id)
            model = self.automl_client.get_model(name=full_id)

            if model.deployment_state == automl.Model.DeploymentState.DEPLOYED:
                deployment_state = "deployed"
            else:
                deployment_state = "undeployed"

            logger.info(f'Model name: {model.name}')
            logger.info(f'Model id: {model.name.split("/")[-1]}')
            logger.info(f'Model display name: {model.display_name}')
            logger.info(f'Model create time: {model.create_time}')
            logger.info(f'Model deployment state: {deployment_state} \n')

            logger.info("List of model evaluations:")
            for evaluation in self.automl_client.list_model_evaluations(parent=model_full_id, filter=""):
                logger.info(f"Model evaluation name: {evaluation.name}")
                logger.info(f"Model annotation spec id: {evaluation.annotation_spec_id}")
                logger.info(f"Create Time: {evaluation.create_time}")
                logger.info(f"Evaluation example count: {evaluation.evaluated_example_count}")
                logger.info(f"Classification model evaluation metrics: { evaluation.classification_evaluation_metrics}")

        except Exception: 
            logger.exception("")

    def delete_model(self, id : str):

        try:
            full_id = self.automl_client.model_path(self.project_id, self.region, id)

            response = self.automl_client.delete_model(name=full_id)

            logger.info(f"Model deleted. {response.result()}") 

        except Exception: 
            logger.exception("")

    def vision_predict(self, 
        model_id : (str, 'the id of the deployed vision model'),
        image : (bytes, 'the image as a byte array'),
        score_threshold : float = 0.7
        ):

        response_payload = None
        try:
            model_full_id = self.automl_client.model_path(self.project_id, self.region, model_id)
    
            payload = {"image": {"image_bytes": image}}

            if score_threshold:
                params = {"score_threshold": str(score_threshold)}

            request = automl.PredictRequest(name=model_full_id, payload=payload, params=params)
            response = self.prediction_client.predict(request=request)
            response_payload = response.payload
     
        except Exception: 
            logger.exception("")

        return response_payload

    def nlp_predict(self, 
        model_id : (str, 'the id of the deployed nlp model'),
        content : (str, 'the text to submit to the prediction model')   
        ):
        
        response_payload = None
        try:
            model_full_id = self.automl_client.model_path(self.project_id, self.region, model_id)
    
            text_snippet = automl.TextSnippet(content=content, mime_type="text/plain")
            payload = automl.ExamplePayload(text_snippet=text_snippet)
            #payload = {'text_snippet': {'content': content, 'mime_type': 'text/plain' }}
           
            response = self.prediction_client.predict(name=model_full_id, payload=payload)
            response_payload = response.payload
     
        except Exception: 
            logger.exception("")

        return response_payload
