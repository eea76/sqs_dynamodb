### In an effort to learn how various AWS services work, I've written a small project that
- generates data
- sends that data to an AWS SQS queue
- receives that data in the form of a message 
- writes that message to a DynamoDB table
- writes the generated payload to an s3 bucket
#### This project was made with Python 3.7. No guarantees with any version of Python 2.
##### Using Python I'll just generate some fake movies, which will have the following attributes:
- title
- year of release
- actor
- director

---

### This section is a step-by-step explanation of how to get this working
#### Project Setup
- Because this project utilizes the python package `localstack` (which creates local AWS resources), it also requires Docker: https://www.docker.com/
- Download and install the Docker client (explaining Docker goes beyond the scope of this tiny project; resources online are plentiful and I don't really understand it myself. It's part of this containerization initiative lately. Worth learning)
- After starting Docker (it just runs in the background; see the menu bar icon to verify), initialize a virtualenv. An IDE like PyCharm/IntelliJ can automatically create a virtualenv, or to create one manually do `virtualenv -p python3 venv` while in the project root.
- Activate the virtualenv if the IDE hasn't already: `source venv/bin/activate`
- Install requirements: `pip3 install -r requirements.txt`


#### Create Resources
- We're using localstack so we can do all this locally; otherwise we would need to create resources in AWS, which would incur usage costs. 
- Run `localstack start`
- Once everything is Ready, open localstack_setup.sh, which is a list of shell script commands. If your IDE supports .sh scripts you can just run this file, or copy the commands from it and run them individually in your terminal
    - `aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"`
        - This creates a SQS queue called movie-load, which is where we'll be sending and receiving messages (ie the generated movies)
    - `aws --endpoint-url=http://localhost:4569 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null`
        - This creates a table named movie-job-information, with job_id as the table's primary key
    - `aws --endpoint-url=http://localhost:4572 s3 mb s3://movie-bucket`
        - This creates a bucket called `movie-bucket`


---

#### Run program
##### Generate
- Initialize the SQS resource using boto3: get the queue named `movie-load.fifo`
- Create a job_id and specify the number of movies to generate
- The `generate_movies` method creates the number of movies specified (one dictionary per movie) and returns them in a list called `movies_payloads`

##### Send the movies to the queue
- For each movies_payload in movies_payloads: 
    - create a movie_id
    - create an instance of the DataLoadMessage object (`data_load_message`), which takes as parameters:
        - the job_id
        - the movie_id
        - a json dump of the movies_payload
    - call the `send_messages_to_queue` function, which sends the message to the queue

##### Receive messages from the queue
- Much of this function was taken from here: https://alexwlchan.net/2018/01/downloading-sqs-queues/
- Call the `process_messages` function and pass the `number_of_movies` argument as a parameter (it's used in the function to do progress-related calculations)
- Receive messages from the specified queue (up to 10 messages can be retrieved at once)
    - iterate through the response object and add its `Messages` to the `messages` list
    - if `Messages` does not exist in the `response` object that means all the messages have been deleted, and the while loop will be broken and the function will return
    - creates a list called `entries` consisting of up to 10 dictionaries each with a MessageID/ReceiptHandle pair
    - all the messages in the `entries` list have been put in the `messages` list, so we can safely delete these from the queue
        - call the `delete_message_batch` method, and delete the messages whose MessageIds currently are in `entries`
    - return to to the top of the loop and repeat this again until no more messages can be retrieved from the queue
- Return `messages` list, which contains all processed messages (aka all messages that have been received and deleted from the queue)


##### Write the message to DynamoDB
- call the `write_to_dynamo` function
    - assign `dynamo_item` to an instance of DynamoItem, which takes job_id and the messages that were returned from `process_messages`
        - sets the started_on, job_id, and message_body
    - writes this item to the table
    - items cannot be more than 400kb each (Dynamo limitation).
    

##### Write the message payload to an S3 bucket
- We can write the generated data to an S3 bucket as json
- Calls the `write_to_s3` function and passes the received_messages (which were returned from the `process_message` function, remember), and the job_id
- Loops through the messages, and for each message (which is its own dict), add its `Body`'s value to the `bucket_message` list
- Put the `bucket_message` onto s3 in a json file with the naming convention `movies-[job_id].json`
  
---
#### Optional stuff
##### Query the database
- To see the messages that made it from the queue to the Dynamo table (as well as seeing other table data), you can perform a scan operation in the console:
    - `aws dynamodb scan --table-name movie-job-information --endpoint-url=http://localhost:4569`
- Alternatively you can output the result to a JSON file which will probably be easier to read:
    - `aws dynamodb scan --table-name movie-job-information --endpoint-url=http://localhost:4569 > table_scan.json`

##### Inspect the bucket in s3
- To obtain a list of all the files in the bucket:
    - `aws s3 ls s3://movie-bucket --endpoint-url=http://localhost:4572`
- To download a specific file from the bucket and see what the generated payload looks like:
    - replace `[desired job_id]` with the job_id
    - this downloads the file to the current directory (`.`):
    - `aws s3 mv s3://movie-bucket/movies-[desired job_id].json . --endpoint-url=http://localhost:4572`
    
##### Purge the queue
- You can purge the queue as a last ditch effort to ensure it's completely empty. A queue will typically be empty approx 60 seconds after the command is run:
    - `aws sqs purge-queue --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576`