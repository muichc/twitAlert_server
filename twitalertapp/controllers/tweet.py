from flask import jsonify, Blueprint, request as flask_request
from flask_jwt_extended import jwt_required, get_jwt_identity
from twitalertapp.extensions import mongo, flask_bcrypt, jwt, JSONEncoder
from twitalertapp.tweets import tweet_main
import requests
from requests.auth import HTTPBasicAuth
from twitalertapp.settings import ZIP_API_KEY2, ZIP_API_EMAIL2, ZIP_API_PASSWORD2

tweet = Blueprint('tweet', __name__)

@tweet.route('/user/tweets', methods=["GET"])
@jwt_required(refresh=False, locations=['headers'])
def get_tweet():
    current_user_id = get_jwt_identity()
    current_user = mongo.db.users.find_one({'_id': current_user_id})
    zip_url = f"https://service.zipapi.us/zipcode/{current_user['location']}?X-API-KEY={ZIP_API_KEY2}"
    response = requests.get(zip_url, auth=HTTPBasicAuth(ZIP_API_EMAIL2, ZIP_API_PASSWORD2))
    response_json = response.json()
    location = response_json["data"]["city"]
    tweets = tweet_main(location)
    print("LENGTH OF TWEETS WE GOT IS ", len(tweets), " AND THE TWEETS ARE >>>>>", tweets)
    return jsonify({"response": tweets}), 200