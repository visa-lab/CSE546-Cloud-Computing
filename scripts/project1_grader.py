import os
import boto3
import dotenv
import httpx
import pdb
import json
import argparse

class aws_grader():
    def __init__(self, access_keyId, access_key):

        self.iam_access_keyId       = access_keyId
        self.iam_secret_access_key  = access_key
        self.iam_session            = boto3.Session(aws_access_key_id = self.iam_access_keyId,
                                                    aws_secret_access_key = self.iam_secret_access_key)
        self.ec2_resources          = self.iam_session.resource('ec2', 'us-east-1')

    def get_tag(self, tags, key='Name'):

        if not tags:
            return 'None'
        for tag in tags:
            if tag['Key'] == key:
                return tag['Value']
        return 'None'


    '''
        Test Case:1
            1) Checks if there is a web EC2 instance with the name "web-instance"
            2) Checks if the state of "web-instance" is "running".
    '''

    def test_case_1(self):
        message = ""
        for instance in self.ec2_resources.instances.all():
            name = self.get_tag(instance.tags)
            if name == "web-instance":
                message += "web-tier instance found."
                state = instance.state['Name']
                message += f" With state: {state}"
                if state == "running":
                    self.web_tier_instanceId = instance.id
                    print(f"Test Case:1 Passed. {message}")
                    return
                else:
                    print(f"Test Case:1 Failed. {message}")
                    return

        message += "web-tier Instance Not Found."
        print("Test Case:1 Failed. {message}")


    def main(self):
        # Use the session to access resources via the role

        print("======== Welcome to CSE546 Cloud Computing Grading Console ==================")
        print(f"IAM ACESS KEY ID: {self.iam_access_keyId}")
        print(f"IAM SECRET ACCESS KEY: {self.iam_secret_access_key}")

        self.test_case_1()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload images')
    parser.add_argument('--access_keyId', type=str, help='ACCCESS KEY ID of the grading IAM user')
    parser.add_argument('--access_key', type=str, help='SECRET ACCCESS KEY of the grading IAM user')

    args = parser.parse_args()

    access_keyId = args.access_keyId
    access_key   = args.access_key

    aws_obj = aws_grader(access_keyId, access_key)
    aws_obj.main()
