import uuid
import json
from datetime import datetime

from data_load_message import DataLoadMessage
from generate import generate_movies
from s3_operations import write_to_s3
from queueing import send_messages_to_queue, process_messages
from dynamo_operations import write_to_dynamo
from delete_item import delete_item


def main():

    # generate
    job_id = str(uuid.uuid4())
    print(job_id)
    movies_to_generate = 100
    movies_payloads = generate_movies(movies_to_generate)

    # send message to queue
    for movies_payload in movies_payloads:
        movie_id = str(uuid.uuid4())
        data_load_message = DataLoadMessage(job_id, movie_id, json.dumps(movies_payload))
        send_messages_to_queue(job_id, data_load_message.toJSON())

    # receive message
    # https://alexwlchan.net/2018/01/downloading-sqs-queues/
    messages = process_messages(movies_to_generate)

    print(messages)
    # write to database
    write_to_dynamo(job_id, messages)

    # write payload to s3
    write_to_s3(messages, job_id)


    # delete a job from the table
    # delete_item(job_table, table_name)


if __name__ == '__main__':
    main()
    print('\nall done thanks')
