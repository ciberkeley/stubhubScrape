import pandas as pd
import numpy as np
import requests


# XHR Scraping Instructions: http://toddhayton.com/2015/03/11/scraping-ajax-pages-with-python/

sample_request_url = 'https://www.stubhub.com/shape/search/inventory/v2/listings/?eventId=9812122&sectionStats=true&zoneStats=true&start=0&allSectionZoneStats=true&eventLevelStats=true&quantitySummary=true&rows=20&sort=price+asc,value+desc&priceType=nonBundledPrice&valuePercentage=true&tld=1'

# 1) Construct the searchRequestJson dictionary.
searchRequestJson = {}

# 2) Initialize searchRequestJson['pageNumber'] to 0
searchRequestJson['pageNumber'] = 0

# 3) Convert the searchRequestJson dict into a JSON string

# 4) Send a POST request


r = requests.post(
    url=sample_request_url,
    #data=payload,
    headers={'X-Requested-With': 'XMLHttpRequest'}
    )

print r.text
