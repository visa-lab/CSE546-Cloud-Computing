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
    -h, --help            show this help message and exit
    --access_keyId ACCESS_KEYID
                        ACCCESS KEY ID of the grading IAM user
    --access_key ACCESS_KEY
                        SECRET ACCCESS KEY of the grading IAM user
    ```




**Note**: This does not show all the test cases for the project. Please refer to the project document for more details.
