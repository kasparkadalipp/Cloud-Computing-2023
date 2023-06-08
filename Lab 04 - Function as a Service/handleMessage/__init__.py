import logging
import uuid
import azure.functions as func
from datetime import datetime


def main(req: func.HttpRequest, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    
    msg = req.params.get('msg')
    rowKey = str(uuid.uuid4())

    json_message = {
        'content': msg,
        'id':  rowKey,
        'message_time': datetime.now().isoformat(" ", "seconds")
    }

    outputDocument.set(func.Document.from_dict(json_message))

    return func.HttpResponse(
        f"Entered message was: {msg}",
        status_code=200,
        mimetype="text/html"
    )