# CSE546 workload_generator

This repository contains code examples for you to use our workload generator.

Usage:
```
usage: workload_generator.py [-h] [--num_request NUM_REQUEST] [--url URL] [--image_folder IMAGE_FOLDER] [--prediction_file PREDICTION_FILE]
Upload images
options:
  -h, --help            show this help message and exit
  --num_request NUM_REQUEST
                        one image per request
  --url URL             URL to the backend server, e.g. http://3.86.108.221:8000/
  --image_folder IMAGE_FOLDER
                        the path of the folder where images are saved
  --prediction_file PREDICTION_FILE
                        the path of the classification results file
```

Examples:

The following command sends three requests to a php backend.
```
python3 workload_generator.py \
 --num_request 3 \
 --url 'http://your_host_ip/php_server.php' \
 --image_folder "your_local_image_folder" \
 --prediction_file "ground_truth_prediction_file"
```

The following command sends three requests to a node.js/Python backend.
```
python3 workload_generator.py \
 --num_request 3 \
 --url 'http://<server_ip>:<server_port>' \
 --image_folder "your_local_image_folder" \
 --prediction_file "ground_truth_prediction_file"
```
**Note**: The workload generator accepts the absolute path in the command line arguments. 

Sample output:
```
test_411.jpg uploaded!
Classification result: test_411:Emily
Waiting ...
.
+++++ Test Result Statistics +++++
Total number of requests: 1000
Total number of requests completed successfully: 1000
Total number of failed requests: 0
Total number of correct predictions: 1000
Total number of wrong predictions: 0
Total Test Duration: 2.104762077331543 (seconds)
```
