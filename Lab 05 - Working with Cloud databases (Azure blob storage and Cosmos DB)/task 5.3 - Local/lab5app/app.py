import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request


class Config(object):
    SECRET_KEY = 'lab5kadalipp'
    # UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/images')
    UPLOAD_FOLDER = 'static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


app = Flask(__name__)
app.config.from_object(Config)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'gif'}


def read_messages_from_file():
    """ Read all messages from a JSON file"""
    with open('data.json') as messages_file:
        return json.load(messages_file)


def append_message_to_file(request):
    """ Read the contents of JSON file, add this message to it's contents, then write it back to disk. """
    image_path = ''
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(str(uuid.uuid4()) + file.filename[-4:])
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

    data = read_messages_from_file()
    new_message = {
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
        append_message_to_file(request)
    data = read_messages_from_file()
    # Return a Jinja HTML template, passing the messages as an argument to the template:
    return render_template('home.html', messages=data['messages'])
