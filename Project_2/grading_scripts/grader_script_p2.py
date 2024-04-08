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
import re

class aws_grader():
    def __init__(self, access_key, secret_key, buckets, lambda_names, region):

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
        self.in_bucket_name = buckets[0]
        self.out_bucket_name = buckets[4]
        self.buckets = buckets
        self.lambda_names = lambda_names
        self.test_result = {}

    def validate_lambda_exists_each(self, name, TC_num):
        try:
            response = self.lambda_function.get_function(
            FunctionName=name
            )
            print(f"Lambda function {name} HTTPStatusCode {response['ResponseMetadata']['HTTPStatusCode']}")
            self.test_result[TC_num] = "PASS"
        except self.lambda_function.exceptions.ResourceNotFoundException as e:
            print(f"Error {e}")
            self.test_result[TC_num] = "FAIL"
        print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
    def validate_lambda_exists(self, TC_num):
        self.validate_lambda_exists_each("video-splitting",TC_num+"_a")
        self.validate_lambda_exists_each("motion-detection", TC_num + "_b")
        self.validate_lambda_exists_each("face-extraction", TC_num + "_c")
        self.validate_lambda_exists_each("face-recognition", TC_num + "_d")

    def validate_s3_subfolders_each(self, buckets, in_objects, TC_num):
        for num, bucket in enumerate(buckets[1:]):
            print(f"\nComparing buckets {buckets[0]} and {bucket} ...")
            TC_num_sub = TC_num+"_"+str(chr(97+num))
            self.test_result[TC_num_sub] = "PASS"
            for obj in in_objects['Contents']:
                folder_name = obj['Key'].rsplit('.', 1)[0]
                out_objects = self.s3.list_objects_v2(Bucket=bucket, Prefix=folder_name, Delimiter='/')
                if out_objects['KeyCount'] == 1 or out_objects['KeyCount'] == 11:
                    folder_name = out_objects['CommonPrefixes'][0]['Prefix'].rsplit("/")[0]
                    prefix_name = out_objects['Prefix']
                    if folder_name == prefix_name:
                        print(f"{prefix_name} matches with {folder_name}")
                else:
                    prefix_name = out_objects['Prefix']
                    self.test_result[TC_num_sub] = "FAIL"
                    print(f"NO folder named {prefix_name}\nExiting this test case... ")
                    # print(f"DEBUG :: {out_objects}")
                    break
            print(f"Test status of {TC_num_sub} : {self.test_result[TC_num_sub]}")

    def validate_s3_subfolders(self, TC_num):
        in_objects = self.s3.list_objects_v2(Bucket=self.in_bucket_name)
        if in_objects['KeyCount']==0:
            print(f"Empty bucket {self.in_bucket_name}")
            print(f"Test status of {TC_num} : {self.test_result[TC_num]}")
            return
        self.validate_s3_subfolders_each(buckets,in_objects,TC_num)

    def check_non_empty_folders(self, bucket_num, TC_num):
        bucket = self.s3_resources.Bucket(self.buckets[bucket_num])
        TC_num_sub = TC_num + "_" + str(chr(96 + bucket_num))
        self.test_result[TC_num_sub] = "FAIL"
        try:
            objects = list(bucket.objects.all())
            print(f"{self.buckets[bucket_num]} contains {len(objects)} objects")
            if bucket_num==4:
                prefix_pattern = r"test_\d{2}/[oO]utput-\d{2}.txt"
            else:
                prefix_pattern = r"test_\d{2}/[oO]utput-\d{2}.(jpg|jpeg)"
            count = self.count_values_with_prefix(objects, prefix_pattern)
            # print(f"DEBUG :: Bucket {stage_1_bucket} has {count} objects that matches the pattern")
            if count >= 100:
                self.test_result[TC_num_sub] = "PASS"
        except ClientError:
            print(f"Couldn't get objects for bucket {bucket.name}")
            raise
        print(f"Test status of {TC_num_sub} : {self.test_result[TC_num_sub]}\n")

    def count_values_with_prefix(self,objects, prefix_pattern):
        count = 0
        for o in objects:
            if re.match(prefix_pattern, o.key):
                # print(f"DEBUG :: Object key '{o.key}' follows the pattern '{prefix_pattern}'")
                count += 1
            else:
                print(f"Object key '{o.key}' does NOT follows the pattern '{prefix_pattern}'")

        return count
    def validate_s3_output_objects(self, TC_num):
        in_bucket = self.s3_resources.Bucket(self.buckets[0])
        try:
            in_objects = list(in_bucket.objects.all())
            print(f"{self.buckets[0]} contains {len(in_objects)} objects")

            # Check if all the folders of stage-1, stage-2, stage-3, and output bucket are non-empty
            self.check_non_empty_folders(1,TC_num=TC_num)
            self.check_non_empty_folders(2,TC_num=TC_num)
            self.check_non_empty_folders(3,TC_num=TC_num)
            self.check_non_empty_folders(4,TC_num=TC_num)

        except ClientError:
            print(f"Couldn't get objects for bucket {in_bucket.name}")
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

    def check_lambda_concurrency_each(self,functionName, TC_num,subcase):
        TC_num_sub = TC_num + "_" + str(chr(96 + subcase))

        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'testConcurrency',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Lambda',
                            'MetricName': 'ConcurrentExecutions',
                            'FunctionName': functionName
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
            self.test_result[TC_num_sub] = "FAIL"
            print(f"Test status of {TC_num_sub} : {self.test_result[TC_num_sub]}")
            return
        if max(values) < 5:
            self.test_result[TC_num_sub] = "FAIL"
        else:
            self.test_result[TC_num_sub] = "PASS"
        print(f"Test status of {TC_num_sub} : {self.test_result[TC_num_sub]}")

    def check_lambda_concurrency(self,TC_num):
        self.check_lambda_concurrency_each('video-splitting', TC_num,1)
        self.check_lambda_concurrency_each('motion-detection', TC_num,2)
        self.check_lambda_concurrency_each('face-extraction', TC_num,3)
        self.check_lambda_concurrency_each('face-recognition', TC_num,4)

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

    def validate_s3_buckets_initial_each(self, bucket_num, TC_num):
        TC_num_sub = TC_num + "_" + str(chr(97 + bucket_num))
        isExist = self.check_bucket_exist(self.buckets[bucket_num])
        self.test_result[TC_num_sub] = "FAIL"
        if isExist:
            obj_count = self.count_bucket_objects(self.buckets[bucket_num])
            print(f"S3 Bucket:{self.buckets[bucket_num]} has {obj_count} object(s)")
            if obj_count == 0:
                self.test_result[TC_num_sub] = "PASS"
            else:
                self.test_result[TC_num_sub] = "FAIL"
        print(f"Test status of {TC_num_sub} : {self.test_result[TC_num_sub]}\n")

    def validate_s3_buckets_initial(self, TC_num):
        print(" - Run this BEFORE the workload generator client starts. Press Ctrl^C to exit.")
        print(" - WARN: If there are objects in the S3 buckets; they will be deleted")
        print(" ---------------------------------------------------------")

        for i in range(len(self.buckets)):
            self.validate_s3_buckets_initial_each(bucket_num=i, TC_num=TC_num)

    def display_menu(self):
        print("\n")
        print("=============================================================================")
        print("======== Welcome to CSE546 Cloud Computing AWS Console ======================")
        print("=============================================================================")
        print(f"IAM ACCESS KEY ID: {self.access_key}")
        print(f"IAM SECRET ACCESS KEY: {self.secret_key}")
        print("=============================================================================")
        print("1 - Validate all Lambda functions")
        print("2 - Validate S3 Buckets names and initial states")
        print("3 - Validate S3 buckets subfolders")
        print("4 - Validate S3 buckets objects")
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
    parser.add_argument('--asu_id', type=str, help='10-digit ASU ID')

    args = parser.parse_args()

    access_key = args.access_key
    secret_key = args.secret_key
    asu_id = args.asu_id
    input_bucket = asu_id+"-input"
    output_bucket = asu_id+"-output"
    stage_1_bucket = asu_id+"-stage-1"
    stage_2_bucket = asu_id + "-stage-2"
    stage_3_bucket = asu_id + "-stage-3"
    buckets = [input_bucket, stage_1_bucket, stage_2_bucket, stage_3_bucket, output_bucket]
    lambda_names = ["video-splitting", "motion-detection","face-extraction", "face-recognition"]
    region = 'us-east-1'

    aws_obj = aws_grader(access_key, secret_key, buckets, lambda_names,region)
    aws_obj.main()
