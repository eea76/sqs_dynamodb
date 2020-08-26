# queue commands
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name movie-load.fifo --attributes "FifoQueue=true"

# create local table and list it
aws --endpoint-url=http://localhost:4566 dynamodb create-table --table-name movie-job-information --attribute-definitions AttributeName=job_id,AttributeType=S --key-schema AttributeName=job_id,KeyType=HASH --billing-mode PAY_PER_REQUEST &> /dev/null

aws --endpoint-url=http://localhost:4566 dynamodb list-tables

# create bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://movie-bucket







