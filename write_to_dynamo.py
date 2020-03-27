import boto3

from dynamo_item import DynamoItem

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:4569")


def write_to_dynamo(table_name, job_id, messages):
    dynamo_item = DynamoItem(job_id, messages)
    dynamo_item = dynamo_item.to_dynamo_object()
    job_table = dynamodb.Table(table_name)
    job_table.put_item(Item=dynamo_item)