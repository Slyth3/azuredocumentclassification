from openai import OpenAIError , AzureOpenAI #OpenAI
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from prompts import get_prompts

# Parameters for llm
endpoint = os.getenv("openai_endpoint")
api_key = os.getenv("openai_key")
api_version = os.getenv("openai_api_version") 
model_name = os.getenv("openai_deployment")

def initialize_llm_inputs():
    #Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    
    # Get prompts
    user_prompt, system_prompt, example_text, example_response = get_prompts()

    return client, system_prompt, user_prompt, example_text, example_response

################################## Run LLM Classification ##################################
def run_llm_classification(client,document_content: str,full_file_name: str, system_prompt: str, user_prompt: str, example_text: str, example_response: str):

    ### Call OpenAI API
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                # Example 
                {"role": "user","content": f"{user_prompt}\n\nExtracted Text:\n{example_text}"},
                {"role": "assistant","content": f"""{example_response}"""},
                # request
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
