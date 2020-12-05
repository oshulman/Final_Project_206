from bs4 import BeautifulSoup
import json
import unittest
import re
import os
import requests

# Spoontacular API_KEY = "8cf1b23a038a4372835238e67ffd74ab"

# Yelp
# client_ID = "rkuo0PKmfif1pdFsWx3U1Q"
API_KEY = "hKxIMdkKPpO81Uq7XqdeG7OB8Eq0TBDhVijsuWbkFguL8W-aR_c9gq3sWXZhZe1p5QEB-cLoRuimq-iW9yukU_KJsXtDC9NoSEkhALOgnTQibKi-3X2PJlRxABXLX3Yx"

def scrape_100_top_cities():
    url = "https://worldpopulationreview.com/us-cities"
    r = requests.get(url)
    
    soup = BeautifulSoup(r.content, 'html.parser')

    city_list = []

    # gets content of table which contains all over 100 most populace US cities
    table_body = soup.find('tbody', class_='jsx-2642336383')
    
    # gets all the city names
    for element in table_body.find_all('tr'):
        if int(str(element.td.text)) <= 100:
            city_list.append(element.td.find_next_sibling('td').a.text)

    #list_100_cities = []

    # gets just top 100
    #for i in range(100):
     #   list_100_cities.append(city_list[i])

    #return list_100_cities
    return city_list


def read_cache(CACHE_FNAME):
    """
    This function reads from the JSON cache file and returns a dictionary from the cache data.
    If the file doesn’t exist, it returns an empty dictionary.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_movie.json"
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
        cache_contents = cache_file.read()  # If it's there, get it into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
        cache_file.close() # Close the file, we're good, we got the data in a dictionary.
        return CACHE_DICTION
    except:
        CACHE_DICTION = {}
        return CACHE_DICTION

def write_cache(cache_file, cache_dict):
    """
    This function encodes the cache dictionary (CACHE_DICT) into JSON format and
    writes the JSON to the cache file (CACHE_FNAME) to save the search results.
    """
    with open(cache_file, 'w') as outfile:
        json.dump(cache_dict, outfile)
    
    outfile.close()

def create_request_url():
    "https://api.yelp.com/v3"


def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

if __name__ == '__main__':
    print(scrape_100_top_cities())