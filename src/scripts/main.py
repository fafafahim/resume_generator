########################################
# To ensure that the code only processes records that have a value in the key "email_feedback", you can add a check before processing each record. Here's how you can modify the main function to include this check
########################################
#!/usr/bin/env python3
import os
import argparse
import csv
from glob import glob
from dotenv import load_dotenv
from openai import AzureOpenAI
import time
import json

# Load .env variables
load_dotenv()

def append_record_to_json(record: dict, output_json: str):
    # If the file already exists, load its JSON content;
    # otherwise initialize an empty list.
    if os.path.exists(output_json):
        with open(output_json, "r", encoding="utf-8") as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []
    else:
        records = []
    records.append(record)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

########################################
# Prompt Config 
########################################

script_dir = os.path.dirname(os.path.abspath(__file__))

PROMPT_CONFIGS = [
    {
        "name": "job_desc_key_terms",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/job_desc_key_terms.txt"),
        "model_name": "o1",
        "output_key": "job_desc_key_terms",        
        "max_completion_tokens": 10000       
    },
    {
        "name": "compare_cv_resume_experience",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/compare_cv_resume_experience.txt"),
        "model_name": "o1",
        "output_key": "compare_cv_resume_experience",        
        "max_completion_tokens": 10000       
    },
    {
        "name": "compare_experiences",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/compare_experiences.txt"),
        "model_name": "o1",
        "output_key": "compare_experiences",        
        "max_completion_tokens": 10000 
    },
    {
        "name": "compare_education",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/compare_education.txt"),
        "model_name": "o1",
        "output_key": "compare_education",        
        "max_completion_tokens": 10000 
    },
    {
        "name": "generate_resume_initial",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/generate_resume_initial.txt"),
        "model_name": "o1",
        "output_key": "generate_resume_initial",        
        "max_completion_tokens": 10000 
    },
    {
        "name": "generate_resume",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/generate_resume.txt"),
        "model_name": "o1",
        "output_key": "resume",        
        "max_completion_tokens": 10000 
    },
    {
        "name": "generate_cover_letter_initial",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/generate_cover_letter_initial.txt"),
        "model_name": "o1",
        "output_key": "generate_cover_letter_initial",        
        "max_completion_tokens": 10000 
    },
    {
        "name": "generate_cover_letter",
        "prompt_path": os.path.join(script_dir, "../../src/prompts/generate_cover_letter.txt"),
        "model_name": "o1",
        "output_key": "cover_letter",        
        "max_completion_tokens": 10000 
    }
]

########################################
# Pricing details (per 1,000,000 tokens)
########################################
PRICING = {
    "o1": {
        "input": 5.00,
        "output": 20.00,
    },
    "o3-mini": {
        "input": 1.10,
        "output": 4.40,
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
    }
}

# Rate limit delays (in seconds) computed from requests per minute limits.
RATE_LIMIT_DELAYS = {
    "o3-mini": 180 / 500,  # 0.36 seconds per request
    "o1": 180 / 500,       # 0.36 seconds per request
    "gpt-4o": 180 / 2700,   # ~0.066 seconds per request (you may choose a slightly higher value to be conservative)
}

########################################
# Helper: Prompt Replacement
########################################
def get_prompt(template: str, variables: dict) -> str:
    prompt = str(template)
    for key, val in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in prompt:
            prompt = prompt.replace(placeholder, val)
    if "{" in prompt:
        idx = prompt.index("{")
        raise Exception(f"Unprocessed variable found at position {idx}: {prompt[idx:idx+30]}")
    return prompt

########################################
# Helper: Call Azure OpenAI with token usage tracking
########################################
API_KEY     = os.getenv("OPENAI_API_KEY")
API_BASE    = os.getenv("AZURE_ENDPOINT")
API_VERSION = "2024-12-01-preview"


def call_azure(model_name: str, prompt_text: str, max_tokens: int,
               reasoning_effort_o1: str = "high", reasoning_effort_o3mini: str = "medium",
               request_timeout_o1: int = 600, request_timeout_o3mini: int = 6000, request_timeout_gpt4o: int = 600) -> (str, dict):
    client = AzureOpenAI(
        azure_endpoint=API_BASE,
        api_key=API_KEY,
        api_version=API_VERSION
    )

    extra_params = {}  # default extra parameters
    req_timeout = None

    if model_name.startswith("o1"):
        extra_params["reasoning_effort"] = reasoning_effort_o1
        req_timeout = request_timeout_o1
    elif model_name.startswith("o3-mini"):
        extra_params["reasoning_effort"] = reasoning_effort_o3mini
        req_timeout = request_timeout_o3mini
    elif model_name.startswith("gpt-4o"):
        req_timeout = request_timeout_gpt4o
    else:
        req_timeout = 60

    messages = [
        {
            "role": "system",
            "content": "You are an expert recruiter in the healthcare industry."
        },
        {"role": "user", "content": prompt_text},
    ]

    if model_name.startswith("gpt-4o"):
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            timeout=req_timeout
        )
    else:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_completion_tokens=max_tokens,
                timeout=req_timeout,
                **extra_params
            )
        except TypeError as e:
            if "reasoning_effort" in str(e):
                extra_params.pop("reasoning_effort", None)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    timeout=req_timeout,
                    **extra_params
                )
            else:
                raise e

    content = response.choices[0].message.content.strip()
    usage = response.usage if hasattr(response, "usage") else {}
    if hasattr(usage, "dict"):
        usage = usage.dict()
    return content, usage


########################################
# Helper: Calculate Cost for a record
########################################
def calculate_cost(record):
    total_cost = 0.0
    for cfg in PROMPT_CONFIGS:
        model = cfg["model_name"]
        pricing = PRICING.get(model)
        if not pricing:
            continue
        key = cfg["output_key"]
        prompt_tokens = float(record.get(f"{key}_prompt_tokens", 0))
        completion_tokens = float(record.get(f"{key}_completion_tokens", 0))
        input_cost = pricing["input"] * (prompt_tokens / 1_000_000)
        output_cost = pricing["output"] * (completion_tokens / 1_000_000)
        total_cost += input_cost + output_cost
    return total_cost

########################################
# CLI Argument Parsing
########################################
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-txt", type=str, default=os.path.join(os.path.dirname(__file__), "../../input/input.txt"))
    # Changed default from resume.txt to output_all.txt for combined responses
    parser.add_argument("--output-txt", type=str, default=os.path.join(os.path.dirname(__file__), "../../output/output_all.txt"))
    return parser.parse_args()

########################################
# Append a record to CSV (filtered to desired columns)
########################################
def append_record(record: dict, output_csv: str, fieldnames: list):
    file_exists = os.path.exists(output_csv)
    filtered_record = { key: record.get(key, "") for key in fieldnames }
    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(filtered_record)

########################################
# Main
########################################
def main():
    args = parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    applied_path = os.path.join(script_dir, "../../_submitted/_applied.json")
    with open(applied_path, "r", encoding="utf-8") as f:
        applied_records = json.load(f)
    
    # Load global variables
    vars_paths = glob(os.path.join(script_dir, "../../variables/*"))
    global_vars = {}
    for v in vars_paths:
        with open(v, "r", encoding="utf-8") as f:
            key = os.path.basename(v).split(".")[0].strip()
            global_vars[key] = f.read().strip()

    # Load prompt templates
    prompt_templates = {}
    for cfg in PROMPT_CONFIGS:
        with open(cfg["prompt_path"], "r", encoding="utf-8") as f:
            prompt_templates[cfg["name"]] = f.read()

    # Process each record in applied_records if not yet processed
    for record in applied_records:
        if record.get("llm_processed", False):
            continue
        try:
            job_desc = record.get("job_description", "")
            if not job_desc.strip():
                raise Exception("Job description is empty for one of the records.")
            
            # Prepare prompt variables from globals and current job description
            prompt_vars = global_vars.copy()
            prompt_vars["input"] = job_desc

            for cfg in PROMPT_CONFIGS:
                template = prompt_templates[cfg["name"]]
                prompt_text = get_prompt(template, prompt_vars)
                model_name = cfg["model_name"]
                max_tokens = cfg.get("max_completion_tokens", 4000)
                
                print(f"Running prompt {cfg['name']} for record id: {record.get('job_title','N/A')}")
        
                result, usage = call_azure(model_name, prompt_text, max_tokens)
                # Save output using its output_key for later prompts.
                prompt_vars[cfg["output_key"]] = result
                delay = RATE_LIMIT_DELAYS.get(model_name, 0)
                time.sleep(delay)
        
            # Update record with outputs and mark as processed.
            record["resume"] = prompt_vars.get("resume", "No output produced for resume")
            record["cover_letter"] = prompt_vars.get("cover_letter", "No output produced for cover_letter")
            record["llm_processed"] = True
            # ...existing code to write updated applied_records...
            with open(applied_path, "w", encoding="utf-8") as f:
                json.dump(applied_records, f, indent=2)
                
        except Exception as e:
            if "content_filter" in str(e):
                print(f"Skipping record due to content filter error: {record.get('job_title','N/A')}")
                record["llm_processed"] = True
                record["skipped_due_to_content_filter"] = True
                with open(applied_path, "w", encoding="utf-8") as f:
                    json.dump(applied_records, f, indent=2)
                continue
            else:
                raise
    
if __name__ == "__main__":
    main()