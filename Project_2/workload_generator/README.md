# CSE546 workload_generator for Project 2

This repository contains code examples for you to use our workload generator.

Usage:
```
usage: workload_generator.py [-h] [--access_key AWS_ACCESS_KEY_ID] [--secret_key AWS_SECRET_KEY] [--input_bucket S3_INPUT_BUCKET_NAME] [--testcase_folder TESTCASE_FOLDER]

Upload videos to input S3

options:
  -h, --help            show this help message and exit
  --access_key ACCESS_KEY
                        ACCCESS KEY of the grading IAM user
  --secret_key SECRET_KEY
                        SECRET KEY of the grading IAM user
  --input_bucket INPUT_BUCKET
                        Name of the input bucket, e.g. 1234567890-input
  --output_bucket OUTPUT_BUCKET
                        Name of the output bucket, e.g. 1234567890-stage-1
  --testcase_folder TESTCASE_FOLDER
                        the path of the folder where videos are saved, e.g. test_cases/test_case_1/
```

Examples:

The following command sends videos from test_case_1 folder to 1234567890-input bucket.
```
python3 workload_generator.py \
 --access_key <ACCESS_KEY> \
 --secret_key <SECRET_KEY> \
 --input_bucket 1234567890-input \
 --testcase_folder test_cases/test_case_1/ \
```

Sample output:
```
Nothing to clear in input bucket
Uploading to input bucket..  name: test_5.mp4
Uploading to input bucket..  name: test_2.mp4
Uploading to input bucket..  name: test_8.mp4
Uploading to input bucket..  name: test_7.mp4
Uploading to input bucket..  name: test_6.mp4
Uploading to input bucket..  name: test_4.mp4
Uploading to input bucket..  name: test_1.mp4
Uploading to input bucket..  name: test_0.mp4
Time to run =  11.037546873092651 (seconds)

```

