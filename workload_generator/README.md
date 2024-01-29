# CSE546_workload_generator

This repository contains code examples for you to use our workload generator.

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
