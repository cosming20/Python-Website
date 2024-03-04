from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from functions import filter_events
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import os
import json
from pymongo import MongoClient

client = MongoClient('mongodb+srv://cosminionutgagea:barbosuetare@cluster0.zcscweb.mongodb.net/')
db = client['PythonProject']
collection = db['Users']

app = Flask(__name__)
app.secret_key = os.urandom(24)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password = str(password )
        user = collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])   
            return redirect(url_for('home', id = user['_id']))

    return render_template('login.html')

@app.route('/')
def startpage():
    return render_template('startpage.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ""
    if request.method == 'POST':
        username = request.form['username']

        if username:
            user = collection.find_one({'username': username})
            if user:
                message = "User already exist"
                return render_template('signup.html',message=message)
        mail = request.form['mail']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user_data = {'username': username, 'mail':mail, 'password': hashed_password}
        collection.insert_one(user_data)

        return redirect(url_for('login'))

    return render_template('signup.html',message=message)

@app.route('/users/<id>', methods = ['GET'])
@login_required
def home(id):
    id = ObjectId(id)
    user = collection.find_one({'_id': id})
    if 'events' in user:
        events = user['events']
    else:
        events = []
    return render_template('mainpage.html', user = user, events = events)

@app.route('/users/<id>/events', methods=['GET','POST'])
@login_required
def events_page(id):
    id = ObjectId(id)
    user = collection.find_one({'_id': id})
    title_filter = request.args.get('titleFilter', default='')  
    if title_filter is None:
        title_filter = ''
    date_filter = request.args.get('dateFilter')
    if 'events' in user:
        events = user['events']
    else:
        events = []
    if 'clearFilters' in request.args:
        title_filter = ""
        date_filter = None

    # Filter events based on title and date
    filtered_events = filter_events(events, title_filter, date_filter)
    return render_template('events.html', filtered_events=filtered_events, user=user)


@app.route('/users/<id>/calendar', methods=['GET', 'POST'])
@login_required
def calendar(id):
    id = ObjectId(id)
    user = collection.find_one({'_id': id})
    if user and 'events' in user:
        events = user['events']
    else:
        events = []

    return render_template('calendar.html', calendarEvents=json.dumps(events), user=user)

@app.route('/users/<id>/add_event', methods=['GET', 'POST'])
@login_required
def add_event(id):
    global events
    id = ObjectId(id)
    user = collection.find_one({'_id': id})
    if 'events' in user:
        events = user['events']
    else:
        events = []
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        time = request.form.get('time')
        event = {'title': title, 'date': date, 'time': time}
        events.append(event)
        print(events)
        collection.update_one({'_id': id}, {'$set': {'events': events}})

    return render_template('index.html', user=user)

@app.route('/users/<id>/edit_event', methods=['GET', 'POST'])
@login_required
def edit_event_route(id):
    message = ""
    user_id = ObjectId(id)
    if request.method == 'POST':
        old_time = request.form.get('old_time')
        new_title = request.form.get('new_title')
        new_date = request.form.get('new_date')
        new_time = request.form.get('new_time')
        collection.update_one(
            {'_id': user_id, 'events.time': old_time},
            {'$set': {'events.$.title': new_title, 'events.$.date': new_date, 'events.$.time': new_time}})
        message = "Event edited successfully"
        return redirect(url_for('events_page', id=user_id))
    return render_template('events.html', events=events, message=message)

@app.route('/users/<id>/delete_event', methods=['POST'])
@login_required
def delete_event_route(id):
    global events
    user_id = ObjectId(id)
    if request.method == 'POST':
        time_to_delete = request.form.get('time_to_delete')
        collection.update_one({'_id': user_id}, {'$pull': {'events': {'time': time_to_delete}}})
        message = "Event deleted successfully"
        return redirect(url_for('events_page', id = user_id))

    return render_template('events.html', events=events, message=message)

if __name__ == '__main__':
    app.run(debug=True)
