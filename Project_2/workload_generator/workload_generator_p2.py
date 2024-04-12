from boto3 import client as boto3_client
import os
import argparse
import time
from datetime import datetime
import json


timestamps = {}

start_time = time.time()
parser = argparse.ArgumentParser(description='Upload videos to input S3')
# parser.add_argument('--num_request', type=int, help='one video per request')
parser.add_argument('--access_key', type=str, help='ACCCESS KEY of the grading IAM user')
parser.add_argument('--secret_key', type=str, help='SECRET KEY of the grading IAM user')
parser.add_argument('--asu_id', type=str, help='10-digit ASU ID, e.g. 1234567890')
parser.add_argument('--testcase_folder', type=str,
					help='the path of the folder where videos are saved, e.g. test_cases/test_case_1/')

args = parser.parse_args()

access_key = args.access_key
secret_key = args.secret_key
asu_id = args.asu_id
input_bucket = asu_id + "-input"
stage1_bucket = asu_id + "-stage-1"
output_bucket = asu_id + "-output"
test_cases = args.testcase_folder
region = 'us-east-1'

s3 = boto3_client('s3', aws_access_key_id=access_key,
				  aws_secret_access_key=secret_key, region_name=region)


def clear_input_bucket(input_bucket):
	global s3
	list_obj = s3.list_objects_v2(Bucket=input_bucket)
	print(list_obj)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=input_bucket, Key=key)
	except:
		print("Nothing to clear in input bucket")


def clear_output_bucket(output_bucket):
	global s3
	list_obj = s3.list_objects_v2(Bucket=output_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=output_bucket, Key=key)
	except:
		print("Nothing to clear in output bucket")


def upload_to_input_bucket_s3(input_bucket, path, name):
	global s3
	s3.upload_file(path + name, input_bucket, name)


def write_to_file(outfilename, save_dict):
	with open(outfilename, 'w') as f:
		f.write(json.dumps(save_dict))


def upload_files(input_bucket, test_dir):
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			print("Uploading to input bucket..  name: " + str(filename))
			filename_raw = filename.split(".mp4")[0]
			timestamps[filename_raw] = time.time()
			upload_to_input_bucket_s3(input_bucket, test_dir, filename)

# Stagger the requests by 3 seconds
def upload_files_v2(input_bucket, test_dir):
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			print("Uploading to input bucket..  name: " + str(filename))
			filename_raw = filename.split(".mp4")[0]
			timestamps[filename_raw] = datetime.timestamp(datetime.now())
			upload_to_input_bucket_s3(input_bucket, test_dir, filename)
			time.sleep(1)


print("Clearing all the buckets ...")
clear_input_bucket(input_bucket)
clear_input_bucket(stage1_bucket)
clear_input_bucket(output_bucket)

print("Starting the upload in 3 sec ...")
time.sleep(3)
# upload_files(input_bucket, test_cases)
upload_files_v2(input_bucket, test_cases)

end_time = time.time()
print("Time to run = ", end_time - start_time, "(seconds)")
print(f"Timestamps: start {start_time}, end {end_time}")

print("Waiting for 10 sec to finish all the processing of the functions ...")
time.sleep(10)
if timestamps:
	for filename in os.listdir(test_cases):
		out_bucket = "1234567890-output"
		response = s3.list_objects(Bucket=out_bucket, Prefix=filename.split(".mp4")[0])
		if "Contents" in response:
			time_lastmodified = datetime.timestamp(response['Contents'][0]['LastModified'])
			timestamps[filename.split(".mp4")[0]] = time_lastmodified - timestamps[filename.split(".mp4")[0]]

	filtered_values = [value for value in timestamps.values() if 0 <= value <= 200]
	if filtered_values:
		minimum = min(filtered_values)
		maximum = max(filtered_values)
		average = sum(filtered_values) / len(filtered_values)
		print("Minimum:", minimum)
		print("Maximum:", maximum)
		print("Average:", average)
	else:
		print("No values between 20 and 200 found in the dictionary.")
