import logging
import json
import time
import os
import requests

def run_DocIntel(post_url, pdf_source,api_key):

    headers = {
    'Content-Type': 'application/json',  # base 64 content within json
    'Ocp-Apim-Subscription-Key': api_key,
    }
    payload = {
    "base64Source": pdf_source
    } 
    
    # Post: File for Analysis 
    resp = requests.post(url=post_url, json=payload, headers=headers)

    if resp.status_code != 202:
        logging.info("Document Intelligence: POST File Failed:\n%s" % resp.text)
        quit()
    logging.info("Document Intelligence: POST File Succeeded\n") #resp.headers

    # response URL (to GET results)
    get_url = resp.headers["operation-location"]

    return get_url

def get_DocIntel_results(api_key, get_url, poll_interval, max_wait):

    elapsed = 0
    while True:
        resp = requests.get(url=get_url, headers={"Ocp-Apim-Subscription-Key": api_key})
        resp_json = resp.json()
        status = resp_json.get("status")

        if status == "succeeded":
            logging.info("Document Intelligence: Get Results Succeeded")
            return resp_json

        elif status == "failed":
            logging.error(
                "Document Intelligence: Processing Failed: %s",
                resp_json
            )
            raise RuntimeError(f"Document Intelligence failed: {resp_json}")

        elif status is None:
            logging.error(
                "Document Intelligence: Missing status in response: %s",
                resp_json
            )
            raise ValueError(f"Unexpected response: {resp_json}")

        
        # Wait before polling again
        time.sleep(poll_interval)
        elapsed += poll_interval

        if elapsed > max_wait:
            logging.info("Document Intelligence polling timed out\n")
            raise TimeoutError(f"Document Intelligence polling timed out\n")
 

def process_results(results):
    full_text=  results['analyzeResult']['content']
    return full_text