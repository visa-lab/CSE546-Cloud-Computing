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
test_918.JPEG uploaded!
Classification result: Bill

test_934.JPEG uploaded!
Classification result: Emily

test_200.JPEG uploaded!
Classification result: Paul
```
