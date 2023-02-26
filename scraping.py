# -*- coding: utf-8 -*-
"""Scraping.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PKMBLI0LqPwZ5Nn98nNgm-NypBkAqmd9

https://dubai.dubizzle.com/en/property-for-sale/residential/villahouse/?filters=(bedrooms%3E%3D3%20AND%20bedrooms%3C%3D3)%20AND%20(neighborhoods.ids%3D62057)

\https://dubailand.gov.ae/en/open-data/real-estate-data/#/
"""

import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import re

def get_url(buy_rent: str, location: str, page: int = 1) -> str:
    url_dict = {'buy':'for-sale', 'rent': 'to-rent', 'spr':'the-springs','lakes': 'the-lakes', 'mdw': 'the-meadows', 'ji': 'jumeirah-islands', 
                'jp': 'jumeirah-park', 'eh': 'emirates-hills', 'acacia': 'al-sufouh/al-sufouh-1/acacia-avenues'}
    url = f"https://www.bayut.com/{url_dict[buy_rent]}/property/dubai/{url_dict[location]}/"
    if page == 1:
        return url
    else:
        return f"{url}page-{page}/"


def get_res_text(url: str) -> str:
    print(f"Making request to {url}")
    res = requests.get(url)
    assert res.status_code == 200
    return res.text

def get_type(desc):
    type =  re.search(r'\bType\s(\d\w?)\b', desc)
    if type is not None:
        return type.group(0)


def get_details(html: str) -> dict:
    soup = BeautifulSoup(html)

    basic_info = soup.find(attrs={'aria-label': 'Property basic info'})
    property_details = soup.find(attrs={'aria-label': 'Property details'})
    side_bar = soup.find(attrs={'aria-label': 'Side bar'})

    beds = basic_info.find(attrs={'aria-label': 'Beds'})
    if beds is not None:
        beds = beds.span.string.split()[0]     #replace(' Beds', '')

    baths = basic_info.find(attrs={'aria-label': 'Baths'})
    if baths:
        baths = baths.span.string.split()[0]     #replace(' Baths', '')

    # avg_rent = property_details.find(attrs={'aria-label': 'Average Rent'})
    # if avg_rent is not None:
    #     # avg_rent = int(avg_rent.span.string.replace(',', ''))
    #     print(avg_rent.text)
    #     avg_rent = avg_rent.text

    plot = soup.find(attrs={'aria-label': 'Plot Area'})
    # print("~~~", plot)
    if plot is not None:
        plot = plot.span.string  #.replace(' sqft', '').replace(',', '')

    agency = side_bar.find(attrs={'aria-label': 'Agency name'})
    if agency is not None:
        agency = agency.string

    # broker = soup.find(attrs={'aria-label': 'Agency photo'})
    # if broker is not None:
    #     broker = broker.attrs['alt']

    agent = soup.find(attrs = {'aria-label' : 'Agent name'})
    agent_name = agent.string
        
    trucheck_badge = soup.find(attrs={'aria-label': 'Property Verified Button'})
    is_trucheck = trucheck_badge is not None
    is_checked = soup.find(attrs={'aria-label': 'Property Verification Eligible Button'}) is not None
    check_date = None
    if is_trucheck:
        badge = "TruCheck"
        check_date = trucheck_badge.find('span').contents[0].lstrip("on ")
    elif is_checked:
        badge = "Checked"
    else:
        badge = "None"  

    posted = soup.find(attrs={'aria-label': 'Reactivated date'})
    if posted is not None:
        posted = posted.string

    desc = soup.find(attrs={'aria-label': 'Property description'}).get_text()
    prop_type = get_type(desc)

    return {
        'price': int(basic_info.find(attrs={'aria-label': 'Price'}).string.replace(',', '')),
        'header': basic_info.find(attrs={'aria-label': 'Property header'}).string,
        # 'beds': basic_info.find(attrs={'aria-label': 'Beds'}).span.string.split()[0],   #replace(' Beds', '')),
        'bu_area': int(basic_info.find(attrs={'aria-label': 'Area'}).span.span.string.replace(' sqft', '').replace(',', '')),
        'desc': desc,
        'prop_type': prop_type,
        'beds' : beds,
        'baths': baths,
        'agency': agency,
        'agent_name' : agent_name,
        'badge': badge,
        'posted' : posted,
        'plot' : plot,
        # 'avg_rent' : avg_rent
        # 'avg_rent': int(basic_info.find(attrs={'aria-label': 'Average Rent'}).span.span.string.replace(' sqft', '').replace(',', '')),


    }

def get_single_page(html: str) -> list:
    soup = BeautifulSoup(html, features="html.parser")
    ul = soup.find("ul", class_="_357a9937")
    lis = ul.find_all('li')
    listings = []
    
    for li in lis:
        anchor = li.find("a")
        if anchor is None:
          continue
        href = anchor["href"]
        url = f"https://www.bayut.com{href}"
        html = get_res_text(url)
        time.sleep(0.5)
        details = get_details(html)
        listings.append((details['header'], details['price'], details['beds'], details['baths'], details['bu_area'], details['prop_type'],
                         details['plot'], details['agency'], details['agent_name'], details['desc'], details['badge'], details['posted'] ))

    return listings

page_no = 1
all_listings = []
while True:
    url = get_url("buy", "acacia", page_no)
    html = get_res_text(url)
    # time.sleep(0.5)
    listings = get_single_page(html)
    print(len(listings))
    all_listings.extend(listings)
    if len(listings) < 24:
      break
    page_no += 1
print(len(all_listings))

frame = pd.DataFrame(all_listings, columns = ['Title', 'Prop Type', 'Price', 'Beds', 'Baths', 'Built up', 'Plot size',  
                                              'Desc', 'Badge', 'Posted',  'Agency', 'Agent Name'])
frame = frame.fillna(0)
frame = frame.astype({
    'Title': str,
    'Prop Type' : str,
    'Price': int,
    'Beds': str,
    'Baths': str,
    'Built up': str,
    'Plot size' : str,
    'Agency': str,
    'Desc': str,
    'Badge': str,
    'Posted' : str,
    # 'avg_rent': str,
    'Agent Name': str
})
frame[frame['Price'] == frame['Price'].min()]
frame.to_excel('acacia.xlsx', index=False)

# from google.colab import drive
# drive.mount('/content/drive')
# path = '/content/drive/My Drive/springs.xlsx'
# with open(path, 'wb') as f:  
#     frame.to_excel(f)

# print(frame)

# r = requests.get('https://www.bayut.com/property/details-6624039.html')
# r
# html = r.text
# soup = BeautifulSoup(html, 'lxml')
# # print(soup.prettify())
# x = soup.span.find(attrs= {'area-label': 'Plot Area'}).text
# print(x)



