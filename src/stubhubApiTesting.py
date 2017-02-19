import requests
import base64
import json, simplejson
import pprint
import pandas as pd
import datetime
import email.utils
import stubhubAPI as sh
time = datetime.datetime.now



if __name__ == '__main__':
    eventId = raw_input('EventId: ')
    event = sh.getEvent(eventId)
    venue = sh.getVenue(event['venue']['id'])
    print '--\nEvent: {}\n--'.format(event)
    print '--\nVenue: {}\n--'.format(venue)
    eiJson = sh.getFullEventInfo(eventId)

