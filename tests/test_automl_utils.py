import yaml
import logging
import os
import sys

from google.cloud import automl

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from txpy.gchelper.automl.datasets import Datasets
from txpy.gchelper.automl.models import Models

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

config = yaml.safe_load(open("config.yaml", "r"))

automl_client = automl.AutoMlClient()

ds = Datasets(automl_client,
    project_id=config["pipeline_project"]["project_id"],
    region=config["pipeline_project"]["region"]
    )

mod = Models(automl_client,
    project_id=config["pipeline_project"]["project_id"],
    region=config["pipeline_project"]["region"]
    )


def automl_datasets(function, id):
    
    if function == 'listing':
        ds.list_datasets()
    elif function == 'get':
        ds.get_dataset(id)
    elif function == 'delete':
        ds.delete_dataset(id)

def automl_models(function, id):
    
    if function == 'listing':
        mod.list_models()
    elif function == 'get':
        mod.get_model(id)
    elif function == 'delete':
        mod.delete_model(id)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Google AutoML API Helper')
    parser.add_argument('--resource', required=True,
                        help='the resource type (e.g. datasets, modules)')
    parser.add_argument('--function', required=True,
                        help='the function to execute (e.g. listing)')
    parser.add_argument('--id', 
                        help='the resource id (e.g. ICN9206264185682395136)')
    
    args = parser.parse_args()

    if args.resource == 'datasets':
        automl_datasets(args.function, args.id)
    elif args.resource == 'models':
        automl_models(args.function, args.id)


