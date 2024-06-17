# policy-verification-llms
Summer research work over utilization of llms for access control policy verification and generation.

# Description

This project uses the Llama-3 language model to generate a regex pattern that matches a set of given strings. The strings are read from a text file, where each string is on a new line. The generated regex pattern is printed to the console.

The project aims to generate a regex pattern that is not overly permissive and is sufficiently restrictive. However, please note that the quality and correctness of the generated regex depend on the capabilities of the Llama-3 model and the complexity of the strings.

# Dependencies

    The project requires the requests library to send HTTP requests to the Llama-3 API.
    The Llama-3 language model must be accessible via an API at http://localhost:11434/api/generate.

# Installing

    Clone the repository.
    Install the required libraries using pip:

# pip install requests

    Replace path_to_your_file.txt in the script with the path to your text file containing the strings.

# Executing

    Run the script using Python:

    python script_name.py

    The generated regex pattern will be printed to the console.

# Help

If you encounter any issues or have any questions, please open an issue in the repository.
# Authors

    Adarsh Vatsa

# Version History

    0.1
        Initial Release

