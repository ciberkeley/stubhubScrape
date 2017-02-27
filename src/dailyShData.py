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

def scrapedToday(history_dict_by_day, day, lat, lon):
    # Given a history_dict_by_day containing {day: [lat, lon]} mappings, determine whether
    # the lat, long pair was scraped on the given day 
    try: # Check if we've searched this location today
        scrapedToday = [lat, lon] in history_dict_by_day[day]
    except KeyError:
        scrapedToday = False    
    return scrapedToday

def addEventInfoByVenue(event_json_list, shCollection, venue_id_list, history_dict_by_eventId):
    # Given a list of event jsons, a mongo collection object, and a list of venue ids,
    # Filter through the event json list for events matching a venue in venue_id_list.
    # For all matching events, use sh.getFullEventInfo to get the inventory data,
    # and add the resulting full event info json to shCollection
    # NOTE: This method will also record the number of API calls made and will limit the 
    #       speed of API calls to not exceed the request limit of 10 calls/min
    api_calls = 0
    st = time()
    filtered_event_list = [x for x in event_json_list if x['venue']['id'] in venue_id_list]
    print('addEventInfoByVenue | Kept {}/{} event observations after venueId filtering.'.format(len(filtered_event_list), len(event_json_list)))
    del event_json_list # free memory
    for event_object in filtered_event_list:
        try: # Get event info and add to mongo
            curr_day = str(time())[:10]
            fullInfo = sh.getFullEventInfo(int(event_object['id']), event_object) # takes .4 sec, 1 api calls with event_object supplied
            shCollection.insert_one(fullInfo)
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
    total_time = time() - st
    api_call_rate = api_calls
    string_format = [len(filtered_event_list), total_time, api_call_rate]
    print('addEventInfoByVenue | Completed Full Event Info pull for {} observations. Time: {}. apiCall:'.format(*string_format))
    return history_dict_by_eventId


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
    venueId_df = pd.read_csv('../data/venueIdSearch_official.csv') # venueId info
    while True: # Infinite loop (ends when program is interrupted)
        localSearch_df = pd.read_csv('../data/locationSearch_official.csv') # Reload every loop
        venueId_df = pd.read_csv('../data/venueIdSearch_official.csv') # Reload every loop
        venueId_list = list(venueId_df.venueId)
        locSearch_names = list(localSearch_df.name)
        print('LocationSerch | Searching through locations: {}'.format(locSearch_names))
        for row_index in localSearch_df.index: # Loop through locations to search through
            lat, lon, rad, units, name = localSearch_df.ix[row_index][['lat', 'lon', 'rad', 'units', 'name']]
            curr_day = str(time())[:10]
            scraped_today = scrapedToday(history_dict_by_day, curr_day, lat, lon)
            if not scraped_today:
                print('LocationSearch | Searching for events around lat:{}, lon:{}, radius:{}, name:{}'.format(lat, lon, rad, name))
                search_response = sh.searchEvents(lat, lon, rad, units)
                api_calls += int(len(search_response['events']) / 500) + 1
                print('LocationSearch | Location search returned {} events.'.format(len(search_response['events'])))
                history_dict_by_eventId = addEventInfoByVenue(search_response['events'][:5], collection, venueId_list, history_dict_by_eventId)
                try:
                    history_dict_by_day[curr_day].append([lat, lon]) # Add entry to location search log
                except:
                    history_dict_by_day[curr_day] = [[lat, lon]]
                string_format = [name, curr_day, (time() - st) / api_calls, collection.count()]
                print('LocationSearch | Pulled Full Event Information for {} on {}. Time/apiCall: {}. Mongo Collection Size: {}'.format(*string_format))
                string_format = [len(history_dict_by_day[curr_day]), len(localSearch_df), history_dict_by_day[curr_day]]
                print('LocationSearch | {}/{} lat, long corrdinates searched today: {}'.format(*string_format))
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
    # $ stdbuf -oL python -W ignore dailyShData.py > log/dailyShData_YYYYMMDD_I.log
    print('PROCESS | Starting Daily Stubhub Data Pull. Start Time: {}'.format(time()))
    
	# Setup mongo client
    client = MongoClient('localhost', 27017)
    db = client.shData
    shCollection = db.shCollection
    print('SUCCESS | Loaded MongoDB client.')
    #gsheet_url = 'https://docs.google.com/spreadsheets/d/1b0fzjO_2QrAz8BnH-TX3uw2oPQ_9peFBUal4ls-rVPE/edit?ts=58a0ad80#gid=0'
    #eid_df = getGoogleSheetDf(gsheet_url)
    continuousPullWrite(shCollection)

