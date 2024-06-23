import subprocess
import requests
import json
import re
import pandas as pd
import os
import math

# Define the paths
quacky_path = "/home/adarsh/Documents/quacky/src/quacky.py"
quacky_output_path = "/home/adarsh/Documents/quacky/src/P1_not_P2.models"
working_directory = "/home/adarsh/Documents/quacky/src/"
response_file_path = "/home/adarsh/Documents/quacky/src/response.txt"

# Define the new path for the results table
result_table_path = "/home/adarsh/Documents/quacky/src/policy_analysis.csv"

# Input the policy path
policy_path = input("Enter the path to the policy file: ")

# Define string generation sizes
sizes = [500, 1000, 3000]

# Define the domain
domain = 598351357374183426465820918966277833792831151602221831961903311927039329512387758629575019633200474225590371059986240972155566335759382453956543412850668250328099108658454710205254006258984829517121

# Function to generate strings, get regex, and run analysis
def generate_and_analyze_strings(size):
    # Define the command to generate strings using quacky
    command = ["python3", quacky_path, "-p1", policy_path, "-b", "100", "-m", str(size), "-m1", "20", "-m2", "250"]

    # Execute the command and capture the output
    try:
        subprocess.run(command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating strings: {e.stderr}")

    # Read the strings from quacky's output file
    try:
        with open(quacky_output_path, "r") as file:
            strings = file.read().splitlines()
    except FileNotFoundError:
        print(f"File not found: {quacky_output_path}")
        strings = []

    # Define the URL and payload
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": f"Provide only the regex that matches the following strings. The regex should not include start (^) or end ($) anchors: {', '.join(strings)}"
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

    # Extract the regex from the response, ensuring no start or end anchors
    regex_match = re.search(r"`([^`]+)`", complete_response)
    if regex_match:
        regex_only = regex_match.group(1)
    else:
        # Fallback in case no backticks are used
        regex_only = complete_response.strip()

    # Remove start and end anchors if they exist
    regex_only = regex_only.replace("^", "").replace("$", "").strip()

    # Save the regex to the response file
    with open(response_file_path, "w") as output_file:
        output_file.write(regex_only)

    print(f"Regex written to {response_file_path}")

    # Run quacky analysis with the generated regex
    analysis_command = ["python3", quacky_path, "-p1", policy_path, "-b", "100", "-cr", response_file_path]
    try:
        analysis_result = subprocess.run(analysis_command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        analysis_output = analysis_result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running quacky analysis: {e.stderr}")
        analysis_output = f"Error: {e.stderr}"

    # Extract counts and compute ratios
    lines = analysis_output.split('\n')
    counts = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':')
            counts[key.strip()] = int(value.strip())

    # Initialize ratios
    BNS_Dom = NBS_Dom = log_BNS = log_NBS = float('nan')

    # Compute ratios and log values
    if 'Baseline_Not_Synthesized Count' in counts:
        BNS_Dom = counts['Baseline_Not_Synthesized Count'] / domain
        log_BNS = math.log(counts['Baseline_Not_Synthesized Count'])
    if 'Not_Baseline_Synthesized_Count' in counts:
        NBS_Dom = counts['Not_Baseline_Synthesized_Count'] / domain
        log_NBS = math.log(counts['Not_Baseline_Synthesized_Count'])

    # Return the results
    return regex_only, analysis_output, {'BNS/Dom': BNS_Dom, 'log_BNS': log_BNS, 'NBS/Dom': NBS_Dom, 'log_NBS': log_NBS}

# Load existing results table or create a new one
if not os.path.exists(result_table_path) or os.path.getsize(result_table_path) == 0:
    result_table = pd.DataFrame(columns=["Policy", "Size", "Regex", "Analysis Result", "BNS/Dom", "log_BNS", "NBS/Dom", "log_NBS"])
    result_table.to_csv(result_table_path, index=False)  # Initialize the CSV file with headers
else:
    result_table = pd.read_csv(result_table_path)  # Read the existing file

# Generate strings, get regex, and run analysis for each size
for size in sizes:
    regex, analysis_result, ratios = generate_and_analyze_strings(size)
    new_entry = {
        "Policy": policy_path,
        "Size": size,
        "Regex": regex,
        "Analysis Result": analysis_result,
        "BNS/Dom": ratios['BNS/Dom'],
        "log_BNS": ratios['log_BNS'],
        "NBS/Dom": ratios['NBS/Dom'],
        "log_NBS": ratios['log_NBS']
    }
    result_table = result_table.append(new_entry, ignore_index=True)

# Save the updated results table
result_table.to_csv(result_table_path, index=False)

print(f"Results table updated and saved to {result_table_path}")

def print_analysis_results(df):
    print("Analysis Results:")
    for analysis_result in df['Analysis Result']:
        print(analysis_result)

# Call the function to print analysis results
print_analysis_results(result_table)
