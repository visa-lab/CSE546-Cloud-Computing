### Grading Scripts


- [Project-1 Part-1 Test Case 1](https://github.com/visa-lab/CSE546-Cloud-Computing/blob/main/scripts/project1_grader.py)
  - Test Objective: 

    | Test # | Test Case            | Test Criteria                                                                                                                | Poor                                     | Good                                                | Excellent                                                | Total Points |
    |--------|----------------------|------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|-----------------------------------------------------|----------------------------------------------------------|--------------|
    | 1      | Validate EC2 Instance | "To check if 1) If there exists a EC2 instance with name ""web-instance"" 2) if exists then check if the state of the web-instance in ""running""" | There is no EC2 intance with name "web-instance" (0) | The EC2 instance with the name "web-instance" exists; but is not in "running" state (5) | The EC2 instance with the name "web-instance" exists; and is in "running" state (10) | 10        |
  
  - How to run the script: 
    ```
    usage: project1_grader.py [-h] [--access_keyId ACCESS_KEYID] [--access_key ACCESS_KEY]
    Grading Script
    options:
    -h, --help                    show this help message and exit
    --access_keyId ACCESS_KEYID   ACCCESS KEY ID of the grading IAM user
    --access_key ACCESS_KEY       SECRET ACCCESS KEY of the grading IAM user
    ```

- [Project-1 Part-2 Grading Script](https://github.com/visa-lab/CSE546-Cloud-Computing/blob/main/scripts/p2_grader.py):

  - How to use the script:
    ```
    usage: p2_grader.py [-h] [--access_keyId ACCESS_KEYID] [--access_key ACCESS_KEY] [--req_sqs REQ_SQS] [--resp_sqs RESP_SQS] [--in_bucket IN_BUCKET] [--out_bucket OUT_BUCKET]
    Grading Script  
    options:
      -h, --help                    show this help message and exit
      --access_keyId ACCESS_KEYID   ACCCESS KEY ID of the grading IAM user
      --access_key ACCESS_KEY       SECRET ACCCESS KEY of the grading IAM user
      --req_sqs REQ_SQS         Name of the Request SQS Queue
      --resp_sqs RESP_SQS       Name of the Response SQS Queue
      --in_bucket IN_BUCKET     Name of the S3 Input Bucket
      --out_bucket OUT_BUCKET   Name of the S3 Output Bucket
    ```
    **Note**: We will follow the naming conventions for S3 Bucket and SQS Queue names as described in the project document to grade your submission
    
    ```
      =============================================================================
      ======== Welcome to CSE546 Cloud Computing AWS Console ======================
      =============================================================================
      IAM ACESS KEY ID: XXXXXXXXXXXXX
      IAM SECRET ACCESS KEY: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
      =============================================================================
      1 - Validate EC2 Instances
      2 - Validate S3 Buckets
      3 - Validate SQS Queues
      4 - Validate autoscaling
      0 - Exit
      Enter a choice:
    ```
    
  
  - **Validate EC2 Instance**: 
    ```
    =============================================================================
    ======== Welcome to CSE546 Cloud Computing AWS Console ======================
    =============================================================================
    IAM ACESS KEY ID: XXXXXXXXXXXXX
    IAM SECRET ACCESS KEY: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    =============================================================================
    1 - Validate EC2 Instances
    2 - Validate S3 Buckets
    3 - Validate SQS Queues
    4 - Validate autoscaling
    0 - Exit
    Enter a choice:
    1
    Found 1 web-tier instances in running state.
    Found 0 app-tier instanes in running state
    ```
      
  - **Validate S3 Buckets**
    ```
    =============================================================================
    ======== Welcome to CSE546 Cloud Computing AWS Console ======================
    =============================================================================
    IAM ACESS KEY ID: XXXXXXXXXXXXX
    IAM SECRET ACCESS KEY: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  
    =============================================================================
    1 - Validate EC2 Instances
    2 - Validate S3 Buckets
    3 - Validate SQS Queues
    4 - Validate autoscaling
    0 - Exit
    Enter a choice:
    2
     - WARN: If there are objects in the S3 buckets; they will be deleted
     ---------------------------------------------------------
    S3 Input Bucket:12345678910-in-bucket has 0 object(s)
    S3 Output Bucket:12345678910-out-bucket has 0 object(s)
    ```
      
  - **Validate SQS Queue**
    ```
    =============================================================================
    ======== Welcome to CSE546 Cloud Computing AWS Console ======================
    =============================================================================
    IAM ACESS KEY ID: XXXXXXXXXXXXX
    IAM SECRET ACCESS KEY: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    =============================================================================
    1 - Validate EC2 Instances
    2 - Validate S3 Buckets
    3 - Validate SQS Queues
    4 - Validate autoscaling
    0 - Exit
    Enter a choice:
    3
     - The expectation is the both the Request and Response SQS should exist and be EMPTY
     - WARN: This will purge any messages available in the SQS
     ---------------------------------------------------------
    SQS Request Queue:12345678910-req-queue has 0 pending messages.
    SQS Response Queue:12345678910-resp-queue has 0 pending messages.
    ```
      
  - **Validate autoscaling**
    ```
    =============================================================================
    ======== Welcome to CSE546 Cloud Computing AWS Console ======================
    =============================================================================
    IAM ACESS KEY ID: XXXXXXXXXXXXX
    IAM SECRET ACCESS KEY: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    =============================================================================
    1 - Validate EC2 Instances
    2 - Validate S3 Buckets
    3 - Validate SQS Queues
    4 - Validate autoscaling
    0 - Exit
    Enter a choice:
    4
     - Run this BEFORE the workload generator client starts. Press Ctrl^C to exit.
     - The expectation is as follows:
     -- # of app tier instances should gradually scale and eventually reduce back to 0
     -- # of SQS messages should gradually increase and eventually reduce back to 0
    ------------------------------------------------------------------------------------------------------------------
    |   # of messages in   |   # of messages in   |  # of EC2 instances  |  # of objects in S3  |  # of objects in S3  |
    |  SQS Request Queue   |  SQS Response Queue  |   in running state   |     Input Bucket     |     Output Bucket    |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          0           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          1           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          2           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          4           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          8           |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          11          |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          16          |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          17          |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          19          |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          50          |          0           |          20          |          0           |          0           |
    ------------------------------------------------------------------------------------------------------------------
    |          48          |          0           |          20          |          2           |          2           |
    ------------------------------------------------------------------------------------------------------------------
    |          35          |          0           |          20          |          2           |          2           |
    ------------------------------------------------------------------------------------------------------------------
    |          35          |          0           |          20          |          9           |          9           |
    ------------------------------------------------------------------------------------------------------------------
    |          35          |          0           |          20          |          12          |          12          |
    ------------------------------------------------------------------------------------------------------------------
    |          32          |          0           |          20          |          21          |          21          |
    ------------------------------------------------------------------------------------------------------------------
    |          42          |          4           |          20          |          28          |          29          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          40          |          40          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          47          |          47          |
    ------------------------------------------------------------------------------------------------------------------
    |          4           |          0           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          41          |          4           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          3           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          12          |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          8           |          20          |          49          |          49          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          3           |          20          |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          20          |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          15          |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          6           |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    |          0           |          0           |          0           |          50          |          50          |
    ------------------------------------------------------------------------------------------------------------------
    ```
    The above example output is for a 50-requests workload.


**Note**: This does not show all the test cases for the project. Please refer to the project document for more details.
