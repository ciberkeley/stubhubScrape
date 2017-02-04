import pandas as pd
import numpy as np
import requests
import re, smtplib, datetime
time = datetime.datetime.now

discovery_root_url = 'https://app.ticketmaster.com/discovery/v2/'

def getEvents(max_count = 1000):
    # DESCRIPTION: Get All Event Jsons. Return a list of event jsons
    # num: max number of events to pull
    page = 0
    events_list = []
    base_request_url = 'https://app.ticketmaster.com/discovery/v2/events.json?size=20&page={}&apikey=qDPfiZcjOMUmxf8zoUbGvUFJkGqKTkx9'
    while True: # Get 20 events at a time until there are no more events left to gather
        all_events_request = base_request_url.format(page)
        all_events_json = requests.get(all_events_request).json()
        try:
            [events_list.append(x) for x in all_events_json['_embedded']['events']] # Add event jsons
        except:
            break
        page += 1 
        if len(events_list) > max_count:
            break
    print('SUCCESS | Pulled all events through Discovery API. Total Events: {}'.format(len(events_list)))
    return events_list

def getPriceJsonList(eventJson):
    # DESCRIPTION: Get price range list of price-info jsons from a given event json
    priceRanges_json_list = eventJson['priceRanges']
    return priceRanges_json_list

def getSalesJson(eventJson, kind = None):
    # DESCRIPTION: Get on-sale information for the given event json, including presale information
	# kind: if 'presales', return only presale. If 'public', return only public sales
    sale_json = eventJson['sales']
    if kind == 'presales':
        sale_json = sale_json['presales']
    elif kind == 'public':
        sale_json = sale_json['public']
    return sale_json

def getDateJson(eventJson):
    # DESCRIPTION: Get event date information given an event json
    date_json = eventJson['dates']
    return date_json

def notifyByEmail(to_address = 'notify.brandon.flannery@gmail.com', subject = 'None', msg = 'None'):
    # Login to notify.brandon.flannery, send email to to_address with subject and msg
    full_message = 'Subject: %s\n\n%s' % (subject, msg)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login('notify.brandon.flannery','pluribus')
    server.sendmail('notify.brandon.flannery@gmail.com', to_address, full_message)
    server.quit()
    return  

def pretty(d, indent=0):
    # Return a pretty dictionary/json (d) string
    final_string = ''
    for key, value in d.items():
        final_string += '\n' + ('\t' * indent + str(key))
        if isinstance(value, dict):
            final_string += '\n' + pretty(value, indent+1)
        else:
            final_string += '\n' + ( '\t' * (indent+1) + str(value.encode('utf-8')))
    final_string = ('\t' * (indent) + '{') + final_string + ('\n' + ('\t' * (indent)) + '}') # Format like json
    return final_string

def emailPresaleInfo(event_list, address_list):
    # For all evnent-jsons in event_list, email all presale information to each address in 
    # address_list
    full_presale_info_string = ''
    for event in event_list:
        url = event['url'].encode('utf-8')
        name = event['name'].encode('utf-8')
        try:
            date_json = getDateJson(event)
            date = date_json['start']['dateTime'].encode('utf-8')
        except:
            date = 'None'
        venue = event['_embedded']['venues'][0]
        venue_string = ", ".join([venue['name'], venue['city']['name'], venue['state']['stateCode']]).encode('utf-8')
        event_header_string = "\n".join([name,date,venue_string,url])
        try:
            presales_json = getSalesJson(event, 'presales')
            pretty_sales = '\n'.join([pretty(x, 1) for x in presales_json]).decode('utf-8')
            presale_info_string = "\n===\n".join([event_header_string, pretty_sales])
            full_presale_info_string += '\n============\n' + presale_info_string.encode('utf-8')
        except Exception, e:
            print('ERROR | Could not extract presale info for --> {}'.format(','.join([name,url])))
            continue
    subject = 'Presale Notifications: {}'.format(time())
    msg = '======================\n==>PRESALE INFO\n==>{}\n==>Total Observations: {}\n======================\n{}'.format(time(), len(event_list), full_presale_info_string)
    for address in address_list:
        notifyByEmail(address, subject, msg)
    print('SUCCESS | Sent Presale Email to {} at {}'.format(address_list, time()))
    return
        

        




if __name__ == '__main__':
    full_presale_info_string = ''
    event_list = getEvents()
    '''
    for event in events_list:
        print '-' * 50
        print('EVENT | {}: {}'.format(event['name'], event['url']))
        priceJson_list = getPriceJsonList(event)
        print('PRICE | {}'.format(priceJson_list))
        sales_json = getSalesJson(event, 'presales')
        print('SALE | {}'.format(sales_json))
        date_json = getDateJson(event)
        print('DATE | {}'.format(date_json))
        pretty_sales = '\n'.join([pretty(x, 1) for x in sales_json]).decode('utf-8')
        event_header = "--".join([event['name'], event['url']])
        presale_info_string = "\n===\n".join([event_header, pretty_sales])
        full_presale_info_string += '\n============\n' + presale_info_string.encode('utf-8')
    '''
    address_list = ['brandonjflannery@gmail.com', 'jaredbaker5@gmail.com']
    emailPresaleInfo(event_list, address_list)    




