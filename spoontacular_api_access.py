from bs4 import BeautifulSoup
import json
import unittest
import re
import os
import requests
import sqlite3
from yelpapi import YelpAPI

# Yelp
# client_ID = "rkuo0PKmfif1pdFsWx3U1Q"
API_KEY = "hKxIMdkKPpO81Uq7XqdeG7OB8Eq0TBDhVijsuWbkFguL8W-aR_c9gq3sWXZhZe1p5QEB-cLoRuimq-iW9yukU_KJsXtDC9NoSEkhALOgnTQibKi-3X2PJlRxABXLX3Yx"

# YELP API
#scrape number of restaurants that have key word "healthy", return a dictionary ex {'New York':100}
def scrape_healthy_restaurants():
    city_list = []
    for tup in top_cities_data():
        city_list.append(tup[0])

    yelp_api = YelpAPI(API_KEY)
    healthy_restuarants_dict = {}

    #get restaurants with key word "healthy in each city
    for city in city_list:
        search_results = yelp_api.search_query(term = 'healthy', location = city)
        healthy_restuarants_dict[city] = search_results["total"]
    
    return(healthy_restuarants_dict)


# WEBSCRAPING

# NEW POTENTIAL PLAN: Scrape from 100 top cities website with more info and then compare with that
# potential variables: city budget, party type of mayor, population density, population change, area
def top_cities_data():
    url = "https://worldpopulationreview.com/us-cities"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    table_body = soup.find('tbody', class_='jsx-2642336383')

    data_tup_list = []
    for element in table_body.find_all('tr'):
        if int(str(element.td.text)) <= 100:
            city = element.td.find_next_sibling('td').text
            state = element.td.find_next_sibling('td').find_next_sibling('td').a.text
            pop = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text
            pop_change = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').span.text
            density = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text
            area = element.td.find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').find_next_sibling('td').text
            data_tup_list.append((city, state, pop, pop_change, density, area))

    return data_tup_list


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
    cur.execute("SELECT * FROM Cities")
    cities_list = cur.fetchall()
    print(cities_list)
    

    cur.execute("DROP TABLE IF EXISTS Restaurants")
    cur.execute("CREATE TABLE Restaurants (id INTEGER PRIMARY KEY, cities_id INTEGER, num_of_healthy_place INTEGER)")

    for i in range(len(restaurants)):
        cur.execute("INSERT INTO Restaurants (id, cities_id, num_of_healthy_place) VALUES (?, ?, ?)", (i, cities_list[i][0], restaurants[cities_list[i][1]]))
    conn.commit()
    

def main():
    cur, conn = setUpDatabase('cities.db')
    setUpCitiesTable(cur, conn)
    setUpRestaurantsTable(cur, conn)
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
    def test_restuarants_table(self):
        self.cur.execute('SELECT num_of_healthy_place FROM Restaurants')
        restaurants_list = self.cur.fetchall()
        self.assertEqual(len(restaurants_list), 100)

if __name__ == '__main__':
    # print(scrape_100_top_cities())
    # print(city_urls())
    #print(arcgis_info())
    main()
    #unittest.main(verbosity = 2)
