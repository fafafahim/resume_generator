# Creating a New Virtual Environment
To create a new virtual environment in Python, follow these steps:

1. Open a terminal in Visual Studio Code.

2. Navigate to the directory where you want to create the virtual environment.

3. Run the following command to create a new virtual environment:

`python3 -m venv emailQA_venv`

# Activate the virtual environment:

On macOS and Linux:
`source emailQA_venv/bin/activate`

On Windows:
`emailQA_venv\Scripts\activate`

5. Verify that the virtual environment is active by checking the command prompt, which should now include the name of your virtual environment.

6. To ensure that no existing dependencies are used, you can check the installed packages list, which should be empty or contain only pip and setuptools:

`pip list`

# Evironment Variables

1. Create accounts with Azure and BraveSearch.
2. Obtain the API keys for both services.
3. Create a `.env` file in the root directory of the project using the same format at `env.txt`.

Values in `.env.example` are illustrative only. Replace them with your own API keys.

Create the `BraveSearch` account and get the API key.

Register for an Azure free account and create the following resources:
`Azure OpenAI` resource in azure portal and get the key and endpoint. Deploy `gpt-4o`, `o3-mini`, and `o1`. 

Rename `.env.example` to `.env`.

# Install Dependencies

To install the required dependencies, run the following command:

```pip install -r requirements.txt```

# Tailor to your needs

Add content to files in `_variables`. You can also create new variables and delete existing variables. However, if you refer to a variable in any prompt, it must exist.

You can also change prompts or create new prompts. If you only change the content of the prompt and it can stay in the same place in the chain, no code changes are need. If you change the order of the prompts, you will need to change the code in `main.py` to reflect the new order.
If you create a new prompt, you will need to add it to the chain in `main.py` in `PROMPT_CONFIGS`. Order matter here, so make sure to add it in a position before all other prompts tht may reference its output.  
Use `output_key` in `main.py` to specify the output key for any new prompt.

# Run frontend

```run_scripts.ipynb```

# Create resume PDF

I am using teal to generate the PDF of the resume. Current prompts exclude education because teal has an issue with capturing the dates for education information. But you can just add that back in the 'generate_resume_initial.txt.`

https://jam.dev/c/22e0bd02-bafb-4173-993b-63fc2205c704