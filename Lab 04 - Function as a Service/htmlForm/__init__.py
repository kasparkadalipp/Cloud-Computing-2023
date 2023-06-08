import logging

import azure.functions as func


def main(req: func.HttpRequest, inputDocument) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    messages = "".join([f"<li>{doc['content']}</li>" for doc in inputDocument[-10:]])

    html_data = f"""
    <title>Message board</title>
    <body>
        <h1>Kaspar Kadalipp</h1>
        <h4> Welcome to the message board. </h4>
        <ul>
          {messages} 
        </ul>
        <h4> Enter a new message</h4>
        <form action="/api/handleMessage">
            <label> Your message: </label><br>
            <input type="text" name="msg"><br>
            <input type="submit" value="Submit">
        </form>
        </body>
        </html>
    """

    return func.HttpResponse(
        html_data,
        status_code=200,
        mimetype="text/html"
    )
