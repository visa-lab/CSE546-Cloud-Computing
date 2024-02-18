__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import pdb
import time
import json
import boto3
import httpx
import sys
import argparse
import textwrap

class aws_grader():
    def __init__(self, access_keyId, access_key, req_sqs, resp_sqs, in_bucket, out_bucket):

        self.iam_access_keyId       = access_keyId
        self.iam_secret_access_key  = access_key
        self.iam_session            = boto3.Session(aws_access_key_id = self.iam_access_keyId,
                                                    aws_secret_access_key = self.iam_secret_access_key)
        self.ec2_resources          = self.iam_session.resource('ec2', 'us-east-1')
        self.s3_resources           = self.iam_session.resource('s3', 'us-east-1')
        self.sqs_resources          = self.iam_session.resource('sqs', 'us-east-1')
        self.sqs_client             = self.iam_session.client('sqs', 'us-east-1')
        self.req_sqs_name           = req_sqs
        self.resp_sqs_name          = resp_sqs
        self.in_bucket_name         = in_bucket
        self.out_bucket_name        = out_bucket
        self.app_tier_tag           = "app-tier-instance"
        self.web_tier_tag           = "web-instance"

    def get_instance_details(self, tag, state):
        instances = self.ec2_resources.instances.filter(
            Filters=[
                {'Name': 'tag:Name', 'Values': [tag+"*"]},
                {'Name': 'instance-state-name', 'Values': [state]}
            ]
        )
        return len(list(instances))

    def validate_ec2_instance(self):
        web_instances = self.get_instance_details(self.web_tier_tag, 'running')
        app_instances = self.get_instance_details(self.app_tier_tag, 'running')
        print(f"Found {web_instances} web-tier instances in running state.")
        print(f"Found {app_instances} app-tier instanes in running state")

    def empty_s3_bucket(self, bucket_name):
        bucket = self.s3_resources.Bucket(bucket_name)
        bucket.objects.all().delete()
        print(f"{bucket_name} S3 Bucket is now EMPTY !!")

    def count_bucket_objects(self, bucket_name):
        bucket = self.s3_resources.Bucket(bucket_name)
        count  = 0
        for index in bucket.objects.all():
            count += 1
        #print(f"{bucket_name} S3 Bucket has {count} objects !!")
        return count

    def validate_s3_buckets(self):
        print(" - WARN: If there are objects in the S3 buckets; they will be deleted")
        print(" ---------------------------------------------------------")
        ip_obj_count = self.count_bucket_objects(self.in_bucket_name)
        op_obj_count = self.count_bucket_objects(self.out_bucket_name)

        print(f"S3 Input Bucket:{self.in_bucket_name} has {ip_obj_count} object(s)")
        print(f"S3 Output Bucket:{self.out_bucket_name} has {op_obj_count} object(s)")

        if ip_obj_count:
            self.empty_s3_bucket(self.in_bucket_name)
        if op_obj_count:
            self.empty_s3_bucket(self.out_bucket_name)

    def get_sqs_queue_length(self, sqs_queue_name):
        num_requests = self.sqs_client.get_queue_attributes(
                QueueUrl=sqs_queue_name,
                AttributeNames=['ApproximateNumberOfMessages'])
        return int(num_requests['Attributes']['ApproximateNumberOfMessages'])

    def validate_sqs_queues(self):
        print(" - The expectation is the both the Request and Response SQS should exist and be EMPTY")
        print(" - WARN: This will purge any messages available in the SQS")
        print(" ---------------------------------------------------------")

        try:
            req_sqs  = self.sqs_resources.get_queue_by_name(QueueName=self.req_sqs_name)
            resp_sqs = self.sqs_resources.get_queue_by_name(QueueName=self.resp_sqs_name)

            ip_queue_requests = self.get_sqs_queue_length(self.req_sqs_name)
            op_queue_response = self.get_sqs_queue_length(self.resp_sqs_name)

            print(f"SQS Request Queue:{self.req_sqs_name} has {ip_queue_requests} pending messages.")
            print(f"SQS Response Queue:{self.resp_sqs_name} has {op_queue_response} pending messages.")

            if ip_queue_requests:
                print(" - WARN: Purging the Requeust SQS. Waiting 60 seconds ..")
                self.sqs_client.purge_queue(QueueUrl=self.req_sqs_name)
                time.sleep(60)

            if op_queue_response:
                print(" - WARN: Purging the SQS. Waiitng 60 seconds ..")
                self.sqs_client.purge_queue(QueueUrl=self.resp_sqs_name)
                time.sleep(60)

        except Exception as ex:
            print(f"SQS Queues Error: {ex}. Please Check your AWS Account")

    def beautify_headers(self):

        column1 = " # of messages in SQS Request Queue "
        column2 = " # of messages in SQS Response Queue "
        column3 = " # of EC2 instances in running state "
        column4 = " # of objects in S3 Input Bucket "
        column5 = " # of objects in S3 Output Buket "

        column_width = 20
        wrapped_column1 = textwrap.fill(column1, column_width)
        wrapped_column2 = textwrap.fill(column2, column_width)
        wrapped_column3 = textwrap.fill(column3, column_width)
        wrapped_column4 = textwrap.fill(column4, column_width)
        wrapped_column5 = textwrap.fill(column5, column_width)
        lines1 = wrapped_column1.split('\n')
        lines2 = wrapped_column2.split('\n')
        lines3 = wrapped_column3.split('\n')
        lines4 = wrapped_column4.split('\n')
        lines5 = wrapped_column5.split('\n')

        print("-" * 114)
        for line1, line2, line3, line4, line5 in zip(lines1, lines2, lines3, lines4, lines5):
                print(f"| {line1.center(column_width)} | {line2.center(column_width)} | {line3.center(column_width)} | {line4.center(column_width)} | {line5.center(column_width)} |")

        print("-" *114)

    def validate_autoscaling(self):
        print(" - Run this BEFORE the workload generator client starts. Press Ctrl^C to exit.")
        print(" - The expectation is as follows:")
        print(" -- # of app tier instances should gradually scale and eventually reduce back to 0")
        print(" -- # of SQS messages should gradually increase and eventually reduce back to 0")
        self.beautify_headers()
        format_string = "| {:^20} | {:^20} | {:^20} | {:^20} | {:^20} |"

        while True:
            req_queue_count  = self.get_sqs_queue_length(self.req_sqs_name)
            resp_queue_count = self.get_sqs_queue_length(self.resp_sqs_name)
            num_instances    = self.get_instance_details(self.app_tier_tag, 'running')
            ip_obj_count     = self.count_bucket_objects(self.in_bucket_name)
            op_obj_count     = self.count_bucket_objects(self.out_bucket_name)
            print(format_string.format(req_queue_count, resp_queue_count, num_instances, ip_obj_count, op_obj_count))
            print("-" * 114)
            time.sleep(2)

    def display_menu(self):
        print("\n")
        print("=============================================================================")
        print("======== Welcome to CSE546 Cloud Computing AWS Console ======================")
        print("=============================================================================")
        print(f"IAM ACESS KEY ID: {self.iam_access_keyId}")
        print(f"IAM SECRET ACCESS KEY: {self.iam_secret_access_key}")
        print("=============================================================================")
        print("1 - Validate EC2 Instances")
        print("2 - Validate S3 Buckets")
        print("3 - Validate SQS Queues")
        print("4 - Validate autoscaling")
        print("0 - Exit")
        print("Enter a choice:")
        choice = input()
        return choice

    def main(self):
        while(1):
            choice = self.display_menu()
            if int(choice) == 1:
                self.validate_ec2_instance()
            elif int(choice) == 2:
                self.validate_s3_buckets()
            elif int(choice) == 3:
                self.validate_sqs_queues()
            elif int(choice) == 4:
                self.validate_autoscaling()
            elif int(choice) == 0:
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Grading Script')
    parser.add_argument('--access_keyId', type=str, help='ACCCESS KEY ID of the grading IAM user')
    parser.add_argument('--access_key', type=str, help='SECRET ACCCESS KEY of the grading IAM user')
    parser.add_argument('--req_sqs', type=str, help="Name of the Request SQS Queue")
    parser.add_argument('--resp_sqs', type=str, help="Name of the Response SQS Queue")
    parser.add_argument('--in_bucket', type=str, help='Name of the S3 Input Bucket')
    parser.add_argument('--out_bucket', type=str, help='Name of the S3 Output Bucket')

    args = parser.parse_args()

    access_keyId = args.access_keyId
    access_key   = args.access_key
    req_sqs      = args.req_sqs
    resp_sqs     = args.resp_sqs
    in_bucket    = args.in_bucket
    out_bucket   = args.out_bucket

    aws_obj = aws_grader(access_keyId, access_key, req_sqs, resp_sqs, in_bucket, out_bucket)
    aws_obj.main()
