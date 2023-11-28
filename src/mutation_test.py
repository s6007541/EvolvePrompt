import requests
import json

url = 'http://127.0.0.1:8794/'  # Replace with your server's address

# Sample array data
prompt = """Please follow the instruction step-by-step to generate a better prompt.
1. Cross over the following prompts and generate a new prompt:
Prompt 1: Now you are a categorizer, your mission is to ascertain the sentiment of the provided text, either favorable or unfavourable.
Prompt 2: Assign a sentiment label to the given sentence from ['negative', 'positive'] and return only the label without any other text.
2. Mutate the prompt generated in Step 1 and generate a final prompt bracketed with <prompt> and </prompt>."""

input = [
            {
                "role": "user",
                "content": prompt,
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