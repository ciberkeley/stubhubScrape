import requests
import base64
import json, simplejson
import pprint
import pandas as pd
import datetime
import email.utils
time = datetime.datetime.now

# Works Cited:https://gist.github.com/ozzieliu #

def login():
    # DESCRIPTION: Login to the stubhub api. You will be prompted for a password
    url = 'https://api.stubhub.com/login'
    ## Enter user's API key, secret, and Stubhub login
    app_token = 'Qkbc3IufMQhlQCODJH_07H6gE5wa'
    consumer_key = 'ZKMRtN_TA2wOfxj0DGIMPv8d2o0a'
    consumer_secret = 'Ia4DTNJUsvq_9TlVnVurh_QZRMEa'
    stubhub_username = 'brandonjflannery@gmail.com'
    stubhub_password = raw_input('Enter Stubhub password: ')

    ## Generating basic authorization token
    combo = consumer_key + ':' + consumer_secret
    basic_authorization_token = base64.b64encode(combo)
    print('SUCCESS | Generated Basic Authorization Token: {}'.format(basic_authorization_token))

    global headers
    headers = {'Content-Type':'application/x-www-form-urlencoded',
                'Authorization':'Basic '+basic_authorization_token}
    body = {
        'grant_type':'password', 'username':stubhub_username,
        'password':stubhub_password, 'scope':'PRODUCTION'
        }
    r = requests.post(url, headers=headers, data=body)
    token_respoonse = r.json()
    global access_token
    access_token = token_respoonse['access_token']
    user_GUID = r.headers['X-StubHub-User-GUID']
    print('SUCCESS | Logged in. User GUID: {}'.format(user_GUID))
    return

def getEvent(eventId):
    # DESCRIPTION: Given an eventId (int), return the event json describing the event
    data = {'eventid':eventId}
    event_url = 'https://api.stubhub.com/catalog/events/v2/{}'.format(data['eventid'])
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'
    event = requests.get(event_url, headers=headers)
    eJson = event.json()
    return eJson

def getVenue(venueId):
    # DESCRIPTION: Given a venueId (int), return the venue json describing the venue
    data = {'venueid':venueId}
    venue_url = 'https://api.stubhub.com/catalog/venues/v2/{}'.format(venueId)
    
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'

    venue = requests.get(venue_url, headers=headers)
    vJson = venue.json()
    return vJson

def getEventInventory(eventId):
    # DESCRIPTION: Given an eventId (int), return the event-inventory json describing the events inventory metadata
    data = {'eventId':eventId}
    event_inv_url = 'https://api.stubhub.com/search/inventory/v2'
    #event_inv_url = 'https://api.stubhubsandbox.com/inventory/listings/v1'
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'

    eventInv = requests.get(event_inv_url, headers=headers, params = data)
    eiJson = eventInv.json()
    return eiJson

def getFullEventInfo(eventId):
    # DESCRIPTION: Given an eventId (int), return a json with 3 keys [event, venue, inventory]
    # event: this keys point to an event json created by getEvent
    # venue: this key points to a venue json created by getVenue
    # inventory: this key points to an inventory json created by getEventInventory
    # date: this key points to a date string representing the time data was gathered
    full_info = {}
    full_info['event'] = getEvent(eventId)
    full_info['venue'] = getVenue(full_info['event']['venue']['id'])
    full_info['inventory'] = getEventInventory(eventId)
    full_info['date'] = str(time())
    return full_info


login() # Login upon package import
