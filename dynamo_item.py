from datetime import datetime


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
        self.completed_on = None

    def to_dynamo_object(self):
        return item_to_dict(self)