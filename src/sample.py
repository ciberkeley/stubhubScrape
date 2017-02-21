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

a=shapi.searchEvents(37.782104, -122.422153, 10, 'mi')
shCollection = pymongo.MongoClient().shData.shCollection
