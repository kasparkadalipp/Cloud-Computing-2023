import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

from flask import Flask, render_template, request

COSMOS_URL = os.getenv('COSMOS_URL')
CONN_KEY = os.getenv('CONN_KEY')
DATABASE_ID = os.getenv('DATABASE_ID')
CONTAINER_ID = os.getenv('CONTAINER_ID')
MasterKey = os.getenv('MasterKey')
storage_account = os.getenv('STORAGE_ACCOUNT')
images_container = 'images'


class Config(object):
    SECRET_KEY = 'lab5kadalipp'
    UPLOAD_FOLDER = 'static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


app = Flask(__name__)
app.config.from_object(Config)
blob_service_client = BlobServiceClient(account_url="https://"+storage_account+".blob.core.windows.net/", credential=CONN_KEY)
cosmos_db_client = cosmos_client.CosmosClient(COSMOS_URL, {'masterKey': MasterKey})
cosmos_db = cosmos_db_client.get_database_client(DATABASE_ID)
container = cosmos_db.get_container_client(CONTAINER_ID)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'gif'}


def read_messages_from_file():
    """ Read all messages from a JSON file"""
    with open('data.json') as messages_file:
        return json.load(messages_file)


def insert_blob(file):
    filename = secure_filename(str(uuid.uuid4()) + file.filename[-4:])
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)
    blob_client = blob_service_client.get_blob_client(container=images_container, blob=filename)
    with open(file=image_path, mode="rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    image_path = 'https://'+storage_account + '.blob.core.windows.net/'+images_container+'/' + filename
    return image_path

def insert_cosmos(request):
    """ Read the contents of JSON file, add this message to it's contents, then write it back to disk. """
    image_path = ''
    file = request.files['file']
    if file and allowed_file(file.filename):
        image_path = insert_blob(file)

    new_message = {
        'id': str(uuid.uuid4()),
        'content': request.form['msg'],
        'timestamp': datetime.now().isoformat(" ", "seconds"),
        'img_path': image_path
    }
    try:
        container.create_item(body=new_message)
    except exceptions.CosmosResourceExistsError:
        print("Resource already exists, didn't insert message.")
 

def read_cosmos():
    return list(container.read_all_items(max_item_count=10))


def append_message_to_file(request):
    """ Read the contents of JSON file, add this message to it's contents, then write it back to disk. """
    image_path = ''
    file = request.files['file']
    if file and allowed_file(file.filename):
        image_path = insert_blob(file)

    data = read_messages_from_file()
    new_message = {
        'id': str(uuid.uuid4()),
        'content': request.form['msg'],
        'timestamp': datetime.now().isoformat(" ", "seconds"),
        'img_path': image_path
    }
    data['messages'].append(new_message)
    with open('data.json', mode='w') as messages_file:
        json.dump(data, messages_file)

# The Flask route, defining the main behaviour of the webserver:


@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        insert_cosmos(request) # task 5.4

    data = read_cosmos()  # task 5.4
    # Return a Jinja HTML template, passing the messages as an argument to the template:
    return render_template('home.html', messages=data)

# Task 5.3
# def home():
#     if request.method == 'POST':
#         append_message_to_file(request) # task 5.3

#     data = read_messages_from_file() # task 5.3
#     # Return a Jinja HTML template, passing the messages as an argument to the template:
#     return render_template('home.html', messages=data['messages'])
