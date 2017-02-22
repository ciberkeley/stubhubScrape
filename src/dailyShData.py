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
    # DESCRIPTION: For each location row in (from ../data/locationSearch_official.csv') pull full event info
    #   Data will be pulled for each event in event in the search results once daily
    #   Data will NOT be pulled for an event that has already occurred
    #   Data will be stored in collection (mongo)
    st = time()
    api_calls = 0
    history_dict_by_day = {} # This will hold info about when a particular location was queried
    history_dict_by_eventId = {} # This will hold info about when a particular event was queried
    localSearch_df = pd.read_csv('../data/locationSearch_official.csv') # Lat, long, radius info
    while True: # Infinite loop (ends when program is interrupted)
        for row_index in localSearch_df.index: # Loop through locations to search through
            lat, lon, rad, units, name = localSearch_df.ix[row_index][['lat', 'lon', 'rad', 'units', 'name']]
            curr_day = str(time())[:10]
            try: # Check if we've searched this location today
                scrapedToday = [lat, lon] in history_dict_by_day[curr_day]
            except KeyError:
                scrapedToday = False
            if not scrapedToday:
                print('LOCATION SEARCH | Searching for events around lat:{}, lon:{}, radius:{}, name:{}'.format(lat, lon, rad, name))
                search_response = sh.searchEvents(lat, lon, rad, units)
                api_calls += int(len(search_response['events']) / 500) + 1
                print('SUCCESS | Location search returned {} events.'.format(len(search_response['events'])))
                for event_object in search_response['events']: # get full event info across location results
                    try: # Get event info and add to mongo
                        fullInfo = sh.getFullEventInfo(int(event_object['id']), event_object) # takes .4 sec, 1 api calls with event_object supplied
                        collection.insert_one(fullInfo)
                        time1.sleep(6) # To avoid reaching api requests limit (10 requests/min). Currently at 1 api calls per loop
                        api_calls += 1
                        try:
                            history_dict_by_eventId[event_object['id']].append(curr_day) # add entry to event query log
                        except:
                            history_dict_by_eventId[event_object['id']] = [curr_day]
                    except Exception, e:
                        print('ERROR | Could not pull and store event information for event:{}. Exception: {}'.format(event_object['id'], e))
                        api_calls += 1
                        time1.sleep(6)
                        continue
                try:
                    history_dict_by_day[curr_day].append([lat, lon]) # Add entry to location search log
                except:
                    history_dict_by_day[curr_day] = [[lat, lon]]
                print('SUCCESS | Pulled Event Information for {} on {}. Time/apiCall: {}. Mongo Collection Size: {}'.format(name, curr_day, (time() - st) / api_calls, collection.count()))
            else:
                print('WARNING | Location: {},{},{} already scraped on {}. Skipping.'.format(lat, lon, rad, curr_day))
            today = str(time())[:10]
            doneForToday = len(history_dict_by_day[today]) == len(localSearch_df) # We searched all locations
            if doneForToday:
                print('SLEEP | Searched all locations for today. Sleeping for 1 hour... Start Time: {}'.format(time()))
                time1.sleep(60 * 60 * 1) # Sleep for 1 hour
        # continue to another event search
    return None

if __name__ == '__main__':
    print('PROCESS | Starting Daily Stubhub Data Pull. Start Time: {}'.format(time()))
    
	# Setup mongo client
    client = MongoClient('localhost', 27017)
    db = client.shData
    shCollection = db.shCollection
    print('SUCCESS | Loaded MongoDB client.')
    #gsheet_url = 'https://docs.google.com/spreadsheets/d/1b0fzjO_2QrAz8BnH-TX3uw2oPQ_9peFBUal4ls-rVPE/edit?ts=58a0ad80#gid=0'
    #eid_df = getGoogleSheetDf(gsheet_url)
    continuousPullWrite(shCollection)

