import yaml
import logging
import os
import sys

from google.cloud import storage


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from txpy.gchelper.storage.buckets import Buckets
from txpy.gchelper.storage.blobs import Blobs

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

config = yaml.safe_load(open("tests/config.yaml", "r"))

if ("service_acct" in config and "key_path" in config["service_acct"]):
    service_acct = config["service_acct"]["key_path"]
    storage_client = storage.Client.from_service_account_json(service_acct)
else:
    storage_client = storage.Client()

buckets = Buckets(storage_client, region=config["pipeline_project"]["region"])

blobs = Blobs(storage_client)

def storage_buckets(function, bucket_name):
    if function == 'create':
        buckets.create_bucket(bucket_name)
    elif function == 'listing':
        buckets.list_buckets()
    elif function == 'get':
        buckets.list_bucket(bucket_name)
    elif function == 'delete':
        buckets.delete_bucket(bucket_name)
    elif function == 'size':
        buckets.size_bucket(bucket_name)

def storage_blobs(function, bucket_name, prefix, local_path, filter, content_type):

    if function == 'listing':
        blobs.list_blobs(bucket_name, prefix)
    
    elif function == 'upload_file':
        blobs.upload_file(
            bucket_name=bucket_name, 
            prefix=prefix,
            source_file=local_path)
    
    elif function == 'upload_file_as_bytes':
        filename = 'YesWeCode.png'
        with open("tests/" + filename, "rb") as image:
            data = image.read()
        blobs.upload_file_as_bytes(
            bucket_name=bucket_name, 
            prefix=prefix,
            data=data,
            content_type=content_type
            )

    elif function == 'upload_files':
        blobs.upload_files(
            bucket_name=bucket_name, 
            prefix=prefix,
            source_folder=local_path,
            extension_filter=filter)
  
    elif function == 'download_files':
        blobs.download_files(
            bucket_name=bucket_name, 
            prefix=prefix,
            destination_folder=local_path,
            extension_filter=filter)             

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Google Storage API Helper')
    parser.add_argument('--resource', required=True,
                        help='the resource type (e.g. storage)')
    parser.add_argument('--function', required=True,
                        help='the function to execute (e.g. listing)')
    parser.add_argument('--bucket_name', required=True,
                        help='the bucket name')
    parser.add_argument('--prefix', 
                        help='the blob prefix (e.g. "public/samples/)')    
    parser.add_argument('--local_path', 
                        help='the path to the local file or folder')   
    parser.add_argument('--filter', 
                        help='the filter name') 
    parser.add_argument('--content_type', 
                        help='the file content type') 
    args = parser.parse_args()

    if args.resource == 'buckets':
        storage_buckets(args.function, args.bucket_name)
    elif args.resource == 'blobs':
        storage_blobs(args.function, args.bucket_name, args.prefix, args.local_path, 
            args.filter, args.content_type)


