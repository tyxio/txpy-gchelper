from re import A
import yaml
import logging
import os
import sys


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from google.cloud import pubsub_v1
from txpy.gchelper.pubsub.pubsub import PubSub

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

config = yaml.safe_load(open("tests/config.yaml", "r"))

pubsub = PubSub(
    service_acct=config["service_acct"]["key_path"],
    project_id=config["pipeline_project"]["project_id"],
    topic_id=config["pubsub"]["topic_id"],
    subscription_id=config["pubsub"]["subscription_id"] 
    )

def subscribe_callback(message):
    print(f"Received {message}.")
    # Acknowledge the message. Unack'ed messages will be redelivered.
    message.ack()
    print(f"Acknowledged {message.message_id}.")

def pubsub_fun(function, message):
    
    if function == 'get_iam_policy':
        pubsub.get_topic_policy()
        pubsub.get_subscription_policy()
    elif function == 'publish':
        myattrs = {
            "origin": "Ford",
            "model": "Mustang"
            }
        pubsub.publish(message=message, **myattrs)
    elif function == 'subscribe':
        pubsub.subscribe(callback=subscribe_callback)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='pub/sub ')
    parser.add_argument('--function', required=True,
                        help='the function to execute (e.g. get_iam_policy)')
    parser.add_argument('--message', 
                        help='a message...')
    args = parser.parse_args()

    pubsub_fun(args.function, args.message)
