import boto3
import json

s3_client = boto3.client('s3', region_name="us-west-2", endpoint_url="http://localhost:4572")
bucket_name = "movie-bucket"


def write_to_s3(messages, job_id):
    for message in messages:
        message = json.loads(message["Body"])
        s3_client.put_object(Body=json.dumps(message).encode('utf-8'),
                             Key=f"movies-{job_id}.json",
                             Bucket=bucket_name)