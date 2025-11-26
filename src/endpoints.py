import numpy as np
import matplotlib.pyplot as plt
import math
import time
from datetime import datetime, timedelta
import os
import sys
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/uploadfile', methods = ['POST'])
def upload():
    pass

if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     file_name = input('Enter the name of file: ')
#     FOLDER_PATH = './data/'
#     name = file_name.split('.')[0]

#     # if the file doesn't exist, exit
#     if not os.path.exists(FOLDER_PATH+file_name):
#         print(f"The file {FOLDER_PATH+file_name} does not exist.")
#         sys.exit(1)

#     X = np.loadtxt(FOLDER_PATH+file_name, dtype=str, delimiter=',')
#     print(X[0])
#     X[:, 0] = np.char.strip(X[:, 0], "[")
#     X[:, 1] = np.char.strip(X[:, 1], "]")
#     X[:, 2] = np.char.strip(X[:, 2], "{} ")
#     X[:, 3] = np.char.strip(X[:, 3], " ")
#     print(X[0])