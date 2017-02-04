import pandas as pd
import numpy as np
import requests
import re

discovery_root_url = 'https://app.ticketmaster.com/discovery/v2/'

def getEvents():
    # DESCRIPTION: Get All Event Jsons. Return a list of event jsons
    all_events_request = 'https://app.ticketmaster.com/discovery/v2/events.json?apikey=qDPfiZcjOMUmxf8zoUbGvUFJkGqKTkx9'
    all_events_json = requests.get(all_events_request).json()
    events_list = all_events_json['_embedded']['events']
    print('SUCCESS | Pulled all events through Discovery API. Total Events: {}'.format(len(events_list)))
    return events_list

def getPriceJsonList(eventJson):
    # DESCRIPTION: Get price range list of price-info jsons from a given event json
    priceRanges_json_list = eventJson['priceRanges']
    return priceRanges_json_list

def getSalesJson(eventJson):
    # DESCRIPTION: Get on-sale information for the given event json, including presale information
    sale_json = eventJson['sales']
    return sale_json

def getDateJson(eventJson):
    # DESCRIPTION: Get event date information given an event json
    date_json = eventJson['dates']
    return date_json


if __name__ == '__main__':
    events_list = getEvents()
    print('EVENT | {}: {}'.format(events_list[0]['name'], events_list[0]['url']))
    priceJson_list = getPriceJsonList(events_list[0])
    print('PRICE | {}'.format(priceJson_list))
    sales_json = getSalesJson(events_list[0])
    print('SALE | {}'.format(sales_json))
    date_json = getDateJson(events_list[0])
    print('DATE | {}'.format(date_json))




