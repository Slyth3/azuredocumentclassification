# To do 
## Error Handing 
## Confidence score for llm classification
## Embeddings for large documents OR set token limitations 
## document intelligence convert to SDK 

import azure.functions as func
from azure.storage.blob import BlobServiceClient
import logging
import os
import base64

## import local files
import run_DocumentIntelligence as docintel
import run_LLMClasscification as llmclass
import run_FabricEventHub as eventhub

########################## Parameters ##########################
poll_interval=2 # seconds to retry polling document intelligence
max_wait=60

eventhub_endpoint = os.getenv("Eventhub_endpoint")
eventhub_name = os.getenv("Eventhub_name")

docintel_endpoint = os.environ.get("docintelligenceendpoint")
docintel_apim_key = os.environ.get("docintelligencekey")
docintel_modelId = "prebuilt-layout" # "prebuilt-document" : General doesnt exist in RSA
docintel_post_url = f"{docintel_endpoint}/documentintelligence/documentModels/{docintel_modelId}:analyze?api-version=2024-11-30"

container_name="document-processing-dropzone"

######################### App settings ##########################
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) #app = func.FunctionApp()

########################################################################### Blob Trigger ##########################################################

### Def Function name (blob_documentprocessing) determines the deployed function name in Azure
@app.blob_trigger(arg_name="myblob", path="document-processing-dropzone/Input/{name}",
                               connection="rgdocumentprocessinb772_STORAGE") 
def blob_documentprocessing(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed\n"
                f"File Name: {myblob.name}\n"
                f"Blob Size: {myblob.length} bytes\n")

    try:
        pdf_bytes = myblob.read() 
        if not pdf_bytes:  
            raise ValueError("Unable to read blob file")
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8") 
        logging.info(f"File read and converted to base64, with file size: {len(pdf_bytes)} bytes\n")

        # get file name 
        full_file_name=os.path.basename(myblob.name)
        file_name=(os.path.splitext(full_file_name)[0]) 
        logging.info("Name:%s\n", full_file_name)

        # ##########################  Call Document Intelligence endpoint 
        results = docintel.run_document_intelligence(pdf_base64, docintel_apim_key, docintel_endpoint)

        # Process results into text 
        full_text = docintel.process_results(results)
        logging.info(f"Text extracted from Document Intelligence, results:\n {full_text}\n")
    
        ##########################  Call LLM Classification
        try:

            client, system_prompt, user_prompt, example_text, example_response = llmclass.initialize_llm_inputs()
            llm_completion, llm_response = llmclass.run_llm_classification(client,full_text,full_file_name, system_prompt, user_prompt, example_text, example_response)
            # Get the current local date and time as a datetime object
        ##########################  Save results to Blob Storage
            try:
                # Blob connection
                blob_service_client = BlobServiceClient.from_connection_string(os.environ["rgdocumentprocessinb772_STORAGE"])
                container_client=blob_service_client.get_container_client(container_name)
                logging.info("Connection set to upload text to blob\n")

                # Upload to blob storage
                # save both docintel and llm results
                final_output = (
                    "Document processing executed successfully\n"
                    f"FileName:{llm_response['FileName']}\n"
                    f"File size: {len(pdf_bytes)} bytes\n"
                    f"Date Processed: {llm_response['Datetime']}\n\n"
                    f"LLM Result: {llm_response['Result']}\n"
                    f"LLM Confidence: {llm_response.get('Confidence', 'N/A')}\n"
                    f"LLM Explanation: {llm_response['Explanation']}\n\n"
                    f"Extracted Text:\n{llm_response['ExtractedText']}" 
                )

                container_client.upload_blob(name=f"Output/{file_name}.txt",data=final_output,overwrite=True)
                logging.info("Uploaded text file to blob storage successfully\n")
            except Exception as e:
                logging.exception("Error during file save to container ")
        ##########################  Fabric Event Hub - Save data 
            try:
                eventhub_response = eventhub.eventhub_save(eventhub_endpoint, eventhub_name, llm_response)
                logging.info("Event Hub save successfully\n")
                logging.info(f"Completed with results:\n{llm_response}\n")
            except Exception as e:
                logging.exception("Error during Event Hub save ")

        ########## Exceptions
        except Exception as e:
            logging.exception("Error during LLM Classification")

    except ValueError as ve:
        logging.error(f"ValueError during document processing: {ve}")
    except Exception as e:
        logging.exception(f"Unexpected error during document processing: {str(e)}")

########################################################################### HTTP Trigger ##########################################################

@app.route(route="func_document_processing")  # this is used in the url path
def http_documentprocessing(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request')

    try:
        pdf_bytes = req.get_body()
        full_file_name = req.params.get("filename") # doesnt work 
        if not pdf_bytes:  
            raise ValueError("No file provided in request body")

        # convert pdf to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8") 
        logging.info(f"File read and converted to base64, with file size: {len(pdf_bytes)} bytes\n")

        # ##########################  Call Document Intelligence endpoint 
        results = docintel.run_document_intelligence(pdf_base64, docintel_apim_key, docintel_endpoint)

        ########################## Process results into text 
        full_text = docintel.process_results(results)
        logging.info(f"Text extracted from Document Intelligence, results:\n {full_text}\n")

        ##########################  Call LLM Classification
        try:
            client, system_prompt, user_prompt, example_text, example_response = llmclass.initialize_llm_inputs()
            llm_completion, llm_response = llmclass.run_llm_classification(client,full_text,full_file_name, system_prompt, user_prompt, example_text, example_response)
        ##########################  Fabric Event Hub - Save data 
            try:
                eventhub_response = eventhub.eventhub_save(eventhub_endpoint, eventhub_name, llm_response)
                logging.info("Event Hub save successfully\n")
                final_output = (
                    "Document processing executed successfully\n"
                    f"FileName:{llm_response['FileName']}\n"
                    f"File size: {len(pdf_bytes)} bytes\n"
                    f"Date Processed: {llm_response['Datetime']}\n\n"
                    f"LLM Result: {llm_response['Result']}\n"
                    f"LLM Confidence: {llm_response.get('Confidence', 'N/A')}\n"
                    f"LLM Explanation: {llm_response['Explanation']}\n\n"
                    f"Extracted Text:\n{llm_response['ExtractedText']}" 
                )

                logging.info(f"Completed with results:\n{llm_response}\n")
                return func.HttpResponse(body=final_output, status_code=200 )

            except Exception as e:
                logging.exception("Error during Event Hub save ")
                return func.HttpResponse(
                    body=f"FAILED to save to Event Hub.Event Hub Error: {str(e)}",
                    status_code=500)

        ########## Exceptions
        except Exception as e:
            logging.exception("Error during LLM Classification")
            return func.HttpResponse(
                body=f"Document processing SUCCESSFUL, but LLM Classification FAILED.\nDocument Intelligence Output:\n{docintel_output}\n\nLLM Error: {str(e)}",
                status_code=500
            )

    except ValueError as ve:
        logging.error(f"ValueError during document processing: {ve}")
        return func.HttpResponse(
            body=f"Document processing FAILED.\nError: {ve}",
            status_code=400
        )

    except Exception as e:
        logging.exception(f"Unexpected error during document processing: {str(e)}")
        return func.HttpResponse(
            body=f"Document processing FAILED.\nUnexpected Error: {str(e)}",
            status_code=500
        )

