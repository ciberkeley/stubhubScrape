import pandas as pd
import numpy as np
import requests
import re, smtplib, datetime
time = datetime.datetime.now
import time as time1

discovery_root_url = 'https://app.ticketmaster.com/discovery/v2/'

def getEvents(max_count = 1000, api_param_dict = {}):
    # DESCRIPTION: Get All Event Jsons. Return a list of event jsons
    # num: max number of events to pull
    page = 0
    events_list = []
    base_request_url = 'https://app.ticketmaster.com/discovery/v2/events.json?size=100&{}&apikey=qDPfiZcjOMUmxf8zoUbGvUFJkGqKTkx9'
    argument_format_string = "&".join([x+'='+api_param_dict[x] for x in api_param_dict.keys()])
    while True: # Get 20 events at a time until there are no more events left to gather
        page_format_string = 'page={}'.format(page)
        temp_format_string = '&'.join([argument_format_string, page_format_string])
        all_events_request = base_request_url.format(temp_format_string)
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

def getSalesJson(eventJson, kind = None, active = False):
    # DESCRIPTION: Get on-sale information for the given event json, including presale information
	# kind: if 'presales', return only presale. If 'public', return only public sales
    # Note: The active argument only works on presales
    # Note: if kind = 'presales' and active = True, the returned json will only have active presales
    #       and presales going active in < 2 days
    sale_json = eventJson['sales']
    if kind == 'presales':
        sale_json_list = sale_json['presales']
        if active == True: # Filter for active presales
            curr_date = time()
            active_json_list = []
            for item in sale_json_list: # Remove inactive list items
                start_date = pd.to_datetime(item[u'startDateTime'])
                end_date = pd.to_datetime(item[u'endDateTime'])
                start_date2 = pd.to_datetime(item[u'startDateTime']) - datetime.timedelta(2)
                if (curr_date > start_date2) and (curr_date < end_date): # Remove presale
                    active_json_list.append(item)
            return active_json_list
        else:
            return sale_json_list
    elif kind == 'public':
        sale_json_list = sale_json['public']
        return sale_json_list
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
        final_string += '\n' + ('\t' * indent + "{}:{}{}".format(str(key), '\t', str(value)))
    return final_string

def emailPresaleInfo(event_list, address_list, notification_id):
    # For all evnent-jsons in event_list, email all presale information to each address in 
    # address_list
    # Note: This method will only pull active presales and has a filter to only report active presales
    #       and presales going active in under 2 days
    full_presale_info_string = ''
    success_count = 0
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
        try: # Get active presales and format the email
            presales_json = getSalesJson(event, 'presales', active = True) # Get active presales
            if sum(['presale' not in str(x['name']).lower() for x in presales_json]) == len(presales_json):
                raise Exception('No presale-specific items found.')
            if len(presales_json) == 0: # No active presales for this event
                continue
            pretty_sales = '\n'.join([pretty(x, 1) for x in presales_json]).decode('utf-8')
            presale_info_string = "\n===\n".join([event_header_string, pretty_sales])
            full_presale_info_string += '\n============\n' + presale_info_string.encode('utf-8')
            success_count += 1
        except Exception, e:
            # Note: most of these errors are because the event is listed on ticketsnow.com, ticketweb.com
            #       or livenation.com.... needs to be fixed
            print('ERROR | Could not extract presale info for --> {}. Exception: {}'.format(','.join([name,url]), e))
            continue
    subject = '{} | Presale Notifications: {}'.format(notification_id, time())
    msg = '======================\n==>PRESALE INFO\n==>{}\n==>Successful Observations: {}/{}\n======================\n{}'.format(time(), success_count, len(event_list), full_presale_info_string)
    for address in address_list:
        notifyByEmail(address, subject, msg)
    print('SUCCESS | Sent Presale Email to {} at {}'.format(address_list, time()))
    return
        

        




if __name__ == '__main__':
    full_presale_info_string = ''
    latlong_sf = ','.join(['37.867197', '-122.249933'])
    latlong_ny = ','.join(['40.751815', '-73.988595'])
    latlong_la = ','.join(['34.047945', '-118.253294'])
    #event_list = getEvents(api_param_dict={'countryCode': 'US', 'stateCode': 'CA'}) #California events
    event_list_sf = getEvents(api_param_dict={'latlong': latlong_sf, 'radius': '50', 'unit': 'miles'})
    event_list_ny = getEvents(api_param_dict={'latlong': latlong_ny, 'radius': '20', 'unit': 'miles'})
    event_list_la = getEvents(api_param_dict={'latlong': latlong_la, 'radius': '50', 'unit': 'miles'})
    '''
    for event in event_list[:2]:
        print '-' * 50
        print('EVENT | {}: {}'.format(event['name'], event['url']))
        priceJson_list = getPriceJsonList(event)
        print('PRICE | {}'.format(priceJson_list))
        sales_json_list = getSalesJson(event, 'presales', active = True)
        print('SALE | {}'.format(sales_json_list))
        date_json = getDateJson(event)
        print('DATE | {}'.format(date_json))
    '''
    address_list = ['brandonjflannery@gmail.com', 'jaredbaker5@gmail.com']
    while True: # infinite loop
        emailPresaleInfo(event_list_sf, address_list, notification_id = 'San Francisco')    
        emailPresaleInfo(event_list_ny, address_list, notification_id = 'New York')
        emailPresaleInfo(event_list_la, address_list, notification_id = 'Los Angeles')
        time1.sleep((60 * 60 * 24) - 120) # Sleep for 24 hours




