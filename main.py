import boto3
import uuid
import json
from datetime import datetime

from data_load_message import DataLoadMessage
from generate import generate_movies
from queueing import enqueue_message, dequeue_message, delete_message
from write_to_dynamo import write_to_dynamo
from delete_item import delete_item

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')

print(f"Queue URL: {queue.url}")
table_name = "movie-job-information"
print(f"Table name: {table_name}")


def main():

    # generate
    job_id = str(uuid.uuid4())
    movies_to_generate = 2
    movies_payloads = generate_movies(movies_to_generate)

    # send message to queue
    for movies_payload in movies_payloads:
        movie_id = str(uuid.uuid4())
        data_load_message = DataLoadMessage(job_id, movie_id, json.dumps(movies_payload))
        enqueue_message(sqs_client, queue, job_id, data_load_message.toJSON())

    # receive message
    messages = dequeue_message(queue, sqs_client)

    # write to database
    write_to_dynamo(table_name, job_id, messages)

    # delete message from queue
    delete_message(queue, sqs_client, messages, job_id)

    # delete a job from the table
    # delete_item(job_table, table_name)



if __name__ == '__main__':
    main()
