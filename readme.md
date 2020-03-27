### In an effort to learn how various AWS services work, I'm going to make a small project that generates data, sends that data to an AWS SQS queue, and then receives that data in the form of a message, and then writes that message to a DynamoDB table

##### Using Python I'll just generate some fake movies, which will have the following attributes:
- title
- year of release
- actor
- director

##### Optional: write the generated JSON to an S3 bucket

---

### This section is a step-by-step explanation of how to get this working
#### Project Setup
- Because this project utilizes the python package localstack (which creates local AWS resources), it also requires Docker: https://www.docker.com/
- Download and install the Docker client
- After starting Docker (it just runs in the background; see the menu bar icon to verify), initialize a virtualenv. An IDE like PyCharm/IntelliJ can automatically create a virtualenv, or to create one manually do `virtualenv -p python3 venv` while in the project root.
- Activate the virtualenv if the IDE hasn't already: `source venv/bin/activate`
- install requirements: `pip3 install -r requirements.txt`

#### Create Resources
- We're using localstack so we can do all this locally; otherwise we would need to create resources in AWS, which would incur usage costs. 
- Run `localstack start`
- Once everything is Ready, open localstack_setup.sh
- In the console, run `aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"`
- This creates a SQS queue called movie-load, which is where we'll be sending and receiving messages (ie the generated movies)
- To create the dynamo table, run `aws --endpoint-url=http://localhost:4569 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null`
- This creates a table named movie-job-information, with job_id as the table's primary key
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

