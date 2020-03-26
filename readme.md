### In an effort to learn how Amazon SQS works, I'm going to make a small project that:

#### Generates data
##### Using Python I'll just generate some fake movies:
- a title
- year of release
- actor
- director

##### Send that data to a SQS message queue
- should it just be a dictionary of the generated data?
- one message = a job_id + one iteration of generated data?
- verify the queue contains the data

##### Pull data from the queue
- after data has been generated and loaded onto the queue, pull it off
- loop through the dequeued messages and write them to a dynamodb table
- delete the messages from the queue
- verify the queue is empty

##### Optional but do it anyway: write generated JSON to an S3 bucket