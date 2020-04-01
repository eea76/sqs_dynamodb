import boto3
from datetime import datetime

table_name = "movie-job-information"


def item_to_dict(item):
    i = vars(item) if not isinstance(item, dict) else item
    for key, val in i.items():
        if type(val) == set:
            i[key] = val
        elif type(val) == dict or "to_dynamo_object" in dir(val):
            i[key] = item_to_dict(val)
    return i


class DynamoItem:
    def __init__(self, job_id, message_body):
        self.job_id = job_id
        self.started_on = str(datetime.utcnow())
        self.message_body = message_body

    def to_dynamo_object(self):
        return item_to_dict(self)


def write_to_dynamo(table_name, job_id, messages):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:4569")
    dynamo_item = DynamoItem(job_id, messages)
    dynamo_item = dynamo_item.to_dynamo_object()
    job_table = dynamodb.Table(table_name)

    # todo: if an item is > 400kb, break the item up so its pieces are < 400kb (how the hell do I do that)
    # todo: figure it out
    # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html#limits-items
    job_table.put_item(Item=dynamo_item)
