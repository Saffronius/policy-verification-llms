import requests
import json

# Read the strings from the file
with open("/home/adarsh/Documents/file1", "r") as file:
    strings = file.read().splitlines()

# Define the URL and payload
url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3",
    "prompt": f"Provide a single regex that matches the following strings, the regex should not be overly permissive and sufficiently restrictive and should fit all the strings in question. Do not provide additional explanation or context,just the regex: {', '.join(strings)}"
}
headers = {"Content-Type": "application/json"}

# Send the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)

# Collect and assemble the response
complete_response = ""
for line in response.iter_lines():
    if line:
        part = json.loads(line)
        complete_response += part["response"]
        if part["done"]:
            break

print(complete_response)
