# queue commands
aws --endpoint-url=http://localhost:4576 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"
# aws sqs list-queues --endpoint-url=http://localhost:4576

# create local table and list it
aws --endpoint-url=http://localhost:4569 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null
aws --endpoint-url=http://localhost:4569 dynamodb list-tables

# create bucket
aws --endpoint-url=http://localhost:4572 s3 mb s3://movie-bucket
# aws -- endpoint-url=http://localhost:4572 s3 ls

# copy a file named movies.json to the local directory just to see what was generated (from the script through the queue and into the bucket)
# aws s3 mv s3://movie-bucket/movies.json . --endpoint-url=http://localhost:4572
# list contents of specified bucket
# aws s3 ls s3://movie-bucket --endpoint-url=http://localhost:4572

# does a scan of the table and pipes its contents to table_scan.json (this can be a massive process depending on the table size)
# aws dynamodb scan --table-name movie-job-information --endpoint-url=http://localhost:4569 > table_scan.json

# receives messages from the specified queue (aka reads queue contents)
# aws sqs receive-message --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576 --max-number-of-messages 10

# purges the messages from the specified queue
# aws sqs purge-queue --queue-url http://localhost:4576/queue/movie-load.fifo --endpoint-url=http://localhost:4576

007c8be6-8e37-435f-9a8c-37092cb56af1