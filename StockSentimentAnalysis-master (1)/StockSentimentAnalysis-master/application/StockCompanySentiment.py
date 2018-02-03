import time
import arrow
import re
import requests
import json
import MySQLdb as mdb
import pandas as pd
import matplotlib.pyplot as plt
from slackclient import SlackClient

host = '34.235.205.203'
username = 'root'
password = 'dwdstudent2015'
database = 'ArticlesSentiment'

def message_is_for_our_bot(user_id, message_text):

    regex_expression = '.*@' + user_id + '.*bot.*'
    regex = re.compile(regex_expression)
    # Check if the message text matches the regex above
    match = regex.match(message_text)
    # returns true if the match is not None (ie the regex had a match)
    return match != None

def extract_company_name(message_text):

    message_text = message_text.lower()
    regex_expression = 'stock prediction for (.+)'
    regex= re.compile(regex_expression)
    matches = regex.finditer(message_text)
    for match in matches:
        # return the captured phrase
        # which comes after 'in'
        return match.group(1) 
    # if there were no matches, return None
    return None
def dynamically_get_company_details(company_name):
    '''
    Returns the details of the company from Dynamic API
    '''
    url = 'http://34.235.205.203:5000/api/company?company_name=' + company_name
    data = requests.get(url).json()
    avg_score = 0
    for i in data[:5]:
        avg_score += i['score']
    avg_score/=5
    message_list = [data[0]['company'], data[0]['article_url'], avg_score]
    return message_list

def create_message(company_name):
    '''
    This function takes as input the username of the user that asked the question,
    and the city_name that we managed to extract from the question (potentially it can be None)
    We check the Openweather API and respond with the weather condiitons in the city.
    '''
    message = ''
    if company_name != None:
        # We want to address the user with the username. Potentially, we can also check
        # if the user has added a first and last name, and use these instead of the username
        message += "Thank you for asking about the stock prediction for " + company_name + '\n'


        matching_company = dynamically_get_company_details(company_name)
        # If we cannot find any matching city...
        company_name = matching_company[0]
        news_article_URL = matching_company[1]
        sentiment_rating = float(matching_company[2])
        message += "\nLatest article about " + company_name + "\n" +\
            "Article URL is " + news_article_URL +"\n"
        if int(sentiment_rating*100) > 50:
            sentiment_rating = (sentiment_rating*100)
            message += "Probability of stock rising in the coming days becuase of the article is " +\
                str(sentiment_rating) + "%"
        else:
            sentiment_rating = -((sentiment_rating*100)%-100)
            message += "Probability of stock falling in the coming days becuase of the article is " +\
                str(sentiment_rating) + "%"
    else:
        message += "Unfortunately I did not understand the city you are asking for.\n"
        message += "Ask me `stock prediction for {name of company}` and I will try to answer."
    return message

def process_slack_event(event):
    '''
    The Slack RTM (real time messaging) generates a lot of events.
    We want to examine them all but only react to:
    1. Messages
    2. ...that come from a user
    3. ...that ask our bot to do something
    4. ...and act only for messages for which we can extract the data we need
    
    
    '''
    
    # Check that the event is a message. If not, ignore and proceed to the next event.
    if event.get("type") != 'message':
        return None

    # Check that the message comes from a user. If not, ignore and proceed to the next event.
    # We do not reply to bots, to avoid getting into infinite loops of discussions with other bots
    if event.get("user") == None:
        return None

    # Check that the message is asking the bot to do something. If not, ignore and proceed to the next event.
    message_text = event.get('text')
    if not message_is_for_our_bot(bot_user_id, message_text):
        return None

    # Extract the company name from the user's message
    company_name = extract_company_name(message_text)

    # Prepare the message that we will send back to the user
    message = create_message(company_name)

    return message
if __name__ == "__main__":
    auth_token = "xoxp-237811062240-249700956231-264640927623-43e4a64bb0bbb2f4798b2197db644710"
    bot_user_id = 'U7BLLU46T'
    # Connect to the Real Time Messaging API of Slack and process the events
    sc = SlackClient(auth_token)
    sc.rtm_connect()

    # We are going to be polling the Slack API for recent events continuously
    while True:
        # We are going to wait 1 second between monitoring attempts
        time.sleep(1)
        # If there are any new events, we will get a list of events. 
        # If there are no events, the response will be empty
        events = sc.rtm_read()
        for event in events:
            # Check if we should generate a response for the event
            response = process_slack_event(event)
            if response:
                # Post a message to Slack with our response
                message = response
                sc.api_call("chat.postMessage", channel="#company_stock", text=message)
