### In an effort to learn how various AWS services work, I'm going to make a small project that:

#### Generates data
##### Using Python I'll just generate some fake movies, which will have the following attributes:
- title
- year of release
- actor
- director

#### Sends that data to a SQS message queue
- should it just be a dictionary of the generated data?
- one message = a job_id + one iteration of generated data?
- verify the queue contains the data

#### Pulls data from the queue
- after data has been generated and loaded onto the queue, pull it off
- delete the messages from the queue
- verify the queue is empty

#### I don't quite understand why we even need this queue if we're going to pull data off of it right after we've put it on. Why not just skip the queue entirely and deal directly with the data? This question proves I do not understand the purpose of queues. This is part of the reason I'm making this project in the first place: to understand the utility of QUEUES.

#### Writes data to a DynamoDB table
- to do

##### Optional but do it anyway: write generated JSON to an S3 bucket

---

### This section is a step-by-step explanation of how to get this working
#### Project Setup
- Because this project utilizes localstack, it also requires Docker: https://www.docker.com/
- Download and install the Docker client
- After starting Docker (it just runs in the background; see the menu bar icon to verify), initialize a virtualenv. An IDE like PyCharm/IntelliJ can automatically create a virtualenv, or to create one manually do `virtualenv -p python3 venv` while in the project root.
- Activate the virtualenv if the IDE hasn't already: `source venv/bin/activate`
- install requirements: `pip3 install -r requirements.txt`

#### Create Resources
- Run `localstack start`
- Once everything is Ready, open localstack_setup.sh
- In the console, run `aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"`
- This creates a SQS queue called movie-load, which is where we'll be sending and receiving messages (ie the generated movies)
- (DYNAMODB COMMAND)
- (S3 BUCKET COMMAND)

#### Run program
##### Generate
- Initialize the SQS resource using boto3: get the queue named `movie-load.fifo`
- Create a job_id and specify the number of movies to generate
- The `generate_movies` method creates the number of movies specified (one dictionary per movie) and returns them in a list called `movies_payloads`

##### Send the movies to the queue
- For each movies_payload in movies_payloads: 
    - create a movie_id
    - create an instance of the DataLoadMessage object (data_load_message), which takes as parameters:
        - the job_id
        - the movie_id
        - a json dump of the movies_payload
    - call the `enqueue_message` function, which sends the message to the queue

##### Receive messages from the queue
- call the `dequeue_message` function, which returns all the messages in the queue (up to 10)

##### Write the message to DynamoDB
- call the `write_to_dynamo` function
    - assign `dynamo_item` to an instance of DynamoItem, which takes job_id and the messages that were returned from dequeue_message
        - sets the started_on, job_id, and message_body
    - writes this item to the table
    
##### Delete the message from the queue
- after the message has been added to the dynamo table, call the `delete_item` method
- loop through the messages and if a message's MessageGroupId matches the job_id, delete it
- I'm not sure yet what gets deleted from the here: the entire message? 

