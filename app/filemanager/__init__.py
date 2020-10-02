import boto3
import botocore

from flask import current_app

class FileManager:  
    def __init__(self):
        pass
    def print_hello(self):
        print(f'hello from {self.__repr__}')

class ModelFile(FileManager):  
    def __init__(self, data_dir, app_dir):
        self.data_dir = data_dir
        self.app_dir = app_dir

class LocalFile(ModelFile): 
    def __init__(self):
        super().__init__()

class AWSS3(ModelFile):
    def __init__(self, aws_s3_bucket):
        super().__init__()
        self.aws_s3_bucket = aws_s3_bucket
    
    def print_hello(self):
        print(f'hello from AWSS3 {self.data_dir} {self.app_dir} {self.aws_s3_bucket}')

class GoogleCloud(ModelFile):
    def __init__(self):
        super().__init__()

file_config = {
    'local': LocalFile(),
    'aws_s3': AWSS3(),
    'google_cloud': GoogleCloud(),

    'default': AWSS3()
}

def create_file(file_config_type):
    File = file_config[file_config_type]

    return File