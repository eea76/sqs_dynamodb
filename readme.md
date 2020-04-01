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
- First make sure you have the aws cli. Type `aws` in your terminal and if you get `command not found`, you'll have to install the cli from here: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
- Because this project utilizes the python package `localstack` (which creates local AWS resources), it also requires Docker: https://www.docker.com/
- Download and install the Docker client (explaining Docker goes beyond the scope of this tiny project; resources online are plentiful and I don't really understand it myself. It's part of this containerization initiative lately. Worth learning)
- After starting Docker (it just runs in the background; see the menu bar icon to verify), initialize a virtualenv. An IDE like PyCharm/IntelliJ can automatically create a virtualenv, or to create one manually do `virtualenv -p python3 venv` while in the project root.
- Activate the virtualenv if the IDE hasn't done so already: `source venv/bin/activate`
- Install requirements: `pip3 install -r requirements.txt`


#### Create Resources
- We're using localstack so we can do all this locally; otherwise we would need to create resources in AWS, which would incur usage costs. 
- Run `localstack start`
- Once everything is Ready, open localstack_setup.sh, which is a list of shell script commands. If your IDE supports .sh scripts you can just run this file, or copy each uncommented command from it and run them individually in your terminal
    - `aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"`
        - This creates a SQS queue called movie-load, which is where we'll be sending and receiving messages (ie the generated movies)
    - `aws --endpoint-url=http://localhost:4569 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null`
        - This creates a table named movie-job-information, with job_id as the table's primary key
    - `aws --endpoint-url=http://localhost:4572 s3 mb s3://movie-bucket`
        - This creates a bucket called `movie-bucket`


---

#### Run program
- Just do `python3 main.py` in your terminal and if localstack is running and all the local AWS resources were created, the script should run and print out progress messages until the program completes. Below is a step-by-step explanation of every step in the process
- Alternatively you can specify the script path in PyCharm/IntelliJ as `/main.py` and then run the program from there. Way easier than using the terminal.

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
- Call the `process_messages` function
- Receive messages from the specified queue (up to 10 messages can be retrieved at a time)
- Return `messages` list, which contains all processed messages (aka all messages that have been received and deleted from the queue)


##### Write the message to DynamoDB
- call the `write_to_dynamo` function
    - assign `dynamo_item` to an instance of DynamoItem, which takes job_id and the messages that were returned from `process_messages`
    - writes this item to the table
    - items cannot be more than 400kb each (Dynamo limitation).
        - to do: figure out how to break up items that are > 400kb
            - how?
                - no idea yet
    

##### Write the message payload to an S3 bucket
- We can write the generated data to an S3 bucket as json
- Calls the `write_to_s3` function
    - Put the `bucket_message` onto s3 in a json file with the naming convention `[job_id].json`

##### Next steps: Implement dead-letter queues in the case of message failure
- Figure it out
  
---
#3## Optional stuff with the `aws` cli

#### Since this project keeps all created resources safely on your local machine (and therefore free of AWS usage costs), we don't have the benefit of the AWS web console, which is a GUI that lets you perform all kinds of individual tasks with AWS resources. Locally, we have to do this using the command line
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
    - `aws s3 mv s3://movie-bucket/[desired job_id].json . --endpoint-url=http://localhost:4572`
    
##### Purge the queue
- You can purge the queue as a last ditch effort to ensure it's completely empty. A queue will typically be empty approx 60 seconds after the command is run:
    - `aws sqs purge-queue --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576`