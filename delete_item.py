def delete_item(table, table_name):
    job_id = input("enter the job_id to delete: ")

    print('attempting to delete')

    try:
        response = table.delete_item(
            Key={
                'job_id': job_id,
            }
        )
    except:
        print("item could not be deleted")
    else:
        print(response)
        print(f'Job {job_id} has been deleted from {table_name}.')
