import json
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential

def eventhub_save(eventhub_endpoint: str,eventhub_name: str, payload: dict):

    credential = DefaultAzureCredential()

    # instantiate a producer client to send messages to the event hub
    producer = EventHubProducerClient(
        fully_qualified_namespace=eventhub_endpoint,
        eventhub_name=eventhub_name,
        credential=credential
    )
    # send a single event to the event hub
    with producer:
        batch = producer.create_batch()
        batch.add(EventData(json.dumps(payload)))
        producer.send_batch(batch)
      
# example usage
# eventhub_save(result)