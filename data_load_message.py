import json


class DataLoadMessage:
    def __init__(self,
                 job_id: str,
                 payload: str
                 ):
        self.job_id = job_id
        self.payload = payload

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)