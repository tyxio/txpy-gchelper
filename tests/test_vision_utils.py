import yaml
import logging
import os
import sys
from google.cloud import automl

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from txpy.gchelper.vision.ocr import OCR

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

config = yaml.safe_load(open("config.yaml", "r"))

if ("service_acct" in config and "key_path" in config["service_acct"]):
    ocrHelper = OCR(
        service_acct=config["service_acct"]["key_path"], 
        project_id=config["pipeline_project"]["project_id"],
        region=config["pipeline_project"]["region"]
        )
else:
    ocrHelper = None

def vision_ocr(function,
    source_bucket, source_prefix
    ):

    if ocrHelper == None:
        logger.error("Service account is not defined in the configuration")
        return
    
    if function == 'png_to_text':
        ocrHelper.run_ocr(
            source_bucket=source_bucket,
            source_prefix=source_prefix)



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Vision helper')
    parser.add_argument('--resource', required=True,
                        help='the resource type (e.g. pdf)')
    parser.add_argument('--function', required=True,
                        help='the function to execute (e.g. pdf_to_png)')
    parser.add_argument('--source_bucket', 
                        help='')   
    parser.add_argument('--source_prefix', 
                        help='')     

    args = parser.parse_args()

    if args.resource == 'ocr':
        vision_ocr(args.function, args.source_bucket, args.source_prefix)