# Policy Verification and Generation using LLMs

## Description

This project utilizes Large Language Models (LLMs), specifically Claude 3.5 Sonnet and llama-3 , for access control policy verification, generation, and comparison. It integrates with the quacky tool for policy analysis and employs regex generation for string matching.

Key features:
- Generate new policies based on descriptions of existing policies
- Compare original and generated policies using quacky
- Generate regex patterns matching strings from policies
- Analyze policies across different sample sizes
- Compute and store various metrics for policy comparison

## Dependencies

- Python 3.x
- pandas
- anthropic
- subprocess
- re
- math
- json
- quacky (separate tool, must be installed and accessible)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/policy-verification-llms.git
   cd policy-verification-llms
   ```

2. Install the required Python libraries:
   ```
   pip install pandas anthropic
   ```

3. Ensure quacky is installed and its path is correctly set in the script.

4. Set up your Anthropic API key as an environment variable or directly in the script (not recommended for security reasons).

## Configuration

Before running the script, ensure the following paths are correctly set:

- `quacky_path`: Path to the quacky.py script
- `working_directory`: Directory containing quacky and related files
- `response_file_path`: Path for storing generated regex
- `result_table_path`: Path for CSV file storing analysis results
- `generated_policy_path`: Path for storing generated policies

## Usage

Run the script using Python:

```
python final-prototype.py
```

When prompted, enter the path to the policy file you want to analyze.

The script will:
1. Read the original policy
2. Generate a description of the policy using Claude
3. Generate a new policy based on this description
4. Compare the original and generated policies using quacky
5. Perform analysis on both policies for different sample sizes
6. Generate regex patterns for string matching
7. Compute various metrics and ratios
8. Store results in a CSV file

## Output

- Generated policies are saved as JSON files
- Analysis results are stored in a CSV file
- Console output provides information on each step of the process

## Troubleshooting

If you encounter issues:
- Ensure all paths are correctly set
- Check that quacky is properly installed and accessible
- Verify your Anthropic API key is correct and has necessary permissions

## Contributing

Contributions to improve the project are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Specify your license here]

## Authors

- Adarsh Vatsa

## Version History

- 0.2
  - Integration with Claude 3.5 Sonnet
  - Added policy generation and comparison features
  - Improved analysis and metrics computation
- 0.1
  - Initial Release
