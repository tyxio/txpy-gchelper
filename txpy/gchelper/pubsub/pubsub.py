import logging

from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)

# see https://github.com/googleapis/python-pubsub/tree/master/samples/snippets

class PubSub:

    def __init__(self, 
        service_acct: str,
        project_id: str,
        topic_id: str,
        subscription_id: str
        ):

        logger.info(f"Create pubsub client ")

        self.publisher_client = pubsub_v1.PublisherClient.from_service_account_json(service_acct)

        self.subscriber_client = pubsub_v1.SubscriberClient.from_service_account_json(service_acct)   
        self.topic_path = self.subscriber_client.topic_path(project_id, topic_id)
        self.subscription_path = self.subscriber_client.subscription_path(project_id, subscription_id)
        

    # https://github.com/googleapis/python-pubsub/blob/HEAD/samples/snippets/iam.py
    def get_topic_policy(self):
        
        policy = self.subscriber_client.get_iam_policy(request={"resource": self.topic_path})

        print("Policy for topic {}:".format(self.topic_path))
        for binding in policy.bindings:
            print("Role: {}, Members: {}".format(binding.role, binding.members))

        
        # [END pubsub_get_topic_policy]

    # https://github.com/googleapis/python-pubsub/blob/HEAD/samples/snippets/iam.py
    def get_subscription_policy(self):

        policy = self.subscriber_client.get_iam_policy(request={"resource": self.subscription_path})

        print("Policy for subscription {}:".format(self.subscription_path))
        for binding in policy.bindings:
            print("Role: {}, Members: {}".format(binding.role, binding.members))

        self.subscriber_client.close()

    # https://github.com/googleapis/python-pubsub/tree/d0d0b704642df8dee893d3f585aeb666e19696fb/samples/snippets/quickstart
    def publish(self, message: str, **attrs):
        """Publishes a message to a Pub/Sub topic."""
        # Data sent to Cloud Pub/Sub must be a bytestring.
        #data = b"Hello, World!"
        data = bytes(message, 'utf-8')

        # When you publish a message, the client returns a future.
        api_future = self.publisher_client.publish(self.topic_path, data=data, **attrs)
        message_id = api_future.result()

        print(f"Published {data} to {self.topic_path}: {message_id}")

    # https://github.com/googleapis/python-pubsub/blob/master/samples/snippets/quickstart/sub.py
    def subscribe(self, callback, timeout=None):
        """Receives messages from a Pub/Sub subscription."""

        streaming_pull_future = self.subscriber_client.subscribe(
            self.subscription_path, callback=callback
        )
        print(f"Listening for messages on {self.subscription_path}..\n")

        try:
            # Calling result() on StreamingPullFuture keeps the main thread from
            # exiting while messages get processed in the callbacks.
            streaming_pull_future.result(timeout=timeout)
        except:  # noqa
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

        self.subscriber_client.close()
