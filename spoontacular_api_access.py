from bs4 import BeautifulSoup
import json
import unittest
import re
import os
import requests
import sqlite3
from yelpapi import YelpAPI

# Spoontacular API_KEY = "8cf1b23a038a4372835238e67ffd74ab"

# Yelp
# client_ID = "rkuo0PKmfif1pdFsWx3U1Q"
API_KEY = "hKxIMdkKPpO81Uq7XqdeG7OB8Eq0TBDhVijsuWbkFguL8W-aR_c9gq3sWXZhZe1p5QEB-cLoRuimq-iW9yukU_KJsXtDC9NoSEkhALOgnTQibKi-3X2PJlRxABXLX3Yx"


#scrape number of restaurants that have key word "healthy", return a dictionary ex {'New York':100}
def scrape_healthy_restaurants():
    city_list = scrape_100_top_cities()
    yelp_api = YelpAPI(API_KEY)
    healthy_restuarants_dict = {}

    #get restaurants with key word "healthy in each city
    for city in city_list:
        search_results = yelp_api.search_query(term = 'healthy', location = city)
        healthy_restuarants_dict[city] = search_results["total"]
    
    return(healthy_restuarants_dict)


# WEBSCRAPING
def scrape_100_top_cities():
    url = "https://worldpopulationreview.com/us-cities"
    r = requests.get(url)
    
    soup = BeautifulSoup(r.content, 'html.parser')

    city_list = []

    # gets content of table which contains all over 100 most populace US cities
    table_body = soup.find('tbody', class_='jsx-2642336383')
    
    # gets only top 100 city names
    for element in table_body.find_all('tr'):
        if int(str(element.td.text)) <= 100:
            city_list.append(element.td.find_next_sibling('td').a.text)

    return city_list

# YELP API
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

"""
def get_data_with_caching(url, CACHE_FNAME):

    cache_dict = read_cache(CACHE_FNAME)

    if url in cache_dict:
        print("Using cache for " + title)
        return cache_dict[url]
    else:
        print("Fetching data for " + title)
        try:
            r = requests.get(url)
            info = json.loads(r.text)
            if info["Response"] == 'True':
                cache_dict[url] = info
                write_cache(CACHE_FNAME, cache_dict)
            else:
                print("Movie not found!")
                return None
        except:
            print("Exception")
            return None 
"""

def city_urls():
    cities = scrape_100_top_cities()
    url_list = []

    for i in range(len(cities)):
        parms = "healthy&location=" + cities[i]
        url = "https://api.yelp.com/v3/businesses/search?term=" + parms
        url_list.append(url)

    
    for url in url_list:
        r = requests.get(url)
        print(r.content)
    

    return 1



# DATABASE
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpCitiesTable(cur, conn):
    cities = scrape_100_top_cities()

    cur.execute("DROP TABLE IF EXISTS Cities")
    cur.execute("CREATE TABLE Cities (id INTEGER PRIMARY KEY, Name TEXT)")

    for i in range(len(cities)):
        cur.execute("INSERT INTO Cities (id, Name) VALUES (?, ?)", (i, cities[i]))
    conn.commit()
    
#set up food table
#cities id can be the shared key
def setUpRestaurantsTable(cur, conn):
    restaurants = scrape_healthy_restaurants()

    cur.execute("DROP TABLE IF EXISTS Restaurant")
    cur.execute("CREATE TABLE Restaurant (id INTEGER PRIMARY KEY, cities_id INTEGER, num_of_healthy_place INTEGER")

    for i in range(len(restaurants))):
        cur.execute("INSERT INTO Restaurant (id, cities_id, num_of_healthy_place ) VALUES (?, ?, ?)", (i, cities[i]))
    conn.commit()
    pass
    

def main():
    cur, conn = setUpDatabase('cities.db')
    setUpCitiesTable(cur, conn)
    print(scrape_healthy_restaurants())
    conn.close()

class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'cities.db')
        self.cur = self.conn.cursor()

    def test_cities_table(self):
        self.cur.execute('SELECT * FROM Cities')
        cities_list = self.cur.fetchall()
        self.assertEqual(len(cities_list), 100)
        self.assertEqual(len(cities_list[0]), 2)

if __name__ == '__main__':
    # print(scrape_100_top_cities())
    print(city_urls())
    main()
    #unittest.main(verbosity = 2)
