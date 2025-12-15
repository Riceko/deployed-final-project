import numpy as np
import time
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify, Response
import secrets
import algorithm
import json
import base64

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex())

# Use session storage instead of file system
PARK_Y_COORD = 9
PARK_X_COORD = 1

def log_header():
    time = datetime.now()
    def extend(int):
        output = str(int)
        if int < 10:
            output = '0' + output
        return output
    return extend(time.month) + " " + extend(time.day) + " " + str(time.year) + ": " + extend(time.hour) + ":" + extend(time.minute) + " "

def log(str):
    if 'log_entries' not in session:
        session['log_entries'] = []
    session['log_entries'].append(log_header() + str)
    session.modified = True

def get_ship():
    return session.get('ship_data', {})

def set_ship(data):
    session['ship_data'] = data
    session.modified = True

def grid_index(y, x):
    y_coord = str(y)
    if y < 10:
        y_coord = '0' + y_coord

    x_coord = str(x)
    if x < 10:
        x_coord = '0' + x_coord

    X = np.array(get_ship()['grid'])
    index = np.where((X[:, 0] == y_coord) & (X[:, 1] == x_coord))[0]
    return int(index[0])

def call_algorithm(file_content, filename):
    # Parse file content directly instead of reading from disk
    lines = file_content.decode('utf-8').strip().split('\n')
    X = []
    for line in lines:
        parts = line.split(',')
        if len(parts) >= 3:
            row = [
                parts[0].strip().strip('['),
                parts[1].strip().strip(']'),
                parts[2].strip().strip('{}').strip(),
                parts[3].strip() if len(parts) > 3 else ''
            ]
            X.append(row)
    
    X = np.array(X)
    X = np.hstack((X, np.array([[""] * len(X)]).T))
    
    ship = {}
    ship['grid'] = X.tolist()
    ship['original_filename'] = filename
    ship['original_content'] = file_content.decode('utf-8')

    # log the file opening
    num_containers = len(np.where((X[:, 3] != 'NAN') & (X[:, 3] != 'UNUSED'))[0])
    ending = ' containers on the ship.' if num_containers != 1 else ' container on the ship.'
    
    # Initialize log
    session['log_entries'] = [log_header() + "Window was opened."]
    log("Manifest " + filename + " is opened, there are " + str(num_containers) + ending)

    steps, total_time, costs = algorithm.a_star(X[:, :4])

    output_name = filename.split(".")[0]+"OUTBOUND.txt"
    ship['output_name'] = output_name

    already_balanced = len(steps) == 0

    moves = ' moves' if len(steps) != 1 else ' move'
    minutes = ' minutes' if total_time != 1 else ' minute'
    log("Balance solution found, it will require " + str(len(steps)) + moves + "/" + str(total_time) + minutes + ".")

    if not already_balanced:
        ship['park'] = 'green'
    else:
        ship['park'] = ''

    ship['steps'] = steps.tolist() if len(steps) > 0 else []
    ship['num_steps'] = len(steps)
    ship['current_step_num'] = 0
    ship['total_time'] = int(total_time)
    ship['move_container'] = False
    ship['all_done'] = already_balanced
    ship['costs'] = costs.tolist() if len(costs) > 0 else []

    if not already_balanced and len(steps) > 0:
        index = grid_index(steps[0, 2], steps[0, 3])
        ship['grid'][index][4] = 'red'

    set_ship(ship)

@app.route("/")
def display_start():
    return render_template("start.html")

@app.route('/', methods=['POST'])
def upload():
    uploaded_file = request.files['file']

    if uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)

        if not filename.endswith('.txt'):
            abort(400)
            return "", 400
        
        # Read file content directly into memory
        file_content = uploaded_file.read()
        uploaded_file.close()

        call_algorithm(file_content, filename)
        return redirect(url_for('display_grid'))
    
    return redirect(url_for('display_start'))

@app.route("/grid")
def display_grid():
    return render_template("grid.html")

@app.route('/api/current_grid', methods=['GET'])
def current_grid():
    ship = get_ship()
    return jsonify(
        grid=ship.get('grid', []),
        park_cell=ship.get('park', ''),
        steps=ship.get('steps', []),
        num_steps=ship.get('num_steps', 0),
        current_step_num=ship.get('current_step_num', 0),
        all_done=ship.get('all_done', False),
        total_time=ship.get('total_time', 0),
        costs=ship.get('costs', []),
        file_name=ship.get('output_name', '')
    )

@app.route('/api/next_grid', methods=['POST'])
def next_grid():
    ship = get_ship()
    
    if ship.get('all_done', False):
        return current_grid()

    curr_step = ship['current_step_num']
    steps = ship['steps']
    first_y_coord = steps[curr_step][0]
    first_x_coord = steps[curr_step][1]
    
    if first_y_coord == PARK_Y_COORD and first_x_coord == PARK_X_COORD:
        ship['park'] = ''
    else:
        ship['grid'][grid_index(first_y_coord, first_x_coord)][4] = ''

    second_y_coord = steps[curr_step][2]
    second_x_coord = steps[curr_step][3]
    if second_y_coord == PARK_Y_COORD and second_x_coord == PARK_X_COORD:
        ship['park'] = ''
    else:
        ship['grid'][grid_index(second_y_coord, second_x_coord)][4] = ''

    def to_string(num):
        output = str(num)
        if num < 10:
            output = '0' + output
        return output
    
    coords = steps[curr_step]
    first = "[" + to_string(coords[0]) + "," + to_string(coords[1]) + "]"
    if coords[0] == 9:
        first = "PARK"
    second = "[" + to_string(coords[2]) + "," + to_string(coords[3]) + "]"
    if coords[2] == 9:
        second = "PARK"
    
    real_minutes = ship['costs'][curr_step]
    minutes = "minutes" if real_minutes != 1 else "minute"
    log(str(curr_step + 1) + " of " + str(ship['num_steps']) + ": Move from " + first + " to " + second + ", " + str(real_minutes) + " " + minutes)

    if curr_step >= ship['num_steps'] - 1:
        ship['all_done'] = True
        set_ship(ship)
        return current_grid()

    if ship['move_container']:
        first_index = grid_index(first_y_coord, first_x_coord)
        second_index = grid_index(second_y_coord, second_x_coord)

        # Swap in grid
        ship['grid'][first_index][2], ship['grid'][second_index][2] = ship['grid'][second_index][2], ship['grid'][first_index][2]
        ship['grid'][first_index][3], ship['grid'][second_index][3] = ship['grid'][second_index][3], ship['grid'][first_index][3]

    ship['current_step_num'] += 1
    ship['move_container'] = not ship['move_container']

    new_step_num = ship['current_step_num']
    new_first_y_coord = steps[new_step_num][0]
    new_first_x_coord = steps[new_step_num][1]
    
    if new_first_y_coord == PARK_Y_COORD and new_first_x_coord == PARK_X_COORD:
        ship['park'] = 'green'
    else:
        ship['grid'][grid_index(new_first_y_coord, new_first_x_coord)][4] = 'green'

    new_second_y_coord = steps[new_step_num][2]
    new_second_x_coord = steps[new_step_num][3]
    if new_second_y_coord == PARK_Y_COORD and new_second_x_coord == PARK_X_COORD:
        ship['park'] = 'red'
    else:
        ship['grid'][grid_index(new_second_y_coord, new_second_x_coord)][4] = 'red'

    set_ship(ship)
    return current_grid()

@app.route('/download_manifest')
def download_manifest():
    ship = get_ship()
    
    log("Finished a Cycle. Manifest " + ship['output_name'] + " was written to desktop, and a reminder pop-up to operator to send file was displayed.")
    
    # Generate manifest content from current grid state
    manifest_lines = []
    grid = ship['grid']
    for row in grid:
        line = f"[{row[0]},{row[1]}], {{{row[2]}}}, {row[3]}"
        manifest_lines.append(line)
    
    manifest_content = '\n'.join(manifest_lines)
    
    return Response(
        manifest_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={ship["output_name"]}'}
    )

@app.route('/log', methods=['POST'])
def log_message():
    message = request.form.get('message')
    log(message)
    return redirect(request.referrer or url_for('display_start'))

@app.route('/close')
def close():
    log("Log file was downloaded.")
    
    # Generate log file content
    log_entries = session.get('log_entries', [])
    log_content = '\n'.join(log_entries) + '\n'
    
    time = datetime.now()
    def extend(int):
        output = str(int)
        if int < 10:
            output = '0' + output
        return output
    
    filename = "KeoghsPort" + extend(time.month) + "_" + extend(time.day) + "_" + str(time.year) + "_" + extend(time.hour) + extend(time.minute) + ".txt"
    
    return Response(
        log_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)