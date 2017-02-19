import requests
import base64
import json, simplejson
import pprint
import pandas as pd
import datetime
import pymongo
from pymongo import MongoClient
import time as time1
import email.utils
import stubhubAPI as sh
import requests
from StringIO import StringIO
time = datetime.datetime.now

def getGoogleSheetDf(url):
    # This will created a pandas datframe of the Google Sheet in url
    r = requests.get(url)
    data = r.content
    #df = pd.read_csv(StringIO(data))
    return data

def continuousPullWrite(collection):
    # DESCRIPTION: For each eventId in eventId_list (from ../data/eventId_list.csv') pull full event info
    #   Data will be pulled for each event in eventId_list once daily
    #   Data will NOT be pulled for an event that has already occurred
    #   Data will be stored in collection (mongo)
    history_dict = {} # This will hold info about when a particular event was queried
    while True:
	eventId_df = pd.read_csv('../data/eventId_list.csv')
	eventId_list = list(eventId_df.eventId.map(lambda x: int(x)))
        for eventId in eventId_list:
            curr_day = str(time())[:10]
            try:
                scrapedToday = curr_day in history_dict[str(eventId)]
            except KeyError:
                scrapedToday = False
            if not scrapedToday:
		print('INFO | Pulling info for eventId:{}'.format(eventId))
                fullInfo = sh.getFullEventInfo(eventId) # Get info
		collection.insert_one(fullInfo)
		time1.sleep(6) # To avoid reaching api requests limit (10 requests/min)
                try:
                    history_dict[str(eventId)].append(curr_day) # Add entry to history_dict
                except:
                    history_dict[str(eventId)] = [curr_day]
                print('SUCCESS | Pulled Event Information for eventId:{} on {}'.format(eventId, curr_day))
            else:
                print('WARNING | EventId:{} already scraped on {}. Skipping.'.format(eventId, curr_day))
        today = str(time())[:10]
        doneForToday = sum([(today in x) for x in history_dict.values()]) == len(eventId_list)
        if doneForToday:
            print('INFO | Sleeping for 1 hour... Start Time: {}'.format(time()))
            time1.sleep(60 * 60 * 1) # Sleep for 1 hour
    return None

if __name__ == '__main__':
    print('PROCESS | Starting Daily Stubhub Data Pull. Start Time: {}'.format(time()))
    
	# Setup mongo client
    client = MongoClient('localhost', 27017)
    db = client.shData
    shCollection = db.shCollection
    gsheet_url = 'https://docs.google.com/spreadsheets/d/1b0fzjO_2QrAz8BnH-TX3uw2oPQ_9peFBUal4ls-rVPE/edit?ts=58a0ad80#gid=0'
    eid_df = getGoogleSheetDf(gsheet_url)
    continuousPullWrite(shCollection)

