import boto3
import botocore

class S3File():
    def __init__(self, bucket_name, key):
        self.bucket_name = bucket_name
        self.key = key
        self.s3 = boto3.resource('s3')

    def copy_from_S3_to(self, target_location):
        try:
            self.s3.Bucket(self.bucket_name).download_file(self.key, target_location)
        
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


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
