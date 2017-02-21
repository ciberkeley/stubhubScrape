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

def getFullEventInfo(eventId, eventObject = None):
    # DESCRIPTION: Given an eventId (int), return a json with 3 keys [event, venue, inventory]
    # event: this keys point to an event json created by getEvent
    # venue: this key points to a venue json created by getVenue
    # inventory: this key points to an inventory json created by getEventInventory
    # date: this key points to a date string representing the time data was gathered
    # Number of API calls = 1-2
    full_info = {}
    if eventObject == None:
    	full_info['event'] = getEvent(eventId)
    else:
      full_info['event'] = eventObject
    full_info['inventory'] = getEventInventory(eventId)
    full_info['date'] = str(time())
    return full_info


def searchEvents(latitude, longitude, radius = 40, units = 'mi'):
    # DESCRIPTION: Given the specified location coordinates, find all active stubhub events
    # 		  matching the specified criteria
    #		  This returns a dictionary formatted as {'numFound: int, 'events': list}
    api_calls = 0
    row_index_dict = {x: 500 * x for x in range(1,10)}
    event_url = 'https://api.stubhub.com/search/catalog/events/v3?point={},{}&radius={}&units={}&rows=500&start=0'.format(latitude, longitude, radius, units)
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'
    event_response = requests.get(event_url, headers=headers)
    api_calls += 1
    try:
        eSearchJson = event_response.json()
        numFound_1st = eSearchJson['numFound']
	if 'geoExpansion' in eSearchJson.keys():
            raise(Exception('GeoExpansion activated, poor search criteria'))
    except Exception, e:
        print('ERROR | Could not get search events. Args: {}, {}, {}, {}. Exception: {}. Response: {}'.format(latitude, longitude, radius, units, e, event_response))
	return {'numFound': 0, 'events': []} # Return empty object
    if numFound_1st < 500:
	return eSearchJson
    addition_query_starts = [row_index_dict[x] for x in range(1, int(numFound_1st / 500) + 1)] # Finding if additonal api calls are needed
    event_url2 = 'https://api.stubhub.com/search/catalog/events/v3?point={},{}&radius={}&units={}&rows=500&start={}'
    event_url_list = [event_url2.format(latitude, longitude, radius, units, x) for x in addition_query_starts]
    for curr_url in event_url_list: # Getting additonal event objects as each api call returns max 10 objects
	try:
	    event_response = requests.get(curr_url, headers=headers)
	    api_calls += 1
	    temp_events_list = event_response.json()['events']
	    eSearchJson['events'] = eSearchJson['events'] + temp_events_list
        except Exception, e:
	    print('ERROR | Could not pull event info. Url: {}. Event response: {}. Exception: {}.'.format(curr_url, event_response, e))
    print('SUCCESS | Event query performed. Args: Lat: {}. Lon: {}. Radius: {}. Units: {}. API Calls: {}. Events Returned: {}.'.format(latitude, longitude, radius, units, api_calls, len(eSearchJson['events'])))
    return eSearchJson


login() # Login upon package import
