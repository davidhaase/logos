import boto3
import botocore

class S3File():
    def __init__(self, bucket_name, key):
        self.bucket_name = bucket_name
        self.key = key
        self.resource = boto3.resource('s3')
        self.client =  boto3.client('s3')

    def copy_from_S3_to(self, target_location):
        try:
            self.resource.Bucket(self.bucket_name).download_file(self.key, target_location)
        
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def crawl_models(self, head):
        path_list = {}

        kwargs = {'Bucket':self.bucket_name, 'Prefix': head}
        response = self.client.list_objects(**kwargs)
        for obj in response['Contents']:
            params = {}
            key = obj['Key']
            dirs = key.split('/')
            if (len(dirs)>6):
                if dirs[2] not in path_list:
                    path_list[dirs[2]] = {}
                    # print(f'Adding {dirs[2]}')
                
                if dirs[3] not in path_list[dirs[2]]:
                    path_list[dirs[2]][dirs[3]] = {}
                    # print(f'Adding {dirs[3]}')
                
                if dirs[4] not in path_list[dirs[2]][dirs[3]]:
                    path_list[dirs[2]][dirs[3]][dirs[4]] = []
                    # print(f'Adding {dirs[4]}')

                if dirs[5] not in path_list[dirs[2]][dirs[3]][dirs[4]]:
                    path_list[dirs[2]][dirs[3]][dirs[4]].append(dirs[5])
                    # print(f'Adding {dirs[5]}')

        return path_list

            
            





def seconds_to_string(total_seconds):
    seconds = total_seconds % 60
    minutes = total_seconds // 60
    if minutes > 0:
        hours = minutes // 60
        if hours > 0:
            days = hours // 24
            if days > 0:
                return f'{days}d {hours}h {minutes}m {seconds}s'
            else:
                return f'{hours}h {minutes}m {seconds}s'

        else:
            return f'{minutes}m {seconds}s'

    else:
        return f'{seconds}s'
