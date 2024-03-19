### Grading Scripts

 - How to run the script: 
    ```
    usage: grader_script_p1.py [-h] [--access_key ACCESS_KEY] [--secret_key SECRET_KEY] [--input_bucket INPUT_BUCKET] [--lambda_name LAMBDA_NAME]
    Grading Script
    options:
    -h, --help          show this help message and exit
    --access_key ACCESS_KEY
                        ACCCESS KEY ID of the grading IAM user
    --secret_key SECRET_KEY
                        SECRET KEY of the grading IAM user
    --input_bucket INPUT_BUCKET
                        Name of the S3 Input Bucket
    --output_bucket OUTPUT_BUCKET
                        Name of the S3 Output Bucket
    --lambda_name LAMBDA_NAME
                        Name of the Lambda function

    ```
    **Note**: We will follow the naming conventions for S3 Bucket and Lambda function names as described in the project document to grade your submission

**Examples**:

We will show examples for each option below.

**Validate Lambda**: 

  - Successful Test
   ```
   python grading_scripts/grader_script_p1.py --access_key XXXX --secret_key XXXX --input_bucket 1234567890-input --lambda_name Video-splitting
   
   =============================================================================
======== Welcome to CSE546 Cloud Computing AWS Console ======================
=============================================================================
IAM ACESS KEY ID: XXXX
IAM SECRET ACCESS KEY: XXXX
=============================================================================
1 - Validate 1 Lambda function
2 - Validate S3 Buckets names and initial states
3 - Validate S3 output bucket subfolders
4 - Validate S3 output objects
5 - Check lambda average duration
6 - Check lambda concurrency
0 - Exit
Enter a choice: 1

Lambda function Video-splitting HTTPStatusCode 200
Test status of Test_1 : PASS



   ```
   - Failed Test
   ```
   python grading_scripts/grader_script_p1.py --access_key XXXX --secret_key XXXX --input_bucket 1234567890-input --lambda_name Video-splitting
   
   =============================================================================
======== Welcome to CSE546 Cloud Computing AWS Console ======================
=============================================================================
IAM ACESS KEY ID: XXXX
IAM SECRET ACCESS KEY: XXXX
=============================================================================
1 - Validate 1 Lmabda function
2 - Validate S3 Buckets names and initial states
3 - Validate S3 output bucket subfolders
4 - Validate S3 output objects
5 - Check lambda average latency
6 - Check lambda concurrency
0 - Exit
Enter a choice: 1

Error An error occurred (ResourceNotFoundException) when calling the GetFunction operation: Function not found: arn:aws:lambda:us-east-1:252116767176:function:Video-splitting
Test status of Test_1 : FAIL
   ```
