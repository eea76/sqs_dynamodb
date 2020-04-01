import uuid
import json

from data_load_message import DataLoadMessage
from generate import generate_movies
from s3_operations import write_to_s3, download_json_from_s3, download_all_s3_contents
from queueing import send_messages_to_queue, process_messages
from dynamo_operations import write_to_dynamo


def main():

    # generate
    job_id = str(uuid.uuid4())
    print(f"\njob id: {job_id}")
    movies_to_generate = 1
    movies_payloads = generate_movies(movies_to_generate)
    print(f"movies generated: {movies_to_generate}")

    # send message to queue
    for movies_payload in movies_payloads:
        movie_id = str(uuid.uuid4())
        data_load_message = DataLoadMessage(job_id, movie_id, json.dumps(movies_payload))
        send_messages_to_queue(job_id, data_load_message.toJSON())

    # receive message
    received_messages = process_messages(movies_to_generate)

    # write to database
    # write_to_dynamo(job_id, received_messages)

    # write payload to s3
    write_to_s3(received_messages, job_id)

    # download this job from s3
    download_json_from_s3(job_id)

    # this operation is potentially foolish
    download_all_s3_contents()


if __name__ == '__main__':
    main()
    print('\nall done thanks')
