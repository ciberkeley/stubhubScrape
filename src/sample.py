import stubhubAPI as shapi
import pymongo
import base64
import requests

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

login()

def get():
    # DESCRIPTION: Given an eventId (int), return the event json describing the event
    event_url = 'https://api.stubhub.com/search/catalog/events/v2?id=9812696'
    event_url = 'https://api.stubhub.com/search/catalog/events/v3?point=40.2,-83.1&radius=120&minAvailableTickets=1&date=2014-06-01T00:00 TO 2014-06-01T23:59&sort=distance asc HTTP/1.1'
    print event_url
    #data = {'query': "title=Warriors"}
    headers['Authorization'] = 'Bearer ' + access_token
    headers['Accept'] = 'application/json'
    headers['Accept-Encoding'] = 'application/json'
    event = requests.get(event_url, headers=headers)
    print event
    eJson = event.json()
    return eJson
a=get()
