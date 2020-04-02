### In an effort to learn how various AWS services work, I've written a small project that
- generates data (movie objects with the following attributes):
    - title
    - year of release
    - actor
    - director
- sends that data to an AWS SQS queue
- receives that data in the form of a queue message
- writes that message to a DynamoDB table
- writes the generated payload to an s3 bucket
#### This project was made with Python 3.7. No guarantees with any version of Python 2.

---

### This section is a step-by-step explanation of how to get this working
### Project Setup

#### Install AWS CLI
- Do you have AWS CLI installed?
- Type `aws` in the command line. If you see `command not found`, you don't have it.
    - run `aws --version` to make sure you have version 2 (version 1 won't work with this project)
- Get it here: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
- Then run `aws configure` and provide your AWS Access Key, AWS Secret Access Key, and region
- If you don't know where this info is stored, you'll have to retrieve/generate it from IAM in the AWS console: https://console.aws.amazon.com/iam

#### Docker and virtual environment
- Because this project utilizes the python package `localstack` (which creates local AWS resources), it also requires Docker: https://www.docker.com/
- Download and install the Docker client (explaining Docker goes beyond the scope of this tiny project; resources online are plentiful. It's part of this containerization idea which I really don't know much about yet)
- After starting Docker (it just runs in the background; see the menu bar icon to verify), initialize a virtualenv. An IDE like PyCharm/IntelliJ can automatically create a virtualenv, or to create one manually do `virtualenv -p python3 venv` while in the project root.
- Activate the virtualenv if the IDE hasn't done so already: `source venv/bin/activate`
- Install requirements: `pip3 install -r requirements.txt`


#### Create Resources
- We're using localstack so we can do all this locally; otherwise we would need to create resources in AWS, which would incur usage costs.
- Run `localstack start`
- Once everything is Ready, open localstack_setup.sh, which is a list of shell script commands. If your IDE supports .sh scripts you can just run this file, or copy each command from it and run them individually in your terminal
    - `aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"`
    - `aws --endpoint-url=http://localhost:4569 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null`
    - `aws --endpoint-url=http://localhost:4572 s3 mb s3://movie-bucket`
- What did these commands do?
    - We created a SQS Queue (specifically a FIFO queue: First-In First-Out) called `movie-load.fifo`, which is where we'll be sending and receiving messages (ie the generated movies)
    - We created a NoSQL DynamoDB table named `movie-job-information`, with job_id as the table's primary key
    - We created an s3 Bucket named `movie-bucket`. JSON from the generated movies will ultimately end up here


---

#### Run program
- Just do `python3 main.py` in your terminal and if localstack is running and all the local AWS resources were created, the script should run and print out progress messages until the program completes. Below is a step-by-step explanation of every step in the process
- Alternatively you can specify the script path in PyCharm/IntelliJ as `/main.py` and then run the program from there. Way easier than using the terminal.


#### This program runs fairly quickly and there isn't much in the way of feedback, but this project is meant to serve as an illustration of how AWS services work together. Therefore in this context inspecting the code and learning how the pieces are connected will ultimately be more useful than what the program produces (a json file of a bunch of fake movies sitting on your hard drive 😉)

---

##### Generate
- A job_id is created
- Specify the number of movies to generate (please don't do anything insane like 1000; it will blow up the database and could also potentially screw up SQS - obviously AWS can handle payloads of messages much greater than 1000, but this project probably cannot until I build in some checks and safeguards)
- The `generate_movies` method creates the number of movies specified (one dictionary per movie) and returns them in a list called `movies_payloads`

##### Send the movies to the queue
- For each movies_payload in movies_payloads:
    - a unique movie_id is created
    - an instance of the DataLoadMessage object is created (`data_load_message`)
    - the `send_messages_to_queue` function is called

##### Receive messages from the queue
- Much of this function was taken from here: https://alexwlchan.net/2018/01/downloading-sqs-queues/
- Call the `process_messages` function
- Receive messages from the specified queue (up to 10 messages can be retrieved at a time)
    - If more than 10 are in the queue, we pull 10 at a time until it's empty
- Return `messages` list, which contains all processed messages (aka all messages that have been received and deleted from the queue)


##### Write the message to DynamoDB
- Call the `write_to_dynamo` function
    - Assign `dynamo_item` to an instance of DynamoItem
    - Writes this item to the table
    - Items cannot be more than 400kb each (Dynamo limitation).
        - To do: figure out how to break up items that are > 400kb
            - How?
                - No idea yet


##### Write the message payload to an S3 bucket
- We can write the generated data to an S3 bucket as json
- Calls the `write_to_s3` function
    - Put the `bucket_message` onto s3 in a json file with the naming convention `[job_id].json`

---

##### Next steps
- Implement dead-letter queues in the case of a message failure
    - Figure it out
- Long-polling support
    - Should not be too hard
- Change the data generation method to a generator (aka use `yield` instead of `return`). This will process the data as it's being generated instead of the end result all at once
- Break up objects > 400kb so a job of any size can be written to Dynamo

##### Why use queues at all and not simply write the generated data directly to the database?
- Ultimately this is the question I wanted to answer when creating this project, so I'm still learning about this concept.
- Queues act as a buffer between the data producer and the data consumer
- If the producer produces data faster than the consumer can consume it, you need a queue to moderate the flow of data
- Queues also provide the ability to scale easily.
- Also incidentally, a queue message contains more data than the generated payload that was sent to it, so more metrics are available to the consumer of the data (timestamps, success/failure rates, etc)
---
### Optional stuff with the `aws` cli

#### Since this project keeps all created resources safely on your local machine (and therefore free from AWS usage costs), we don't have the benefit of the AWS web console, which is a GUI that lets you perform all kinds of individual tasks with AWS resources. Locally, we have to do this using the command line
##### Dynamo
- List tables:
    - `aws --endpoint-url=http://localhost:4569 dynamodb list-tables`
- To see the messages that made it from the queue to the Dynamo table (as well as seeing other table data), you can perform a scan operation in the console:
    - `aws dynamodb scan --table-name movie-job-information --endpoint-url=http://localhost:4569`
- Alternatively you can output the result to a JSON file which will probably be easier to read (this can be a massive process depending on the table size):
    - `aws dynamodb scan --table-name movie-job-information --endpoint-url=http://localhost:4569 > table_scan.json`

##### S3
- List buckets
    - `aws --endpoint-url=http://localhost:4572 s3 ls`
- To obtain a list of all the files in the bucket:
    - `aws s3 ls s3://movie-bucket --endpoint-url=http://localhost:4572`
- To download a specific file from the bucket and see what the generated payload looks like:
    - replace `[desired job_id]` with the job_id
    - this downloads the file to the current directory (`.`):
    - `aws s3 mv s3://movie-bucket/[desired job_id].json . --endpoint-url=http://localhost:4572`

##### Queues
- List queues:
    - `aws sqs list-queues --endpoint-url=http://localhost:4576`
- List messages in a queue (per the thorough SQS documentation, running this command may return an empty response even if you know for certain the queue is not empty; better to run this command programmatically)
    - `aws sqs receive-message --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576 --max-number-of-messages 10`
- You can purge the queue as a last ditch effort to ensure it's completely empty. A queue will typically be empty approx 60 seconds after the command is run:
    - `aws sqs purge-queue --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576`
