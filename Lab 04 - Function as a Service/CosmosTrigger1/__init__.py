import logging
import json
import azure.functions as func


def main(documents: func.DocumentList, message: func.Out[str]) -> func.HttpResponse:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])
        body = documents[0]['content']

        value = {
            "body": body,
            "to": ""
        }

        
        message.set(json.dumps(value))
