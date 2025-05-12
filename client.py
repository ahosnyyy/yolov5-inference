import requests

# Define the URL for the API endpoint
url = 'http://yolov5-inference-alb-209717925.eu-central-1.elb.amazonaws.com/detect-default'

# Define query parameters for the request
params = {
    'weights': 'models/merged_clothing.pt',
    'img_size': 640,
    'conf_thres': 0.25,
    'iou_thres': 0.45,
    'yaml_file': 'merged_clothing.yaml'
}

# Send the GET request to the API with parameters
response = requests.get(url, params=params)

# Check if the request was successful (HTTP 200)
if response.status_code == 200:
    print("Request Successful!")
    print("Response JSON:", response.json())  # Print the JSON response
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response text:", response.text)
