from openai import OpenAIError , AzureOpenAI #OpenAI
import json
import logging
import os
from datetime import datetime, timezone, timedelta

# Parameters for llm
endpoint = os.getenv("openai_endpoint")
api_key = os.getenv("openai_key")
api_version = "2024-12-01-preview"
model_name = "gpt-4.1"

document_types = """Medical Aid/ Medical Scheme Certificate,Employee Tax Certificate, Retirement Annuity Certificate, Investment Income Certificate,
                     Medical Expenses, Travel Log Book, Other"""

def initialize_llm_inputs():
    #Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    # define prompts 
    user_prompt = f"""Analyze the following text and classify the document type(s)"""

    system_prompt = f"""You are a document classification agent for the South African Revenue Service. 
    Your task is to analyze the provided text and classify it into one or more document types. 
    Valid types are strictly limited to: {document_types}. 
    If 'Other' is used, you must specify the exact type in plain text (e.g., 'Proof of donations', 'travel logbook', 'Bank Statement', 'Invoice' etc). 
    You must respond ONLY in valid JSON with the following structure:"
    {{
    "Result": "<comma-separated list of identified types>",
    "Explanation": "<short explanation of why these types were chosen>
    }}
    Do not include any text outside of this JSON object. If more than one type is identified, separate them with commas."""

    return client, system_prompt, user_prompt

################################## Run LLM Classification ##################################
def run_llm_classification(client,document_content: str,full_file_name: str, system_prompt: str, user_prompt: str):

    ### Call OpenAI API
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_prompt}\n\nExtracted Text:\n{document_content}"}
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
            # max_completion_tokens=32768,
            max_tokens=32768
        )

        # Defensive checks
        if completion and completion.choices and completion.choices[0].message:
            model = completion.model
            logging.info(
                f"Classification Successful:\nModel {model}\nResponse:\n{completion.choices[0].message}"
            )
            # Parse JSON response
            try:
                response = json.loads(completion.choices[0].message.content)   # Try to parse the string

                # create additional response details
                response["ExtractedText"]=  document_content
                response["FileName"]= full_file_name
                response["Datetime"]= datetime.now(timezone(timedelta(hours=2))).isoformat()
                logging.info("Valid JSON response from LLM")
            except (ValueError, json.JSONDecodeError):
                logging.error("Invalid JSON response from LLM")
        else:
            logging.error("Completion returned no choices or message.")

    except OpenAIError as e:
        logging.exception(f"OpenAI API call failed: {e}")
    except Exception as e:
        logging.exception(f"Unexpected error during classification: {e}")

    return completion, response
