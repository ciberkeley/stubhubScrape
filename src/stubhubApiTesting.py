import requests
import base64
import json, simplejson
import pprint
import pandas as pd
import datetime
import email.utils

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
    event_inv_url = 'https://api.stubhub.com/search/inventory/v1'
    print('Using: {}'.format(event_inv_url))
    #event_inv_url = 'https://api.stubhubsandbox.com/inventory/listings/v1'
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'

    eventInv = requests.get(event_inv_url, headers=headers, params = data)
    print eventInv
    eiJson = eventInv.json()
    print eiJson
    return eiJson

if __name__ == '__main__':
    login()
    eventId = raw_input('EventId: ')
    event = getEvent(eventId)
    venue = getVenue(event['venue']['id'])
    print '--\nEvent: {}\n--'.format(event)
    print '--\nVenue: {}\n--'.format(venue)
    eiJson = getEventInventory(eventId)

