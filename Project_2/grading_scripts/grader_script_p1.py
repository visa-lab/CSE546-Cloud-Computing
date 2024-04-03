__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import pdb
import time
import botocore
import argparse
import textwrap
import boto3
from boto3 import client as boto3_client
from botocore.exceptions import ClientError
from datetime import datetime,timezone,timedelta

class aws_grader():
    def __init__(self, access_key, secret_key, input_bucket, output_bucket, lambda_name, region):

        self.access_key = access_key
        self.secret_key  = secret_key
        self.region = region
        self.s3 = boto3_client('s3', aws_access_key_id=self.access_key,
                          aws_secret_access_key=self.secret_key, region_name=region)
        self.cloudwatch = boto3_client('cloudwatch', aws_access_key_id=self.access_key,
                          aws_secret_access_key=self.secret_key, region_name=region)
        self.iam_session = boto3.Session(aws_access_key_id=self.access_key,
                                         aws_secret_access_key=self.secret_key)
        self.s3_resources = self.iam_session.resource('s3', region)
        self.lambda_function = boto3_client('lambda', aws_access_key_id=self.access_key,
                               aws_secret_access_key=self.secret_key, region_name=region)
        self.in_bucket_name = input_bucket
        self.out_bucket_name = output_bucket
        self.lambda_name = lambda_name
        self.test_result = {}

    def validate_lambda_exists(self, TC_num):
        try:
            response = self.lambda_function.get_function(
            FunctionName=self.lambda_name
            )
            print(f"Lambda function {self.lambda_name} HTTPStatusCode {response['ResponseMetadata']['HTTPStatusCode']}")
            self.test_result[TC_num] = "PASS"
        except self.lambda_function.exceptions.ResourceNotFoundException as e:
            print(f"Error {e}")
            self.test_result[TC_num] = "FAIL"
        print(f"Test status of {TC_num} : {self.test_result[TC_num]}")

    def validate_s3_subfolders(self, TC_num):
        in_objects = self.s3.list_objects_v2(Bucket=self.in_bucket_name)
        if in_objects['KeyCount']==0:
            self.test_result[TC_num] = "FAIL"
            print(f"Empty bucket {self.in_bucket_name}")
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
            return
        self.test_result[TC_num] = "PASS"
        for obj in in_objects['Contents']:
            folder_name = obj['Key'].rsplit('.',1)[0]
            out_objects = self.s3.list_objects_v2(Bucket=self.out_bucket_name, Prefix=folder_name, Delimiter='/')
            if out_objects['KeyCount'] == 1 or out_objects['KeyCount'] == 11:
                folder_name = out_objects['CommonPrefixes'][0]['Prefix'].rsplit("/")[0]
                prefix_name = out_objects['Prefix']
                if folder_name == prefix_name:
                    print(f"{prefix_name} matches with {folder_name}")
            else:
                prefix_name = out_objects['Prefix']
                self.test_result[TC_num] = "FAIL"
                print(f"NO folder named {prefix_name}")
                print(out_objects)
        print(f"Test status of {TC_num} : {self.test_result[TC_num]}")

    def validate_s3_output_objects(self, TC_num):
        bucket = self.s3_resources.Bucket(self.out_bucket_name)
        in_bucket = self.s3_resources.Bucket(self.in_bucket_name)

        try:
            objects = list(bucket.objects.all())
            print(f"Got {len(objects)} objects {[o.key for o in objects]} from bucket {bucket.name}")
            in_objects = list(in_bucket.objects.all())
            self.test_result[TC_num] = "PASS"

            for i,folder_n in enumerate(in_objects):
                if len(in_objects) * 10 == len(objects) or len(in_objects) * 11 == len(objects):
                    print(f"Number of objects matches for given input {folder_n}")
                    self.test_result[TC_num] = "PASS"
                else:
                    self.test_result[TC_num] = "FAIL"
                    break
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")


        except ClientError:
            print(f"Couldn't get objects for bucket {bucket.name}")
            raise
        else:
            return

    # You have to make sure to run the workload generator and it executes within 15 mins
    # of polling for cloudwatch metrics.
    def check_lambda_duration(self, TC_num):
        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'testDuration',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Lambda',
                            'MetricName': 'Duration'
                        },
                        'Period': 600,
                        'Stat': 'Average'
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=datetime.now().utcnow() - timedelta(minutes=15),
            EndTime=datetime.now().utcnow(),
            ScanBy='TimestampAscending'
        )
        print(response['MetricDataResults'][0]['Values'])
        values = response['MetricDataResults'][0]['Values']
        if not values:
            self.test_result[TC_num] = "FAIL"
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
            return
        if max(values) > 10000:
            self.test_result[TC_num] = "FAIL"
        else:
            self.test_result[TC_num] = "PASS"
        print(f"Test status of {TC_num} : {self.test_result[TC_num]}")

    def check_lambda_concurrency(self,TC_num):
        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'testConcurrency',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Lambda',
                            'MetricName': 'ConcurrentExecutions'
                        },
                        'Period': 600,
                        'Stat': 'Maximum'
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=datetime.now().utcnow() - timedelta(minutes=15),
            EndTime=datetime.now().utcnow(),
            ScanBy='TimestampAscending'
        )
        print(response['MetricDataResults'][0]['Values'])
        values = response['MetricDataResults'][0]['Values']
        if not values:
            self.test_result[TC_num] = "FAIL"
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
            return
        if max(values) < 5:
            self.test_result[TC_num] = "FAIL"
        else:
            self.test_result[TC_num] = "PASS"
        print(f"Test status of {TC_num} : {self.test_result[TC_num]}")

    def check_bucket_exist(self, bucket):
        if not bucket:
            print(f"Bucket name is empty!")
            return False
        try:
            self.s3.head_bucket(Bucket=bucket)
            print(f"Bucket {bucket} Exists!")
            return True
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                print("Private Bucket. Forbidden Access!")
                return True
            elif error_code == 404:
                print(f"Bucket {bucket} does Not Exist!")
                return False
    def empty_s3_bucket(self, bucket_name):
        bucket = self.s3_resources.Bucket(bucket_name)
        bucket.objects.all().delete()
        print(f"{bucket_name} S3 Bucket is now EMPTY !!")

    def count_bucket_objects(self, bucket_name):
        bucket = self.s3_resources.Bucket(bucket_name)
        count = 0
        for index in bucket.objects.all():
            count += 1
        #print(f"{bucket_name} S3 Bucket has {count} objects !!")
        return count

    def validate_s3_buckets_initial(self, TC_num):
        print(" - Run this BEFORE the workload generator client starts. Press Ctrl^C to exit.")
        print(" - WARN: If there are objects in the S3 buckets; they will be deleted")
        print(" ---------------------------------------------------------")

        in_isExist = self.check_bucket_exist(self.in_bucket_name)
        out_isExist = self.check_bucket_exist(self.out_bucket_name)

        if in_isExist:
            ip_obj_count = self.count_bucket_objects(self.in_bucket_name)
            print(f"S3 Input Bucket:{self.in_bucket_name} has {ip_obj_count} object(s)")
        if out_isExist:
            op_obj_count = self.count_bucket_objects(self.out_bucket_name)
            print(f"S3 Output Bucket:{self.out_bucket_name} has {op_obj_count} object(s)")

        if in_isExist and out_isExist and ip_obj_count==0 and op_obj_count==0:
            self.test_result[TC_num] = "PASS"
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
        else:
            self.test_result[TC_num] = "FAIL"
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")

    def display_menu(self):
        print("\n")
        print("=============================================================================")
        print("======== Welcome to CSE546 Cloud Computing AWS Console ======================")
        print("=============================================================================")
        print(f"IAM ACESS KEY ID: {self.access_key}")
        print(f"IAM SECRET ACCESS KEY: {self.secret_key}")
        print("=============================================================================")
        print("1 - Validate 1 Lambda function")
        print("2 - Validate S3 Buckets names and initial states")
        print("3 - Validate S3 output bucket subfolders")
        print("4 - Validate S3 output objects")
        print("5 - Check lambda average duration")
        print("6 - Check lambda concurrency")
        print("0 - Exit")
        print("Enter a choice:")
        choice = input()
        return choice

    def main(self):
        while(1):
            choice = self.display_menu()
            if int(choice) == 1:
                self.validate_lambda_exists('Test_1')
            elif int(choice) == 2:
                self.validate_s3_buckets_initial('Test_2')
            elif int(choice) == 3:
                self.validate_s3_subfolders('Test_3')
            elif int(choice) == 4:
                self.validate_s3_output_objects('Test_4')
            elif int(choice) == 5:
                self.check_lambda_duration('Test_5')
            elif int(choice) == 6:
                self.check_lambda_concurrency('Test_6')
            elif int(choice) == 0:
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grading Script')
    parser.add_argument('--access_key', type=str, help='ACCCESS KEY ID of the grading IAM user')
    parser.add_argument('--secret_key', type=str, help='SECRET KEY of the grading IAM user')
    parser.add_argument('--input_bucket', type=str, help='Name of the S3 Input Bucket')
    parser.add_argument('--output_bucket', type=str, help='Name of the S3 Output Bucket')
    parser.add_argument('--lambda_name', type=str, help="Name of the Lambda function")


    args = parser.parse_args()

    access_key = args.access_key
    secret_key   = args.secret_key
    input_bucket    = args.input_bucket
    output_bucket   = args.output_bucket
    lambda_name = args.lambda_name
    region = 'us-east-1'

    aws_obj = aws_grader(access_key, secret_key, input_bucket, output_bucket, lambda_name,region)
    aws_obj.main()
