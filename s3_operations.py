import boto3
import json


s3_client = boto3.client('s3', region_name="us-west-2", endpoint_url="http://localhost:4572")
bucket_name = "movie-bucket"
bucket_object = s3_client.list_objects(Bucket=bucket_name)
bucket_contents = bucket_object.get("Contents")


def write_to_s3(messages, job_id):

    # creating a new list to put the messages is probably inefficient and silly but it works
    # todo: rewrite this as a list comprehension so we get better at writing list comprehensions
    bucket_message = []
    for message in messages:
        message = json.loads(message["Body"])
        bucket_message.append(message)

    s3_client.put_object(Body=json.dumps(bucket_message).encode('utf-8'),
                         Key=f"{job_id}.json",
                         Bucket=bucket_name)


def download_json_from_s3(job_id):
    s3_client.download_file(bucket_name, f"{job_id}.json", f"{job_id}.json")

    return True


def download_all_s3_contents():

    is_sure = input("This will download all the contents of the specified bucket, \n \
which could take awhile depending on the size of the bucket \n \
and the number of files. Are you sure you want to do this? y/n: ")
    if is_sure.lower() == "y":
        for filename_object in bucket_contents:
            filename = filename_object["Key"]
            s3_client.download_file(bucket_name, filename, filename)

    return True
