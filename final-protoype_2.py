import subprocess
import re
import pandas as pd
import os
import math
import anthropic
import json 

# Define the paths (unchanged)
quacky_path = "/home/adarsh/Documents/quacky/src/quacky.py"
quacky_output_path = "/home/adarsh/Documents/quacky/src/P1_not_P2.models"
working_directory = "/home/adarsh/Documents/quacky/src/"
response_file_path = "/home/adarsh/Documents/quacky/src/response.txt"
result_table_path = "/home/adarsh/Documents/quacky/src/policy_analysis.csv"
generated_policy_path = "/home/adarsh/Documents/quacky/src/gen_pol.json"

new_entries = []

# Input the policy path (unchanged)
policy_path = input("Enter the path to the policy file: ")

# Define string generation sizes (unchanged)
sizes = [500, 1000, 3000]

# Define the domain (unchanged)
domain = 598351357374183426465820918966277833792831151602221831961903311927039329512387758629575019633200474225590371059986240972155566335759382453956543412850668250328099108658454710205254006258984829517121

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="Your_API_Key")

def read_policy_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def get_policy_description(policy_content):
    prompt = f"Please provide a short description of what the following policy is doing:\n\n{policy_content}\n\nDescription:"
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error calling Anthropic API for policy description: {str(e)}")
        return ""

def generate_new_policy(description):
    # System prompt for policy generation
    policy_system_prompt = """When asked to generate a policy, provide only the policy in JSON format. Do not include any explanations, markdown formatting, or additional text. The response should be a valid JSON object that can be directly parsed.

    Example response format:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::example-bucket/*"
    }
  ]
}

Ensure that the generated policy is relevant to the given description and follows the access control policy structure."""

    prompt = f"Based on the following description, generate a new access control policy:\n\n{description}\n\nPolicy:"
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            system=policy_system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error calling Anthropic API for policy generation: {str(e)}")
        return ""

def save_generated_policy(policy_content, file_path):
    try:
        # Parse the policy_content as JSON
        policy_dict = json.loads(policy_content)
        
        # Write the parsed JSON to the file
        with open(file_path, 'w') as file:
            json.dump(policy_dict, file, indent=2)
        
        print(f"Generated policy saved to: {file_path}")
    except json.JSONDecodeError:
        print("Error: The generated policy is not valid JSON.")
        # Optionally, you might want to save the raw content for debugging
        with open(file_path, 'w') as file:
            file.write(policy_content)
        print(f"Raw content saved to: {file_path}")


def run_quacky_comparison(original_policy_path, generated_policy_path):
    # Get the full path to quacky.py
    quacky_full_path = os.path.abspath(quacky_path)
    
    command = [
        "python3",
        quacky_full_path,
        "-p1", original_policy_path,
        "-p2", generated_policy_path,
        "-b", "100"
    ]
    
    try:
        # Change to the directory containing quacky.py before running the command
        quacky_dir = os.path.dirname(quacky_full_path)
        result = subprocess.run(command, check=True, text=True, capture_output=True, cwd=quacky_dir)
        print("Quacky Comparison Results:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the comparison: {e}")
        if e.output:
            print("Output:")
            print(e.output)
        if e.stderr:
            print("Errors:")
            print(e.stderr)

def read_strings_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.read().splitlines() if line.strip()]


def generate_and_analyze_strings(size, policy_path, generated_policy_path):
    # Define system prompt for regex generation
    system_prompt = """When asked to give a regex, only give me the regex, no explanation nothing, do not talk to me at all. just give me the regex as output.

    For example:

    Prompt: 

    Give me a single regex that accepts the following set of strings, it should be close to optimal and not super permissive :

    arn:aws:s3:::foo!T~}[tk+\R~ s~
    arn:aws:s3:::foobk:p
    arn:aws:s3:::foovsbmD~uNp3vEBF
    arn:aws:s3:::bary|z~}
    arn:aws:s3:::foor^}\/Bl|T@'~
    arn:aws:s3:::bars}j|>iUb~7x|
    arn:aws:s3:::barL~~yEqy
    arn:aws:s3:::bar|9~pnq~~djb
    arn:aws:s3:::foo3{[u~rpGA
    arn:aws:s3:::foo~k|y,}vn
    arn:aws:s3:::foo~l}~
    arn:aws:s3:::fooTZg~{
    arn:aws:s3:::foo=~~xi
    arn:aws:s3:::bar~~~||
    arn:aws:s3:::fooUgyX~x
    arn:aws:s3:::barkz|wsz~


    Response:arn:arn:aws:s3:::(?:foo|bar)[a-z0-9.-]{0,60}$

    """

    # Define the command to generate strings using quacky (unchanged)
    command = [
     "python3", quacky_path,
     "-p1", policy_path,
     "-p2", generated_policy_path,
     "-b", "100",
     "-m", str(size),
     "-m1", "20",
     "-m2", "250"
    ]

    # Execute the command and capture the output (unchanged)
    try:
        subprocess.run(command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating strings: {e.stderr}")

    # Read the strings from quacky's output file (unchanged)
    try:
        with open(quacky_output_path, "r") as file:
            strings = [line.strip() for line in file.read().splitlines() if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {quacky_output_path}")
        return None, None, None

    # Use Anthropic API to generate regex
    prompt = "Give me a single regex that accepts each string in the following set of strings, it should be close to optimal and not super permissive :\n\n"
    prompt += "\n".join(f" {s}" for s in strings)
    prompt += "\n Response:"

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        complete_response = response.content[0].text
    except Exception as e:
        print(f"Error calling Anthropic API: {str(e)}")
        complete_response = ""
    regex_match = re.search(r"`([^`]+)`", complete_response)
    if regex_match:
        regex_only = regex_match.group(1)
    else:
        # Fallback in case no backticks are used
        regex_only = complete_response.strip()

    # Remove start and end anchors if they exist
    regex_only = regex_only.replace("^", "").strip()

    # Save the regex to the response file (unchanged)
    with open(response_file_path, "w") as output_file:
        output_file.write(regex_only)

    print(f"Regex written to {response_file_path}")

    # Run quacky analysis with the generated regex (unchanged)
    analysis_command = [
        "python3", quacky_path,
        "-p1", policy_path,
        "-p2", generated_policy_path,
        "-b", "100",
        "-cr", response_file_path
    ]

    try:
        analysis_result = subprocess.run(analysis_command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        analysis_output = analysis_result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running quacky analysis: {e.stderr}")
        return None, f"Error: {e.stderr}", None

    # Extract counts and compute ratios
    lines = analysis_output.split('\n')
    counts = {}
    for line in lines:
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                key = parts[0].strip()
                value = parts[1].strip()
                try:
                    counts[key] = int(value)
                except ValueError:
                    counts[key] = value  # Keep as string if it's not an integer
        elif "Policy 1 and Policy 2 are equivalent" in line:
            counts["Equivalence"] = "Policies are equivalent"

    # Initialize ratios
    BNS_Dom = NBS_Dom = log_BNS = log_NBS = float('nan')

    # Compute ratios and log values with error handling
    if 'Baseline_Not_Synthesized Count' in counts:
        BNS_count = counts['Baseline_Not_Synthesized Count']
        if isinstance(BNS_count, int) and BNS_count > 0:
            BNS_Dom = BNS_count / domain
            log_BNS = math.log(BNS_count)
        else:
            print(f"Warning: Baseline_Not_Synthesized Count is {BNS_count}, which is not a positive integer. Unable to compute ratios.")
    else:
        print("Warning: Baseline_Not_Synthesized Count not found in the analysis output.")

    if 'Not_Baseline_Synthesized_Count' in counts:
        NBS_count = counts['Not_Baseline_Synthesized_Count']
        if isinstance(NBS_count, int) and NBS_count > 0:
            NBS_Dom = NBS_count / domain
            log_NBS = math.log(NBS_count)
        else:
            print(f"Warning: Not_Baseline_Synthesized_Count is {NBS_count}, which is not a positive integer. Unable to compute ratios.")
    else:
        print("Warning: Not_Baseline_Synthesized_Count not found in the analysis output.")

    # Return the results
    return regex_only, analysis_output, {'BNS/Dom': BNS_Dom, 'log_BNS': log_BNS, 'NBS/Dom': NBS_Dom, 'log_NBS': log_NBS, 'Equivalence': counts.get('Equivalence', 'Not specified')}
    # Load existing results table or create a new one

def print_analysis_results(entries):
    print("New Analysis Results:")
    for entry in entries:
        print(f"Size: {entry['Size']}")
        print(f"Regex: {entry['Regex']}")
        print(f"Analysis Result: {entry['Analysis Result']}")
        print(f"BNS/Dom: {entry['BNS/Dom']}")
        print(f"log_BNS: {entry['log_BNS']}")
        print(f"NBS/Dom: {entry['NBS/Dom']}")
        print(f"log_NBS: {entry['log_NBS']}")
        print("---")

model_name = "claude-3-5-sonnet-20240620"  # This should be set to the current model being used


# Main execution
if __name__ == "__main__":
 
    policy_path = os.path.abspath(policy_path)
    generated_policy_path = os.path.abspath(generated_policy_path)    
    original_policy = read_policy_file(policy_path)
    
    # Get policy description
    policy_description = get_policy_description(original_policy)
    print(f"Policy Description:\n{policy_description}\n")
    
    # Generate new policy
    new_policy = generate_new_policy(policy_description)
    
    # Save the new policy
    save_generated_policy(new_policy, generated_policy_path)
    print(f"Generated policy saved to: {generated_policy_path}\n")

    # Run quacky comparison
    run_quacky_comparison(policy_path, generated_policy_path)
    # Initialize or load the results DataFrame
    if not os.path.exists(result_table_path):
        result_table = pd.DataFrame(columns=["model_name", "Policy", "Size", "Regex", "Analysis Result", "BNS/Dom", "log_BNS", "NBS/Dom", "log_NBS"])
    else:
        result_table = pd.read_csv(result_table_path)
        if "model_name" not in result_table.columns:
            result_table.insert(0, "model_name", "")

    # Generate strings, get regex, and run analysis for each size
    for size in sizes:
        regex, analysis_result, ratios = generate_and_analyze_strings(size, policy_path, generated_policy_path)
        if regex is not None and analysis_result is not None:
            new_entry = pd.DataFrame({
                "model_name": [model_name],
                "Policy": [policy_path],
                "Size": [size],
                "Regex": [regex],
                "Analysis Result": [analysis_result],
                "BNS/Dom": [ratios['BNS/Dom']],
                "log_BNS": [ratios['log_BNS']],
                "NBS/Dom": [ratios['NBS/Dom']],
                "log_NBS": [ratios['log_NBS']]
            })
            result_table = pd.concat([result_table, new_entry], ignore_index=True)
            new_entries.append(new_entry.to_dict('records')[0])

    # Save the updated results table
    result_table.to_csv(result_table_path, index=False)
    print(f"Results table updated and saved to {result_table_path}")

    # Call the function to print analysis results
    print_analysis_results(new_entries)


    #The print_analysis_results function is not printing the 'Equivalence' information that's now being returned by generate_and_analyze_strings.

    