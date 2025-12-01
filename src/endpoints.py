import numpy as np
import matplotlib.pyplot as plt
import math
import time
from datetime import datetime, timedelta
import os
import sys
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, abort, session
import secrets

app = Flask(__name__)
app.config['data'] = 'data'
app.secret_key = secrets.token_hex()

# This dictionary will store all of the data for all of the different sessions.
# The key is the session_id found in the session array managed by Flask.
ships = {}

def call_algorithm(filename):
    FOLDER_PATH = './data/'
    X = np.loadtxt(FOLDER_PATH+filename, dtype=str, delimiter=',')
    X[:, 0] = np.char.strip(X[:, 0], "[")
    X[:, 1] = np.char.strip(X[:, 1], "]")
    X[:, 2] = np.char.strip(X[:, 2], "{} ")
    X[:, 3] = np.char.strip(X[:, 3], " ")
    ships[session['session_id']].append(X)
    # CALL THE ALGORITHM HERE
    # algorithm(X)

def unique_token():
    while True:
        # Use the number 16 since it's what most encryption services use
        # so it must be pretty good.
        token = secrets.token_urlsafe(16)
        if token not in ships:
            return token

@app.route("/")
def index():
    return render_template("index.html")

# POST request that takes in a file in the body of the request.
# The file should have the key 'file'.
# Saves the file into the 'data' folder.
@app.route('/', methods = ['POST'])
def upload():
    # get the file with the 'file' key from the request
    uploaded_file = request.files['file']

    # if there is a file, handle it
    if uploaded_file.filename != '':
        
        # secure the filename incase it's a dangerous name
        filename = secure_filename(uploaded_file.filename)

        # if it's not a .txt file, throw an error 400 Bad Request
        if filename.split('.')[1] != "txt":
            abort(400)
            return "", 400
        
        # upload the file to the 'data' folder
        uploaded_file.save(os.path.join(app.config['data'], filename))

        # Flask manages an array session[] for us but it lives in the browser
        # cookies so the amount of storage isn't enough for our large grid.
        # To fix this, we use our own dictionary to store info.
        # V stores a session_id in the browser cookies
        session['session_id'] = unique_token()
        ships[session['session_id']] = []

        # call the algorithm portion to do its thing on the info in the file
        call_algorithm(filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)