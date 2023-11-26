import requests
import json

url = 'http://127.0.0.1:8794/'  # Replace with your server's address

# Sample array data
input = [
            {
                "role": "user",
                "content": "In Bash, how do I list all text files in the current directory (excluding subdirectories) that have been modified in the last month?",
            }
        ]

# Send a POST request with the array data
try:
    response = requests.post(url, json={'messages': input})
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print('Success! Server Response:\n{}'.format(response.json()[0]['generation']['content']))
    else:
        print(f'Error: {response.status_code} - {response}')

except requests.exceptions.RequestException as e:
    print(f'Request failed: {e}')
