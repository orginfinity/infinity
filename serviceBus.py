from time import sleep

from azure.servicebus import ServiceBusClient, ServiceBusMessage

from googleClient import getKeyValue
CONNECTION_STRING =  getKeyValue("sb-connection-string")
TOPIC_NAME = "infinityresearch"


def publish_message_to_topic(message_content):
    try:
        # Create a ServiceBusClient
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STRING, logging_enable=True)

        # Get a sender for the topic
        with servicebus_client:
            sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
            with sender:
                # Create and send a message
                message = ServiceBusMessage(message_content)
                sender.send_messages(message)
                print(f"Message sent to topic: {message_content}")
    except Exception as e:
        print(f"Error sending message: {e}")