import requests
import base64
import json, simplejson
import pprint
import pandas as pd
import datetime
import email.utils

# Works Cited:https://gist.github.com/ozzieliu #
#### Step 1: # Obtaining StubHub User Access Token ####

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

## POST parameters for API call
headers = {
        'Content-Type':'application/x-www-form-urlencoded',
        'Authorization':'Basic '+basic_authorization_token,}

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

    headers = {'Content-Type':'application/x-www-form-urlencoded',
                'Authorization':'Basic '+basic_authorization_token}
    body = {
        'grant_type':'password', 'username':stubhub_username,
        'password':stubhub_password,  'scope':'PRODUCTION'
        }
    r = requests.post(url, headers=headers, data=body)
    token_respoonse = r.json()
    access_token = token_respoonse['access_token']
    user_GUID = r.headers['X-StubHub-User-GUID']
    print('SUCCESS | Logged in. User GUID: {}'.format(user_GUID))
    return

def getEvent(eventId):
    # DESCRIPTION: Given an eventId (int), return the event json describing the event
    data = {'eventId':eventId}
    inventory_url = 'https://api.stubhub.com/catalog/events/v2/{}'.format(data['eventId'])

    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'

    event = requests.get(event_url, headers=headers, params=data)
    eJson = event.json()
    return eJson

## Flattening some nested dictionary for ticket price
for t in listing:
    for k,v in t.items():
        if k == 'currentPrice':
            t['amount'] = v['amount']
## Converting to Pandas dataframe and exporting to CSV
listing_df = pd.DataFrame(listing)
listing_df.to_csv(open('export.csv', 'wb'))

#### Step 3 - Adding Event and Venue Info ####

## Calling the eventsearch api
info_url = 'https://api.stubhub.com/catalog/events/v2/' + eventid
info = requests.get(info_url, headers=headers)

pprint.pprint(info.json())

info_dict = info.json()
event_date = datetime.datetime.strptime(info_dict['eventDateLocal'][:10], '%Y-%m-%d')

full_title = info_dict['title'].split('[', 2)
event_name = full_title[0].strip()
event_date = full_title[1][:10]

venue = info_dict['venue']['name']
snapshotdate = datetime.datetime.today().strftime('%m/%d/%Y')

my_col = ['SnapshotDate','EventName','EventDate', 'Venue', 'sectionName', 'row',
          'seatNumbers', 'quantity', 'deliveryTypeList', 'amount']
listing_df['SnapshotDate'] = snapshotdate
listing_df['EventName'] = event_name
listing_df['EventDate'] = event_date
listing_df['Venue'] = venue
final_df = listing_df[my_col]

## Exporting final report
final_df.to_csv(open('export.csv', 'wb'), index=None)
