import os
import json
import requests
import urllib.parse
import tweet_auth as tweet
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions

# ############## The connections to the twitter were based on 
# https://developer.twitter.com/en/docs/tutorials/how-to-analyze-the-sentiment-of-your-own-tweets


#################################
# Twitter setup
#################################

def create_twitter_url(location="San Francisco"):
    max_results = 10
    mrf = f"max_results={max_results}"
    search = urllib.parse.quote("car crash OR fire OR tornado OR earthquake OR flood")
    search = "(" + search +")"
    query = urllib.parse.quote(f'-is:retweet entity:"{location}"')
    query = "query=" + search + query
    url = f"https://api.twitter.com/2/tweets/search/recent?{mrf}&{query}"
    return url

def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.request("GET", url, headers=headers)
    return response.json()

#################################
# IBM setup
#################################

def check_categories(string):
    """
    Checks if a our desired categories is contained within the category string of returned results

    >>> check_categories("/family and parenting/babies and toddlers/baby clothes")
    False
    >>> check_categories("/science/weather/meteorological disaster")
    True

    """
    categories = ["/society/crime", "disaster", "fire department", "news"]
    for category in categories:
        if category in string:
            return True
    return False


def build_authenticator(data):
    apikey = data["ibm"]["subscription_key"]
    authenticator = IAMAuthenticator(f"{apikey}")
    return authenticator

def build_ibm_url(authenticator, data):
    natural_language_understanding = NaturalLanguageUnderstandingV1(    
    version='2021-03-25',
    authenticator=authenticator)
    url = data["ibm"]["url"]
    natural_language_understanding.set_service_url(f'{url}')
    return natural_language_understanding

def analyze(natural_language_understanding, tweets):
    sentiment_list = []
    try:
        tweets = tweets['data']
        print(tweets)
    except:
        print("tweets were not returned correctly")
    try:
        for tweet in tweets:
            tweet_text = tweet["text"]
            response = natural_language_understanding.analyze(
            text=f'{tweet_text}',
            features=Features(
                entities=EntitiesOptions(sentiment=True, limit=2),
                keywords=KeywordsOptions(sentiment=True,limit=2),
                categories=CategoriesOptions(explanation=True,limit=3)
                )).get_result()
            response_json = json.dumps(response)
            if response["categories"][0]["score"] > 0.75 and check_categories(response["categories"][0]["label"]):
                sentiment_list += [tweet, response_json]
                print("sentiment list at the end of one tweet")
                print(sentiment_list)
    except Exception as e:
        print("json response was not filtered properly", e)
    return sentiment_list

#################################
# Main
#################################

def tweets_main(location="San Francisco"):
    url = create_twitter_url(location)
    data = tweet.process_yaml()
    bearer_token = tweet.create_bearer_token(data)
    res_json = twitter_auth_and_connect(bearer_token, url)
    authenticator = build_authenticator(data)
    natural_language_understanding = build_ibm_url(authenticator, data)
    sentiments = analyze(natural_language_understanding, res_json)
    return sentiments

if __name__ == "__main__":
    tweets_main()