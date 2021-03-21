from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, abort
from flask_cors import CORS
from flask_api import status
from datetime import date, datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse
import pytz
import os
import sys
import time
import uuid
import json
import random
import string
import pathlib
import io
from uuid import UUID
from bson.objectid import ObjectId

# straight mongo access
from pymongo import MongoClient

# mongo
# mongo "mongodb+srv://uber.c7iad.mongodb.net/myFirstDatabase" --username vaibhav
# mongo_client = MongoClient('mongodb://localhost:27017/')
# mongo_client = MongoClient("mongodb+srv://admin:admin@tweets.8ugzv.mongodb.net/tweets?retryWrites=true&w=majority")
mongo_client = MongoClient("mongodb+srv://vaibhav:vaibhav@uber.c7iad.mongodb.net/Uber?retryWrites=true&w=majority")

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
bookings = dict()


################
# Apply to mongo
################

# def atlas_connect():
#     # Node
#     # const MongoClient = require('mongodb').MongoClient;
#     # const uri = "mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
#     # const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
#     # client.connect(err => {
#     # const collection = client.db("test").collection("devices");
#     # // perform actions on the collection object
#     # client.close();
#     # });

#     # Python
#     client = pymongo.MongoClient(
#         "mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
#     db = client.test


# database access layer
def insert_one(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['Uber']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_one() to mongo: ", r)
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.insert_one(r)
            print("inserted _ids: ", result.inserted_id)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) +
          " microseconds to insert_one.")


def tryexcept(requesto, key, default):
    lhs = None
    try:
        lhs = requesto.json[key]
        # except Exception as e:
    except:
        lhs = default
    return lhs

# seconds since midnight


def ssm():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return str((now - midnight).seconds)


################################################
# Tweets
################################################

# endpoint to create new booking
@app.route("/book", methods=["POST"])
def add_booking():
    user = request.json['user']
    source = request.json['source']
    destination = request.json['destination']
    date = request.json['date']
    pic = request.json['pic']

    for key, value in bookings.items():
        if(value['user'] == user and value['source'] == source and value['destination'] == destination and value['date'] == date):
            return jsonify({"msg": "Same Booking Already Present"})

    booking = dict(user=user, source=source, destination=destination,
                   date=date, pic=pic, _id=str(ObjectId()))
    bookings[booking['_id']] = booking

    insert_one(booking)
    return jsonify(booking)


# endpoint to show all bookings


@app.route("/bookings", methods=["GET"])
def get_bookings2():
    # for tweet in tweets:
    #         print(tweet)
    return json.dumps({"results": bookings})


@app.route("/bookings-results", methods=["GET"])
def get_booking_results():
    applyCollectionLevelUpdates()
    return json.dumps({"results":
                       sorted(
                           bookings.values(),
                           key=lambda t: t['date']
                       )
                       })

##################
# Apply from mongo
##################


def applyRecordLevelUpdates():
    return None


def applyCollectionLevelUpdates():
    global bookings
    with mongo_client:
        db = mongo_client['Uber']
        mongo_collection = db['bookings']

        cursor = mongo_collection.find({})
        records = list(cursor)

        howmany = len(records)
        print('found ' + str(howmany) + ' bookings!')
        sorted_records = sorted(records, key=lambda t: t['source'])
        
        for book in sorted_records:
            bookings[book['_id']] = book


################################################
# Mock
################################################
@app.route("/")
def home():
    return """Welcome to online mongo/Uber testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/bookings<br />
        http://localhost:5000/bookings-results<br /
        """


# add new tweet, for testing
@app.route("/dbg-uber", methods=["GET"])
def dbg_tweet():
    with app.test_client() as c:
        json_data = []
        name = ''.join(random.choices(string.ascii_lowercase, k=7))
        description = ''.join(random.choices(string.ascii_lowercase, k=50))
        print("posting..")
        rv = c.post('/tweet', json={
            'user': name, 'description': description,
            'private': False, 'pic': None
        })
    return rv.get_json()


# # endpoint to mock tweets
# @app.route("/mock-tweets", methods=["GET"])
# def mock_tweets():

#     # first, clear all collections
#     global tweets
#     tweets.clear()

#     # create new data
#     json_data_all = []
#     with app.test_client() as c:

#         # tweets: 30
#         print("@@@ mock-tweets(): tweets..")
#         json_data_all.append("@@@ tweets")
#         for i in range(30):
#             description = []
#             private = random.choice([True, False])
#             for j in range(20):
#                 w = ''.join(random.choices(
#                     string.ascii_lowercase, k=random.randint(0, 7)))
#                 description.append(w)
#             description = ' '.join(description)
#             u = ''.join(random.choices(string.ascii_lowercase, k=7))
#             img_gender = random.choice(['women', 'men'])
#             img_index = random.choice(range(100))
#             img_url = 'https://randomuser.me/api/portraits/' + \
#                 img_gender + '/' + str(img_index) + '.jpg'
#             rv = c.post('/tweet', json={
#                 'user': u, 'private': private,
#                 'description': description, 'pic': img_url
#             })
#             # json_data.append(rv.get_json())
#         json_data_all.append(tweets)

#     # done!
#     print("@@@ mock-tweets(): done!")
#     return jsonify(json_data_all)


##################
# ADMINISTRATION #
##################

# This runs once before the first single request
# Used to bootstrap our collections
@app.before_first_request
def before_first_request_func():
    applyCollectionLevelUpdates()

# This runs once before any request


@app.before_request
def before_request_func():
    applyRecordLevelUpdates()


############################
# INFO on containerization #
############################

# To containerize a flask app:
# https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
