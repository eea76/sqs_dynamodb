import uuid
import json
from datetime import datetime

from data_load_message import DataLoadMessage
from generate import generate_movies
from s3_operations import write_to_s3
from queueing import enqueue_message, dequeue_message, delete_message
from write_to_dynamo import write_to_dynamo
from delete_item import delete_item


def main():

    # generate
    job_id = str(uuid.uuid4())
    movies_to_generate = 10
    movies_payloads = generate_movies(movies_to_generate)

    # send message to queue
    for movies_payload in movies_payloads:
        movie_id = str(uuid.uuid4())
        data_load_message = DataLoadMessage(job_id, movie_id, json.dumps(movies_payload))
        enqueue_message(job_id, data_load_message.toJSON())

    # receive message
    messages = dequeue_message()

    # write to database
    write_to_dynamo(job_id, messages)

    # write payload to s3
    write_to_s3(messages, job_id)

    # delete message from queue
    # todo: only do this if we've verified the messages made it into the db and the bucket
    delete_message(messages, job_id)

    # delete a job from the table
    # delete_item(job_table, table_name)


if __name__ == '__main__':
    main()
    print('all done thanks')
