import boto3
import uuid
import json

from data_load_message import DataLoadMessage
from generate import generate_movies
from dynamo_item import DynamoItem
from queueing import enqueue_message, dequeue_message, delete_message
from delete_item import delete_item

sqs = boto3.resource('sqs', region_name='us-west-2', endpoint_url="http://localhost:4576")
sqs_client = boto3.client('sqs', region_name="us-west-2", endpoint_url="http://localhost:4576")
queue = sqs.get_queue_by_name(QueueName='movie-load.fifo')

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:4569")
dynamodb_client = boto3.client('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:4569")

print(f"Queue URL: {queue.url}")
print("Table name: movie-job-information")


def main():

    # generate
    job_id = str(uuid.uuid4())
    movies_to_generate = 1
    movies_payloads = generate_movies(movies_to_generate)

    # send message to queue
    for movies_payload in movies_payloads:
        movie_id = str(uuid.uuid4())
        data_load_message = DataLoadMessage(job_id, movie_id, json.dumps(movies_payload))
        enqueue_message(sqs_client, queue, job_id, data_load_message.toJSON())

    # receive message
    messages = dequeue_message(queue, sqs_client)

    # write to database
    table_name = "movie-job-information"
    job_table = dynamodb.Table(table_name)

    dynamo_item = DynamoItem(job_id, messages)
    dynamo_item = dynamo_item.to_dynamo_object()
    # job_table.put_item(Item=dynamo_item)


    # delete message from queue
    delete_message(queue, sqs_client, messages, job_id)

    # update dynamo_item in db with completed time

    # delete a job from the table
    # delete_item(job_table, table_name)



if __name__ == '__main__':
    main()